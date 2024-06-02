from flask import Flask, render_template, redirect, url_for, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import db, init_db, PaperType, PrintType

import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
migrate = Migrate(app, db)


# Views
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
        quantity = request.form['quantity']

        if not quantity:
            error_message = "Введите значение в поле количество"
            paper_types = PaperType.query.all()
            print_types = PrintType.query.all()
            return self.render('admin/calculator.html', error_message=error_message, paper_types=paper_types,
                               print_types=print_types)

        quantity = int(quantity)
        paper_type = PaperType.query.get(paper_type_id)
        print_type = PrintType.query.get(print_type_id)
        total_price = round(quantity * (paper_type.price_per_unit + print_type.price_per_unit), 2)
        paper_types = PaperType.query.all()
        print_types = PrintType.query.all()
        return self.render('admin/calculator.html', total_price=total_price, paper_types=paper_types,
                           print_types=print_types)


# Initialize admin panel
admin = Admin(app, name='Print Shop Admin', template_mode='bootstrap3')
admin.add_view(ModelView(PaperType, db.session, endpoint='papertype'))
admin.add_view(ModelView(PrintType, db.session, endpoint='printtype'))
admin.add_view(CalculatorView(name='Calculator', endpoint='calculator'))


@app.route('/')
def index():
    return redirect('/admin')


@app.route('/admin/')
def admin_index():
    return render_template('admin/index.html')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
