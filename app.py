from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from models import db, PaperType, PrintType, init_db
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY
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
        total_price = round(quantity * (paper_type.price_per_unit + print_type.price_per_unit), 2)
        paper_types = PaperType.query.all()
        print_types = PrintType.query.all()
        return self.render('admin/calculator.html', total_price=total_price, paper_types=paper_types,
                           print_types=print_types)


admin = Admin(app, name='Print Shop Admin', template_mode='bootstrap3', base_template='base.html')
admin.add_view(ModelView(PaperType, db.session))
admin.add_view(ModelView(PrintType, db.session))
admin.add_view(CalculatorView(name='Calculator', endpoint='calculator'))


@app.route('/')
def index():
    return redirect('/admin')


if __name__ == '__main__':
    # Выполняем инициализацию базы данных при запуске приложения
    with app.app_context():
        init_db()
    app.run(debug=True)
