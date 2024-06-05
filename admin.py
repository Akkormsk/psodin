from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required

from models import db, PaperType, PrintType


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


def create_admin(app):
    admin = Admin(app, name="PSadmin", index_view=MyAdminIndexView(), template_mode='bootstrap3')
    admin.add_view(MyModelView(PaperType, db.session, endpoint='papertype'))
    admin.add_view(MyModelView(PrintType, db.session, endpoint='printtype'))
    return admin