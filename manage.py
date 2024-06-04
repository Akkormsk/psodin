from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

# Добавление команды миграции в менеджер
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
