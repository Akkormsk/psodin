from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from config import Config
from .. import User  # Импортируем класс User из __init__.py

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == Config.SECRET_ADMIN_PASSWORD:
            user = User()  # Инициализация User
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Неверный пароль')
    return render_template('login.html')


@auth_bp.route('/logout')
@auth_bp.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
