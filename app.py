from flask import Flask, render_template, redirect, url_for, request, flash
from flask_migrate import Migrate
from config import Config
from models import db, PaperType, PrintType
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


@app.route('/calculator/', methods=['GET', 'POST'])
def calculator():
    paper_types = PaperType.query.all()
    print_types = PrintType.query.all()
    total_cost = None
    if request.method == 'POST':
        paper_type_id = request.form['paper_type']
        print_type_id = request.form['print_type']
        quantity = request.form.get('quantity', type=int)
        if not quantity:
            flash("Введите значение в поле количество", "warning")
            return redirect(url_for('calculator'))
        paper_type = PaperType.query.get(paper_type_id)
        print_type = PrintType.query.get(print_type_id)
        total_cost = round((paper_type.price_per_unit + print_type.price_per_unit) * quantity, 2)
    return render_template('Calculator/calculator.html', paper_types=paper_types, print_types=print_types,
                           total_cost=total_cost)


@app.route('/sheet_printing')
def sheet_printing():
    return render_template('Calculator/sheet_printing.html')


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
