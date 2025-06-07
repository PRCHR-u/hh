import os
import logging
from typing import Dict, Any
from psycopg2 import pool
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_db_params() -> None:
    """Проверка наличия всех необходимых параметров для подключения к БД"""
    required_params = {
        'DB_NAME': DB_NAME,
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD
    }
    
    missing_params = [
        param for param, value in required_params.items() 
        if not value
    ]
    
    if missing_params:
        error_msg = f"Отсутствуют обязательные параметры БД: {', '.join(missing_params)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def get_connection_params() -> Dict[str, Any]:
    """Получение параметров подключения к БД"""
    return {
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT
    }


class DatabaseConnectionPool:
    """Класс для управления пулом соединений с базой данных"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            try:
                validate_db_params()
                self._pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    **get_connection_params()
                )
                logger.info("Пул соединений с базой данных успешно создан")
            except Exception as e:
                logger.error(f"Ошибка при создании пула соединений: {e}")
                raise
    
    def get_connection(self):
        """Получение соединения из пула"""
        try:
            conn = self._pool.getconn()
            logger.debug("Получено соединение из пула")
            return conn
        except Exception as e:
            logger.error(f"Ошибка при получении соединения: {e}")
            raise
    
    def return_connection(self, conn):
        """Возврат соединения в пул"""
        try:
            self._pool.putconn(conn)
            logger.debug("Соединение возвращено в пул")
        except Exception as e:
            logger.error(f"Ошибка при возврате соединения: {e}")
            raise
    
    def close_all(self):
        """Закрытие всех соединений в пуле"""
        if self._pool:
            self._pool.closeall()
            logger.info("Все соединения в пуле закрыты") 