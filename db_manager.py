import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from typing import List, Dict, Any

class DBManager:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self):
        self.conn_params = {
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "host": DB_HOST,
            "port": DB_PORT
        }

    def create_tables(self):
        """Создание таблиц в базе данных"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                # Создание таблицы employers
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        employer_id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        site_url VARCHAR(255),
                        hh_url VARCHAR(255)
                    )
                """)
                
                # Создание таблицы vacancies
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        vacancy_id INTEGER PRIMARY KEY,
                        employer_id INTEGER REFERENCES employers(employer_id),
                        title VARCHAR(255) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(255),
                        requirement TEXT,
                        responsibility TEXT
                    )
                """)
                conn.commit()

    def insert_employer(self, employer_data: Dict[str, Any]):
        """Добавление работодателя в базу данных"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO employers (employer_id, name, description, site_url, hh_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (employer_id) DO UPDATE
                    SET name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        site_url = EXCLUDED.site_url,
                        hh_url = EXCLUDED.hh_url
                """, (
                    employer_data['id'],
                    employer_data['name'],
                    employer_data.get('description', ''),
                    employer_data.get('site_url', ''),
                    employer_data.get('alternate_url', '')
                ))
                conn.commit()

    def insert_vacancy(self, vacancy_data: Dict[str, Any]):
        """Добавление вакансии в базу данных"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                salary_from = vacancy_data.get('salary', {}).get('from')
                salary_to = vacancy_data.get('salary', {}).get('to')
                currency = vacancy_data.get('salary', {}).get('currency')
                
                cur.execute("""
                    INSERT INTO vacancies (
                        vacancy_id, employer_id, title, salary_from, salary_to,
                        currency, url, requirement, responsibility
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO UPDATE
                    SET title = EXCLUDED.title,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        url = EXCLUDED.url,
                        requirement = EXCLUDED.requirement,
                        responsibility = EXCLUDED.responsibility
                """, (
                    vacancy_data['id'],
                    vacancy_data['employer']['id'],
                    vacancy_data['name'],
                    salary_from,
                    salary_to,
                    currency,
                    vacancy_data['alternate_url'],
                    vacancy_data.get('snippet', {}).get('requirement', ''),
                    vacancy_data.get('snippet', {}).get('responsibility', '')
                ))
                conn.commit()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получение списка всех компаний и количества вакансий"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.name
                    ORDER BY vacancy_count DESC
                """)
                return cur.fetchall()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получение списка всех вакансий"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.name as company_name, v.title, v.salary_from, v.salary_to,
                           v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    ORDER BY e.name, v.title
                """)
                return cur.fetchall()

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты по вакансиям"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """)
                return cur.fetchone()[0] or 0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получение списка вакансий с зарплатой выше средней"""
        avg_salary = self.get_avg_salary()
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.name as company_name, v.title, v.salary_from, v.salary_to,
                           v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
                    ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
                """, (avg_salary,))
                return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получение списка вакансий по ключевому слову"""
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.name as company_name, v.title, v.salary_from, v.salary_to,
                           v.currency, v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE LOWER(v.title) LIKE LOWER(%s)
                    ORDER BY e.name, v.title
                """, (f'%{keyword}%',))
                return cur.fetchall() 