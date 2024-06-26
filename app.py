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
        paper_type_ids = request.form.getlist('paper_type')
        paper_quantities = request.form.getlist('paper_quantity')
        machine_types = request.form.getlist('machine_type')
        print_type_ids = request.form.getlist('print_type')
        print_quantities = request.form.getlist('print_quantity')
        postprint_types = request.form.getlist('postprint_type')
        postprint_quantities = request.form.getlist('postprint_quantity')
        work_time = float(request.form['work_time'])

        paper_details = []
        paper_cost = 0
        total_paper = 0
        for i in range(len(paper_type_ids)):
            paper = PaperType.query.get(paper_type_ids[i])
            quantity = int(paper_quantities[i])
            paper_cost += quantity * paper.price_per_unit
            total_paper += quantity
            paper_details.append((paper, quantity))

        print_details = []
        print_cost = 0
        for i in range(len(machine_types)):
            machine_type = machine_types[i]
            print_type = PrintType.query.get(print_type_ids[i])
            quantity = int(print_quantities[i])
            if machine_type == 'xerox':
                print_cost += quantity * print_type.price_per_unit_xerox
            else:
                print_cost += quantity * print_type.price_per_unit_konica
            print_details.append((machine_type, print_type, quantity))

        postprint_details = []
        postprint_cost = 0
        for i in range(len(postprint_types)):
            postprint_type = PostPrintProcessing.query.get(postprint_types[i])
            quantity = int(postprint_quantities[i])
            postprint_cost += quantity * postprint_type.price_per_unit
            postprint_details.append((postprint_type, quantity))

        work = Variables.query.get(1)
        margin_ratio = Variables.query.get(2)
        regulars_discount = Variables.query.get(5)
        partners_discount = Variables.query.get(6)
        urgency = Variables.query.get(7)

        work_cost = work_time * work.value if work else 0

        total_cost = round(paper_cost + print_cost + postprint_cost + work_cost, 2)
        retail_price = round(total_cost * margin_ratio.value * (1 + (1/total_paper)), 2)
        regulars_price = round(retail_price * regulars_discount.value, 2)
        partners_price = round(retail_price * partners_discount.value, 2)
        urgent_price = round(retail_price * urgency.value, 2)

        return render_template('Calculator/sheet_printing.html', total_cost=total_cost,
                               paper_details=paper_details, print_details=print_details,
                               postprint_details=postprint_details, work_time=work_time,
                               paper_cost=paper_cost, postprint_cost=postprint_cost,
                               paper_types=PaperType.query.all(), print_types=PrintType.query.all(),
                               postprint_types=PostPrintProcessing.query.all(), work_cost=work_cost,
                               print_cost=print_cost, retail_price=retail_price,
                               regulars_price=regulars_price, partners_price=partners_price,
                               urgent_price=urgent_price, machine_type=machine_types[0])

    return render_template('Calculator/sheet_printing.html',
                           paper_types=PaperType.query.all(),
                           print_types=PrintType.query.all(),
                           postprint_types=PostPrintProcessing.query.all(),
                           machine_type='xerox',
                           paper_details=[(0,)],
                           print_details=[('xerox', 0,)],
                           postprint_details=[(0,)])  # Default values for initial load


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
        app.run(host="0.0.0.0", port=5000)
    #     db.create_all()
    # app.run(debug=True)
