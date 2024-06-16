from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

from models import *


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        return super(MyAdminIndexView, self).index()

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    column_display_pk = True  # Показывать первичный ключ

    # Отключаем отображение в меню
    def is_visible(self):
        return False


def create_admin(app):
    admin = Admin(app, name="PS#1 admin", index_view=MyAdminIndexView(name='Главная'), template_mode='bootstrap4')
    admin.add_view(CustomModelView(PaperType, db.session, name='Бумага', endpoint='papertype'))
    admin.add_view(CustomModelView(PrintType, db.session, name='Печать', endpoint='printtype'))
    admin.add_view(CustomModelView(PostPrintProcessing, db.session, name='Постпечатка',
                                   endpoint='postprintprocessing'))
    admin.add_view(CustomModelView(Embossing, db.session, name='Тиснение', endpoint='embossing'))
    admin.add_view(CustomModelView(Variables, db.session, name='Переменные', endpoint='variables'))
    admin.add_view(CustomModelView(PaperTypeLarge, db.session, name='Бумага шир', endpoint='papertypelarge'))
    admin.add_view(CustomModelView(PrintTypeLarge, db.session, name='Печать шир', endpoint='printtypelarge'))
    admin.add_view(CustomModelView(PostPrintProcessingLarge, db.session, name='Постпечатка шир',
                                   endpoint='postprintprocessinglarge'))
    return admin
