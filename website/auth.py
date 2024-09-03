from . import db
from flask import Blueprint, request, flash, redirect, url_for, render_template

from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/sign_in', methods = ['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        company_code = request.form.get('company_code')
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        user = User.query.filter_by(
            company_code = company_code, 
            user_id = user_id
        ).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('로그인 완료.', category = 'success')

                return redirect(url_for('views.home'))
            else:
                flash('비밀번호가 일치하지 않습니다.', category = 'error')
        else:
            flash('해당 회사 코드 또는 아이디가 존재하지 않습니다.', category = 'error')
        
    return render_template('sign_in.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.sign_in'))

@auth.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        company_code = request.form.get('company_code')
        user_id = request.form.get('user_id')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not company_code or not user_id or not password1 or not password2:
            flash('모든 필드를 입력해야 합니다.', category = 'error')
        elif len(company_code) < 3:
            flash('회사 코드는 3자 이상이어야 합니다.', category = 'error')
        elif User.query.filter_by(user_id = user_id).first():
            flash('이미 존재하는 아이디입니다.', category = 'error')
        elif password1 != password2:
            flash('비밀번호가 일치하지 않습니다.', category = 'error')
        elif len(user_id) < 4:
            flash('아이디는 4자 이상이어야 합니다.', category = 'error')
        elif len(password1) < 6:
            flash('비밀번호는 6자 이상이어야 합니다.', category = 'error')
        else:
            new_user = User(company_code = company_code, user_id = user_id, password = generate_password_hash(password1, method = 'pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember = True)
            flash('회원가입이 완료되었습니다.', category = 'success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')