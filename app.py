from flask import Flask, render_template, redirect, url_for, request, flash
from flask_migrate import Migrate
from config import Config
from models import *
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from admin import create_admin
from flask_session import Session

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
Session(app)


class User(UserMixin):
    id = 1  # Поскольку мы не используем базу данных для пользователей


@login_manager.user_loader
def load_user(user_id):
    return User()


admin = create_admin(app)


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/calculator/sheet_printing', methods=['GET', 'POST'])
@app.route('/sheet_printing', methods=['GET', 'POST'])
def sheet_printing():
    if request.method == 'POST':
        paper_type_id = request.form['paper_type']
        paper_quantity = int(request.form.get('paper_quantity', ''))
        print_type_id = request.form['print_type']
        print_quantity = int(request.form.get('print_quantity', ''))
        postprint_type_id = request.form['postprint_type']
        postprint_quantity = int(request.form.get('postprint_quantity', ''))
        work_time = float(request.form['work_time'])

        paper_type = PaperType.query.get(paper_type_id)
        print_type = PrintType.query.get(print_type_id)
        postprint_type = PostPrintProcessing.query.get(postprint_type_id)

        machine_type = request.form['machine_type']
        if machine_type == 'xerox':
            print_cost = print_quantity * print_type.price_per_unit_xerox
        else:
            print_cost = print_quantity * print_type.price_per_unit_konica

        paper_cost = paper_quantity * paper_type.price_per_unit
        postprint_cost = postprint_quantity * postprint_type.price_per_unit
        work = Variables.query.get(1)
        margin_ratio = Variables.query.get(2)
        regulars_discount = Variables.query.get(5)
        partners_discount = Variables.query.get(6)
        urgency = Variables.query.get(7)

        if work:
            work_cost = work_time * work.value
        else:
            work_cost = 0

        total_cost = paper_cost + print_cost + postprint_cost + work_cost
        retail_price = total_cost * margin_ratio.value
        regulars_price = retail_price * regulars_discount.value
        partners_price = retail_price * partners_discount.value
        urgent_price = retail_price * urgency.value

        return render_template('Calculator/sheet_printing.html', total_cost=total_cost,
                               paper_type=paper_type, paper_quantity=paper_quantity,
                               print_type=print_type, print_quantity=print_quantity,
                               postprint_type=postprint_type, postprint_quantity=postprint_quantity,
                               work_time=work_time,
                               paper_types=PaperType.query.all(),
                               print_types=PrintType.query.all(),
                               postprint_types=PostPrintProcessing.query.all(),
                               work=work.value, print_cost=print_cost, retail_price=retail_price,
                               regulars_price=regulars_price, partners_price=partners_price, urgent_price=urgent_price)

    return render_template('Calculator/sheet_printing.html',
                           paper_types=PaperType.query.all(),
                           print_types=PrintType.query.all(),
                           postprint_types=PostPrintProcessing.query.all())


@app.route('/update_print_options')
def update_print_options():
    machine_type = request.args.get('machine_type')
    if machine_type == 'xerox':
        return render_template('Calculator/sheet_printing_xerox.html', print_types=PrintType.query.all())
    elif machine_type == 'konica':
        return render_template('Calculator/sheet_printing_konica.html', print_types=PrintType.query.all())


@app.route('/calculator')
def calculator():
    return redirect(url_for('sheet_printing'))


@app.route('/multi_page_printing')
def multi_page_printing():
    return render_template('Calculator/multi_page_printing.html')


@app.route('/wide_format_printing')
def wide_format_printing():
    return render_template('Calculator/wide_format_printing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == Config.SECRET_ADMIN_PASSWORD:
            user = User()
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.index'))
        flash('Неверный пароль')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
