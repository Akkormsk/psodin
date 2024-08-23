from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import Config
from ..models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    password = request.form['password']
    if password == Config.SECRET_ADMIN_PASSWORD:
        session['authenticated'] = True  # Сохраняем состояние аутентификации в сессии
        return redirect(url_for('admin.index'))  # Перенаправляем в админку
    flash('Неверный пароль')
    return redirect(url_for('main.index'))


@auth_bp.route('/logout')
@auth_bp.route('/admin/logout')
def logout():
    session.pop('authenticated', None)  # Удаляем флаг аутентификации из сессии
    return redirect(url_for('main.index'))
