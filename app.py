from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from models import db, PaperType, PrintType

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

admin = Admin(app, name='PSadmin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(PaperType, db.session))
admin.add_view(ModelView(PrintType, db.session))


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
    return render_template('admin/calculator.html', paper_types=paper_types, print_types=print_types,
                           total_cost=total_cost)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
