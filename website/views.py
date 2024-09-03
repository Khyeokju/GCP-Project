from . import db
from flask import Blueprint, request, flash, redirect, url_for, render_template, jsonify, Response, send_from_directory
import requests, json   
from flask_login import login_required

from .models import Employee, Video

from tensorflow.keras.models import load_model
from ultralytics import YOLO
from google.cloud import storage
import cv2, mediapipe as mp, supervision as sv

import os, threading, queue, time, datetime, math, numpy as np

views = Blueprint('views', __name__)

cap = cv2.VideoCapture(0)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

model = load_model('realrealfinal_model.h5')
class_names = ['Normal', 'Bending', 'Sitting', 'Fall Down']

model2 = YOLO('reallasthelmet.pt')
class_names2 = ['no-helmet', 'helmet']

status = 'Processing'
has_helmet = 'Processing'
frame_queue = queue.Queue(maxsize = 1)

BUCKET_NAME = 'cctv_image'

def upload_to_gcs(image_bytes, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f'captures/{filename}')
    
    # 메모리에서 GCS로 직접 업로드
    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    
    # make_public() 제거 - 대신 public URL을 구성하여 반환
    # 공개 URL 구성 (버킷이 공개적으로 설정된 경우에만 접근 가능)
    return f"https://storage.googleapis.com/{BUCKET_NAME}/captures/{filename}"

def proc_frames():
    global status, has_helmet

    frame_count = 0
    predict_interval = 5
    predict_interval2 = 60

    fall_down_start = None
    fall_down_has_saved = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        draw_frame = frame.copy()
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(draw_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            if frame_count % predict_interval == 0:
                landmarks = np.array([[lmk.x, lmk.y, lmk.z] for lmk in results.pose_landmarks.landmark]).flatten()
                sequence = np.array([landmarks] * 20).reshape(1, 20, -1)
                
                if sequence.shape[1] != 30:
                    padded_sequence = np.zeros((1, 30, 99))  # 99개의 특징을 가진 30 타임스텝 시퀀스로 0으로 초기화
                    padded_sequence[:, :sequence.shape[1], :] = sequence  # 기존 시퀀스를 앞 부분에 삽입
                    sequence = padded_sequence
             
                prediction = model.predict(sequence)
                predicted_class = class_names[np.argmax(prediction)]
                
                prediction_prob = np.max(prediction)
                status = predicted_class

            if frame_count % predict_interval2 == 0:
                results2 = model2(frame, agnostic_nms = True)[0]
                prediction2 = sv.Detections.from_yolov8(results2)

                for _, confidence, class_id, _ in prediction2:
                    if confidence > 0.4:
                        has_helmet = class_names2[class_id]
                    else:
                        has_helmet = 'Processing'
            
            # /cv2.putText(draw_frame, f'{predicted_class} ({prediction_prob:.2f})', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            
            frame_count += 1

        else:
            frame_count = 0
            status = 'Processing'
            has_helmet = 'Processing'

        if status == 'Fall Down':
            if fall_down_start is None:
                fall_down_start = time.time()
            elif (time.time() - fall_down_start) > 7:
                if not fall_down_has_saved:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

                    mosaic_frame = frame.copy()

                    h, w, _ = mosaic_frame.shape
                    if results.pose_landmarks:
                        pose_landmarks = results.pose_landmarks
                        try:
                            nose = pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
                            left_eye = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE]
                            right_eye = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]

                            eye_dist = math.sqrt(
                                ((left_eye.x - nose.x) ** 2 * w ** 2) + 
                                ((left_eye.y - nose.y) ** 2 * h ** 2)
                            )

                            mosaic_size = int(eye_dist * 2)

                            for eye in [left_eye, right_eye]:
                                ex, ey = int(eye.x * w) - mosaic_size // 2, int(eye.y * h) - mosaic_size // 2

                                if ex < 0 or ey < 0 or ex + mosaic_size > w or ey + mosaic_size > h: continue

                                sub_img = mosaic_frame[ey : ey + mosaic_size, ex : ex + mosaic_size]
                                if sub_img.size == 0: continue

                                sub_img = cv2.resize(sub_img, (5, 5))
                                mosaic_frame[ey : ey + mosaic_size, ex : ex + mosaic_size] = cv2.resize(sub_img, (mosaic_size, mosaic_size), interpolation = cv2.INTER_NEAREST)

                        except IndexError:
                            pass

                    success, img_encoded = cv2.imencode('.jpg', mosaic_frame)
                    if not success:
                        print("Failed to encode image")
                        continue

                    image_bytes = img_encoded.tobytes()
                    public_url = upload_to_gcs(image_bytes, f'{timestamp}.jpg')
                    
                    data = {
                        'filename': f'{timestamp}.jpg',
                        'filepath': public_url
                    }
                    
                    domain = '127.0.0.1'
                    port = 5000
                    url = f'http://{domain}:{port}/save_video'

                    try:
                        response = requests.post(url, json=data)
                        if response.status_code == 200:
                            print(f"Saved {timestamp}.jpg to database via POST request.")
                        else:
                            print(f"Failed to save {timestamp}.jpg to database: {response.text}")
                    except requests.RequestException as e:
                        print(f"Failed to send POST request: {str(e)}")
                    
                    fall_down_has_saved = True
        else:
            fall_down_start = None
            fall_down_has_saved = False

        if not frame_queue.full():
            frame_queue.put(draw_frame)
            
@views.route('/send_kakao_alert', methods=['POST'])
def send_kakao_alert():
    data = request.get_json()
    message_content = data.get('message', '긴급 알림이 도착했습니다.')
    image_url = data.get('image_url', '')  # GCS 이미지 URL
    print(f"Message content: {message_content}, Image URL: {image_url}")

    try:
        with open("kakao/kakao_token.json", 'r') as file:
            tokens = json.load(file)

        print(f"Tokens loaded: {tokens}")

        friend_url = 'https://kapi.kakao.com/v1/api/talk/friends'
        headers = {
            'Authorization': 'Bearer ' + tokens['access_token']
        }

        result = json.loads(requests.get(friend_url, headers=headers).text)
        print(f"Kakao friends API result: {result}")

        if 'elements' not in result or not result['elements']:
            return jsonify({'error': 'No friends found or token is invalid'}), 400

        friend_id = result['elements'][0]['uuid']
        print(f"Friend ID: {friend_id}")

        send_url = 'https://kapi.kakao.com/v1/api/talk/friends/message/default/send'
        data = {
            'receiver_uuids': json.dumps([friend_id]),
            'template_object': json.dumps({
                'object_type': 'feed',
                'content': {
                    'title': '비정상 행동 감지!',
                    'description': message_content,
                    'image_url': image_url,
                    'link': {
                        'web_url': image_url,
                        'mobile_web_url': image_url
                    }
                },
                'buttons': [
                    {
                        'title': '자세히 보기',
                        'link': {
                            'web_url': image_url,
                            'mobile_web_url': image_url
                        }
                    }
                ]
            })
        }

        response = requests.post(send_url, headers=headers, data=data)
        print(f"Kakao API response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            return jsonify({'message': 'Kakao alert sent successfully'}), 200
        return jsonify({'error': 'Failed to send Kakao alert'}), response.status_code
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

    
def gen_frames():
    while True:    
        if not frame_queue.empty():
            frame = frame_queue.get()

            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret: break

            buffer_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer_bytes + b'\r\n')
        else:
            time.sleep(0.01)

threading.Thread(target = proc_frames, daemon = True).start()

@views.route('/save_video', methods=['POST'])
def save_video():
    data = request.get_json()
    filename = data.get('filename')
    filepath = data.get('filepath')

    if not filename or not filepath:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        # Save to database
        video = Video(filename=filename, filepath=filepath)
        db.session.add(video)
        db.session.commit()
        return jsonify({'message': 'Video saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@views.route('/status')
def get_status():
    global status, has_helmet

    latest_image_url = ''  # 기본값으로 초기화

    # 가장 최근의 이미지 URL을 반환
    videos = Video.query.all()  # DB에서 모든 동영상을 가져옴

    if videos:
        latest_image_url = videos[-1].filepath  # 가장 최근 파일 URL을 사용

    return jsonify({'status': status, 'has_helmet': has_helmet, 'image_url': latest_image_url})

@views.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route('/')
@login_required
def home():
    return render_template('home.html')

@views.route('/menual')
def menual():
    return render_template('menual.html')

@views.route('/safe')
def safe():
    return render_template('safe.html')

@views.route('/employ_list', methods = ['GET', 'POST'])
def employ_list():
    if request.method == 'POST':
        position = request.form.get('position')
        name = request.form.get('name')
        phone = request.form.get('phone')

        new_employee = Employee(
            position = position,
            name = name,
            phone = phone
        )

        db.session.add(new_employee)
        db.session.commit()

        flash('직원이 성공적으로 등록되었습니다.', category = 'success')

        return redirect(url_for('views.employ_list'))
    
    employees = Employee.query.all()
    return render_template('employ_list.html', employees = employees)

@views.route('/employ_update/<int:id>', methods = ['GET', 'POST'])
def employ_update(id):
    employee = Employee.query.get(id)

    if request.method == 'POST':
        employee.position = request.form.get('position')
        employee.name = request.form.get('name')
        employee.phone = request.form.get('phone')

        db.session.commit()
        flash('직원 정보가 성공적으로 수정되었습니다.', category = 'success')

        return redirect(url_for('views.employ_list'))

    return render_template('employ_update.html', employee = employee)

@views.route('/employ_delete/<int:id>', methods = ['POST'])
def employ_delete(id):
    employee = Employee.query.get(id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
        flash('직원이 성공적으로 삭제되었습니다.', category = 'success')
    else:
        flash('해당 직원이 존재하지 않습니다.', category = 'error')

    return redirect(url_for('views.employ_list'))

@views.route('/image_list')
def image_list():
    videos = Video.query.all()

    # 디버깅을 위한 파일 목록 출력
    print("Video Entries:", videos)
    
    images = []
    for video in videos:
        url = video.filepath
        base_name = os.path.splitext(video.filename)[0]
        try:
            # 파일 이름에서 날짜와 시간 추출 (형식: YYYYMMDD_HHMMSS)
            timestamp = datetime.datetime.strptime(base_name, '%Y%m%d_%H%M%S')
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            images.append({'filename': os.path.basename(url), 'timestamp': formatted_timestamp, 'url': url})
        except ValueError:
            # 날짜와 시간 포맷이 맞지 않는 파일은 무시
            print("Skipping file with invalid timestamp format:", url)
            continue
    
    # 디버깅을 위한 추출된 이미지 정보 출력
    print("Extracted Images:", images)
    
    # 날짜별로 그룹화
    grouped_images = {}
    for image in images:
        date = image['timestamp'].split(' ')[0]  # 날짜 부분만 추출
        if date not in grouped_images:
            grouped_images[date] = []
        grouped_images[date].append(image)

    # 디버깅을 위한 그룹화된 이미지 정보 출력
    print("Grouped Images:", grouped_images)
    
    return render_template('image_list.html', grouped_images=grouped_images)
    
@views.route('/show_image/<filename>')
def show_image(filename):
    # 여전히 URL을 반환한다고 가정
    url = f'https://storage.googleapis.com/cctv_image/captures/{filename}'
    print(f"Generated image URL: {url}")  # 디버깅용 로그
    return jsonify({'url': url})

@views.route('/delete_image', methods=['POST'])
def delete_image():
    data = request.get_json()
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': 'Invalid filename'}), 400
    
    try:
        # 데이터베이스에서 파일명을 기준으로 해당 행 삭제
        video = Video.query.filter_by(filename=filename).first()
        if video:
            db.session.delete(video)
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'File not found in database'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
