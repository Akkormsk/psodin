from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

from models import db, PaperType, PrintType, PostPrintProcessing


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
    # Отключаем отображение в меню
    def is_visible(self):
        return False


def create_admin(app):
    admin = Admin(app, name="PS#1 admin", index_view=MyAdminIndexView(name='Главная'), template_mode='bootstrap4')
    admin.add_view(CustomModelView(PaperType, db.session, endpoint='papertype'))
    admin.add_view(CustomModelView(PrintType, db.session, endpoint='printtype'))
    admin.add_view(CustomModelView(PostPrintProcessing, db.session, name='Постпечатная обработка',
                                   endpoint='postprintprocessing'))
    return admin
