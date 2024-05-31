from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


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


# Настройка административной панели
admin = Admin(app, name='Print Shop Admin', template_mode='bootstrap3', base_template='base.html')
admin.add_view(ModelView(PaperType, db.session))
admin.add_view(ModelView(PrintType, db.session))
admin.add_view(CalculatorView(name='Calculator', endpoint='calculator'))


@app.route('/')
def index():
    return redirect('/admin')


if __name__ == '__main__':
    if not os.path.exists('print_shop.db'):
        with app.app_context():
            init_db()
    app.run(debug=True)
