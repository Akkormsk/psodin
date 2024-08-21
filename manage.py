from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import __init__, db

migrate = Migrate(__init__, db)
manager = Manager(__init__)

# Добавление команды миграции в менеджер
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
