from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import Config
from ..models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == Config.SECRET_ADMIN_PASSWORD:
            session['authenticated'] = True  # Устанавливаем флаг сессии
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Неверный пароль')
    return render_template('login.html')


@auth_bp.route('/logout')
@auth_bp.route('/admin/logout')
def logout():
    session.pop('authenticated', None)  # Удаляем флаг аутентификации из сессии
    return redirect(url_for('main.index'))
