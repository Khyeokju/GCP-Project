# Google Cloud AI 인재 양성 프로젝트  


## Safepro+
>제주 4팀

> 개발기간: 2024.08.21 ~ 2024.08.27

원래 기간은 4주였지만 프로젝트 후반, 아이디어가 갈아 엎어지는 바람에 짧은 기간 내에 개발&배포.

## 배포
GCP vm instance로 서버를 열고 vscode로 ssh를 연결하여 배포하였지만 이젠 금액을 지원받지 못하므로. . . 중단

## 팀 소개
> 조장: 김도현 (제주대학교 인공지능학과)

> 조원: 권혁주 (제주대학교 전산통계학과) 외 제주대학교 3명

 - 내 역할
   - 앱 백&프론트&배포
 - 그 외
   - AI 모델 생성 / 자료조사 / PPT&발표 

## 프로젝트 소개 
**Safepro+ [노동자 안전관리 앱]**

1. 프로젝트 배경 & 기획 의도
   - 우리나라를 뜨겁게 달구는 중대재해처벌법에 포커싱을 두고 프로젝트를 시작함.

   - 50인 미만 사업장에서 중대재해처벌법을 확대 적용했으나 여전한 재해수치를 나타냄
   
   - why? 전문인력을 사용할 예산 부족 & 사업주나 기존 관리자가 겸임

   - 이 고착된 문제를 해결하고자 산업안전체제를 효율적으로 구축할 수 있는 프로젝트 기획

2. 프로젝트 간단한 소개

   - cctv를 앱에 연동하여 실시간으로 AI와 결합 + 관리자 안전 메뉴얼
     - 누구나 쉽게 전문가 수준의 안전관리와 효율적인 관리를 하도록 도와주는 앱

## 버전
파이썬 버전 3.10.11

## **기술스택**
  ### Environment
  <img src="https://img.shields.io/badge/Visual Studio Code-0769AD?style=for-the-badge&logo=Visual Studio Code&logoColor=white">

  ### Config
  <img src="https://img.shields.io/badge/npm-CB3837?style=for-the-badge&logo=npm&logoColor=white">

  ### Development
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <img src="https://img.shields.io/badge/sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">

  ### Model
  <img src="https://img.shields.io/badge/tensorflow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"> <img src="https://img.shields.io/badge/MediaPipe-4FC08D?style=for-the-badge&logo=MediaPipe&logoColor=white"> <img src="https://img.shields.io/badge/Yolo-003545?style=for-the-badge&logo=Yolo&logoColor=white">

## 주요 기능
   - AI를 적용한 cctv 메인 화면
   - 비정상 행동 감지 시 감지됐을 때의 사진을 포함한 화면 알림 & 카카오톡 알림 기능
   - 알림 시 긴급 신고 기능 & 관계자 연락 기능
   - 산업 안전 메뉴얼 체크 리스트
   - cctv 알림 이미지 모자이크 저장
   - 관련 법률 안내
     
## 프로젝트 아키텍처

![image](https://github.com/user-attachments/assets/42feca44-d70f-435a-857e-912d4dae45da)

## API 문서 (없음.. 다음부턴 만들면서 해보도록 하겠다.)

## 개발 리뷰
우리 팀에서는 내가 전체적인 앱 개발을 맡게 되었다. <br>하지만 그땐 나도 개발에 대해 아는 것이 없었던 상태였기 때문에 맨땅에 해딩을 해보기로 했다.
<br>처음엔 flask로 간단한 웹페이지를 설계하는 것도 어려워했던 나였다. 계속 구글링 하고.. gpt한테 물어보고.. 모든게 어렵게만 느껴졌다. <br>
결국 클론 코딩을 택했고, 이 코드 내에서 오류가 생기지 않고 뻗어나갈 수 있는 선에서 코드와 아이디어를 붙여갔다. <br>
한 사흘정도 복붙하고... 오류 고치고, 복붙하고.. 오류 고치고, 어찌저찌 내가 코드를 짰다고 하기도 부끄러운 첫 웹사이트를 만들었다. <br>
그리고 GCP를 통한 사이트 배포를 하루 밤새 붙잡다가 겨우 어떻게든 해냈었다. 내가 이때 어떻게 했는지도 기억이 안난다. <br>
열심히 만든 첫 웹사이트였지만, 강사님의 피드백을 받고 아이디어가 엎어진 바람에 처음부터 시작을 해야했다. 그래도 짧은 기간이었지만 사이트, 배포야 뭐 해봤으니 금방 하겠거니 했다.<br>
큰 착각이었다. 이해를 하지않고 그냥 코드를 따라친 탓에 다시 만드려고 하니 머리 속이 하얬다. 응용을 할 수 없었다. <br>
그때, 내가 개발을 이렇게 한다면 밑빠진 독에 물 붓기나 다름 없다는 것을 깨달았다. <br> 일주일이란 짧은 시간이었지만 최대한 코드를 이해하려고 노력하며
써나갔다. (AI 관련 함수는 조장분이 코딩해주셨다.) <br> 그랬더니 오류를 고쳐나가는 과정에서 이 코드가 무슨 동작을 하는지와 코드의 전체적인 구조를 이해하고 있었기에 빠른 수정이 가능했다. <br>
이해가 됐기에 수정이 빨랐고 그 덕과 아침부터 새벽을 빌려 코딩한 탓에 배포까지 성공 할 수 있었다. <br> 
<br> **프로젝트를 마치며** <br>
이번 프로젝트를 잘 만들었다고는 절대 말할 수 없지만, 이 프로젝트가 나를 비약적으로 성장시켜주었다. 단순 취미 코딩이 아닌 개발 영역으로써의 시야가 트이게 해주었다. <br>
프로젝트 전엔 대학교 전공강의들을 왜 배우는지, 어디에 쓰이는지 제대로 몰랐지만 다 알게 되었고, 일반적으로 하는 프로젝트는 어떻게 진행 되는 것인지에 대한 전체적인 개요, 개발자가 되기 위해 무엇을 해야하는지 깨달을 수 있던 시간이었다.



  







  
