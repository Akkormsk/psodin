from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/calculator/', methods=['GET', 'POST'])
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
