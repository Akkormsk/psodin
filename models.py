from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

class PaperTypeLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

class PrintType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit_xerox = db.Column(db.Float, nullable=False)
    price_per_unit_konica = db.Column(db.Float, nullable=False)

class PrintTypeLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit_canon = db.Column(db.Float, nullable=False)

class PostPrintProcessing(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

class PostPrintProcessingLarge(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

class Embossing(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

class Variables(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'  # Обновлено название таблицы
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    retail_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    materials = db.Column(db.String(500), nullable=False)  # Указание длины
