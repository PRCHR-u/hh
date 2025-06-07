import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Создаем директорию для логов, если она не существует
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Формат логов
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Настройка корневого логгера
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(log_format, date_format)
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# Создаем обработчик для записи в файл
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(log_format, date_format)
file_handler.setFormatter(file_formatter)
root_logger.addHandler(file_handler)

# Создаем логгер для базы данных
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

# Создаем логгер для API
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO) 