from flask import redirect, url_for, request, session
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup


from app.models import *


class MyModelView(ModelView):
    def is_accessible(self):
        return session.get('authenticated')  # Проверка аутентификации

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('authenticated'):
            return redirect(url_for('auth.login', next=request.url))
        return super(MyAdminIndexView, self).index()


class CustomModelView(ModelView):
    def is_accessible(self):
        return True

    column_display_pk = True  # Показывать первичный ключ

    def is_visible(self):
        return False


class OrderAdminView(ModelView):
    def is_accessible(self):
        return True

    column_display_pk = True
    column_list = ('id', 'retail_price', 'cost_price', 'materials')

    def _list_materials(view, context, model, name):
        return Markup(model.materials.replace('\n', '<br>'))

    column_formatters = {
        'materials': _list_materials
    }


class LogsView(BaseView):
    @expose('/')
    def index(self):
        with open('app.log', 'r') as f:
            logs = f.readlines()
        return self.render('admin/logs.html', logs=logs)


def create_admin(app):
    admin = Admin(app, name="PS#1 admin", index_view=MyAdminIndexView(name='Главная'), template_mode='bootstrap4')
    admin.add_view(CustomModelView(PaperType, db.session, name='Бумага', endpoint='papertype'))
    admin.add_view(CustomModelView(PrintType, db.session, name='Печать', endpoint='printtype'))
    admin.add_view(CustomModelView(PostPrintProcessing, db.session, name='Постпечатка', endpoint='postprintprocessing'))
    admin.add_view(CustomModelView(Embossing, db.session, name='Тиснение', endpoint='embossing'))
    admin.add_view(CustomModelView(Variables, db.session, name='Переменные', endpoint='variables'))
    admin.add_view(CustomModelView(PaperTypeLarge, db.session, name='Бумага шир', endpoint='papertypelarge'))
    admin.add_view(CustomModelView(PrintTypeLarge, db.session, name='Печать шир', endpoint='printtypelarge'))
    admin.add_view(CustomModelView(PostPrintProcessingLarge, db.session, name='Постпечатка шир',
                                   endpoint='postprintprocessinglarge'))
    admin.add_view(OrderAdminView(Order, db.session, name='Заказы'))
    admin.add_view(LogsView(name='Логи', endpoint='logs'))  # Добавляем Логи в меню
    admin.add_link(MenuLink(name='Выход', category='', url='/admin/logout'))
    return admin

