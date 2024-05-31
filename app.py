from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import db, PaperType, PrintType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///print_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем отслеживание изменений
db.init_app(app)
migrate = Migrate(app, db)


# Оставляем инициализацию административной панели

class CalculatorView(BaseView):
    @expose('/')
    def index(self):
        paper_types = PaperType.query.all()
        print_types = PrintType.query.all()
        return self.render('admin/calculator.html', paper_types=paper_types, print_types=print_types)

    @expose('/calculate', methods=['POST'])
    def calculate(self):
        paper_type_id = int(request.form['paper_type'])
        print_type_id = int(request.form['print_type'])
        quantity = int(request.form['quantity'])
        paper_type = PaperType.query.get(paper_type_id)
        print_type = PrintType.query.get(print_type_id)
        total_price = quantity * (paper_type.price_per_unit + print_type.price_per_unit)
        paper_types = PaperType.query.all()
        print_types = PrintType.query.all()
        return self.render('admin/calculator.html', total_price=total_price, paper_types=paper_types,
                           print_types=print_types)


admin = Admin(app, name='Print Shop Admin', template_mode='bootstrap3', base_template='base.html')
admin.add_view(ModelView(PaperType, db.session))
admin.add_view(ModelView(PrintType, db.session))
admin.add_view(CalculatorView(name='Calculator', endpoint='calculator'))


def init_db():
    with app.app_context():
        db.create_all()
        if PaperType.query.count() == 0:
            paper_types = [
                {"name": "Standard", "price_per_unit": 0.10},
                {"name": "Premium", "price_per_unit": 0.20}
            ]
            for paper_type in paper_types:
                db.session.add(PaperType(name=paper_type['name'], price_per_unit=paper_type['price_per_unit']))
            db.session.commit()

        if PrintType.query.count() == 0:
            print_types = [
                {"name": "Digital", "price_per_unit": 0.05},
                {"name": "Offset", "price_per_unit": 0.15}
            ]
            for print_type in print_types:
                db.session.add(PrintType(name=print_type['name'], price_per_unit=print_type['price_per_unit']))
            db.session.commit()


if __name__ == '__main__':
    # Выполняем инициализацию базы данных при запуске приложения
    with app.app_context():
        init_db()
    app.run(debug=True)


@app.route('/')
def index():
    return redirect('/admin')
