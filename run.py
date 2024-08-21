import os
from app import app

if __name__ == '__main__':
    with app.app_context():
        port = int(os.environ.get('PORT', 3060))  # Получаем порт из переменной окружения
        app.run(host="0.0.0.0", port=port)  # Используем этот порт для запуска приложения
