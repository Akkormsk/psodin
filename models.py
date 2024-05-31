from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


def init_db():
    with db.session.no_autoflush:
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
