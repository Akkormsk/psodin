from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PaperTypeLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PrintTypeLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PostPrintProcessing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class PostPrintProcessingLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class Embossing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)


class Variables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
