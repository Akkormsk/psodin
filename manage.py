from flask_migrate import Migrate
from app import app
from app.models import db

# Инициализация миграций для текущего приложения
migrate = Migrate(app, db)

if __name__ == '__main__':
    # Запуск не нужен: миграции вызываются через flask CLI
    # Оставляем заглушку для совместимости
    print('Use: set FLASK_APP=app && flask db upgrade')
