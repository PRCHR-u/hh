import os
from dotenv import load_dotenv
from pathlib import Path

# Получаем путь к текущей директории
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

# Загружаем переменные окружения
load_dotenv(env_path)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# Отладочная информация
print("Путь к .env:", env_path)
print("Файл .env существует:", env_path.exists())
print("DB_NAME:", DB_NAME)
print("DB_USER:", DB_USER)
print("DB_PASSWORD:", "***" if DB_PASSWORD else "None")
print("DB_HOST:", DB_HOST)
print("DB_PORT:", DB_PORT) 