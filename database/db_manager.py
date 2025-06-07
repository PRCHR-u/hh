import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict, Any, Optional
from models.employer import Employer
from models.vacancy import Vacancy
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from utils.db_utils import DatabaseConnectionPool, logger

class DBManager:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self):
        """Инициализация менеджера базы данных"""
        self.pool = DatabaseConnectionPool()
        logger.info("DBManager инициализирован")
        self.conn_params = {
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "host": DB_HOST,
            "port": DB_PORT
        }

    def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cur:
                    # Создание таблицы работодателей
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS employers (
                            employer_id INTEGER PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            url TEXT,
                            description TEXT
                        )
                    """)
                    
                    # Создание таблицы вакансий
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS vacancies (
                            vacancy_id INTEGER PRIMARY KEY,
                            employer_id INTEGER REFERENCES employers(employer_id),
                            title VARCHAR(255) NOT NULL,
                            salary_from INTEGER,
                            salary_to INTEGER,
                            currency VARCHAR(10),
                            url TEXT,
                            requirements TEXT,
                            description TEXT
                        )
                    """)
                    conn.commit()
                    logger.info("Таблицы успешно созданы")
        except Exception as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            raise

    def insert_employer(self, employer_id: int, name: str, url: str, 
                       description: str) -> None:
        """Добавление или обновление работодателя в базу данных"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO employers (employer_id, name, url, description)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (employer_id) 
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            url = EXCLUDED.url,
                            description = EXCLUDED.description
                    """, (employer_id, name, url, description))
                    conn.commit()
                    logger.info(f"Работодатель {name} успешно добавлен/обновлен")
        except Exception as e:
            logger.error(f"Ошибка при добавлении работодателя {name}: {e}")
            raise

    def insert_vacancy(self, vacancy_id: int, employer_id: int, title: str,
                      salary_from: Optional[int], salary_to: Optional[int],
                      currency: str, url: str, requirements: str,
                      description: str) -> None:
        """Добавление или обновление вакансии в базу данных"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO vacancies (
                            vacancy_id, employer_id, title, salary_from,
                            salary_to, currency, url, requirements, description
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id) 
                        DO UPDATE SET
                            employer_id = EXCLUDED.employer_id,
                            title = EXCLUDED.title,
                            salary_from = EXCLUDED.salary_from,
                            salary_to = EXCLUDED.salary_to,
                            currency = EXCLUDED.currency,
                            url = EXCLUDED.url,
                            requirements = EXCLUDED.requirements,
                            description = EXCLUDED.description
                    """, (vacancy_id, employer_id, title, salary_from,
                          salary_to, currency, url, requirements, description))
                    conn.commit()
                    logger.info(f"Вакансия {title} успешно добавлена/обновлена")
        except Exception as e:
            logger.error(f"Ошибка при добавлении вакансии {title}: {e}")
            raise

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получение списка всех компаний и количества их вакансий"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                        FROM employers e
                        LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                        GROUP BY e.employer_id, e.name
                        ORDER BY vacancy_count DESC
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении списка компаний: {e}")
            raise

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получение списка всех вакансий с указанием названия компании"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT e.name as company_name, v.title, v.salary_from,
                               v.salary_to, v.currency, v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.employer_id
                        ORDER BY v.salary_from DESC NULLS LAST
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении списка вакансий: {e}")
            raise

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты по вакансиям"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT AVG((COALESCE(salary_from, 0) + 
                                  COALESCE(salary_to, 0)) / 2) as avg_salary
                        FROM vacancies
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    """)
                    result = cur.fetchone()
                    return float(result[0]) if result[0] else 0.0
        except Exception as e:
            logger.error(f"Ошибка при получении средней зарплаты: {e}")
            raise

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получение списка вакансий с зарплатой выше средней"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        WITH avg_salary AS (
                            SELECT AVG((COALESCE(salary_from, 0) + 
                                      COALESCE(salary_to, 0)) / 2) as avg
                            FROM vacancies
                            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                        )
                        SELECT e.name as company_name, v.title, v.salary_from,
                               v.salary_to, v.currency, v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.employer_id
                        WHERE (COALESCE(v.salary_from, 0) + 
                               COALESCE(v.salary_to, 0)) / 2 > 
                              (SELECT avg FROM avg_salary)
                        ORDER BY (COALESCE(v.salary_from, 0) + 
                                 COALESCE(v.salary_to, 0)) / 2 DESC
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении вакансий с высокой зарплатой: {e}")
            raise

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получение списка вакансий по ключевому слову"""
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT e.name as company_name, v.title, v.salary_from,
                               v.salary_to, v.currency, v.url
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.employer_id
                        WHERE v.title ILIKE %s OR v.description ILIKE %s
                        ORDER BY v.salary_from DESC NULLS LAST
                    """, (f'%{keyword}%', f'%{keyword}%'))
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при поиске вакансий по ключевому слову '{keyword}': {e}")
            raise

    def __del__(self):
        """Закрытие пула соединений при удалении объекта"""
        try:
            self.pool.close_all()
            logger.info("Пул соединений закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии пула соединений: {e}") 