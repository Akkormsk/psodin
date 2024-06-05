from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price_per_unit = db.Column(db.Float)

    def __repr__(self):
        return f'<PaperType {self.name}>'


class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price_per_unit = db.Column(db.Float)

    def __repr__(self):
        return f'<PrintType {self.name}>'

