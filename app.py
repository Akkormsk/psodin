from flask import Flask, render_template, request, redirect, url_for, flash
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from models import db, PaperType, PrintType

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

admin = Admin(app, name='PSadmin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(PaperType, db.session, name='Типы бумаги', endpoint='papertype'))
admin.add_view(ModelView(PrintType, db.session, name='Типы печати', endpoint='printtype'))


class CalculatorView(BaseView):
    @expose('/')
    def index(self):
        paper_types = PaperType.query.all()
        print_types = PrintType.query.all()
        return self.render('calculator.html', paper_types=paper_types, print_types=print_types)

    @expose('/calculate', methods=('POST',))
    def calculate(self):
        paper_type_id = request.form.get('paper_type')
        print_type_id = request.form.get('print_type')
        quantity = request.form.get('quantity')

        if not quantity:
            flash('Введите значение в поле количество', 'error')
            return redirect(url_for('calculator.index'))

        paper_type = PaperType.query.get(paper_type_id)
        print_type = PrintType.query.get(print_type_id)

        if not paper_type or not print_type:
            flash('Неверный выбор типа бумаги или печати', 'error')
            return redirect(url_for('calculator.index'))

        try:
            quantity = int(quantity)
        except ValueError:
            flash('Количество должно быть числом', 'error')
            return redirect(url_for('calculator.index'))

        total_price = round((paper_type.price_per_unit + print_type.price_per_unit) * quantity, 2)
        return self.render('calculator.html', paper_types=paper_type, print_types=print_type, total_price=total_price)


admin.add_view(CalculatorView(name='Калькулятор', endpoint='calculator'))


@app.route('/')
def admin_index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
