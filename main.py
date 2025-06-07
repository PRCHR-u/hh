from api.hh_api import HeadHunterAPI
from database.db_manager import DBManager
import time


def print_vacancies(vacancies, limit=None):
    """Вывод списка вакансий"""
    if not vacancies:
        print("Вакансии не найдены")
        return

    for i, vacancy in enumerate(vacancies[:limit], 1):
        salary = f"{vacancy['salary_from']}-{vacancy['salary_to']} {vacancy['currency']}" \
            if vacancy['salary_from'] or vacancy['salary_to'] else "Не указана"
        print(f"{i}. {vacancy['company_name']} - {vacancy['title']}")
        print(f"   Зарплата: {salary}")
        print(f"   Ссылка: {vacancy['url']}")
        print()


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    db_manager = DBManager()
    
    while True:
        print("\nВыберите действие:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить список вакансий с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")
        
        choice = input("\nВведите номер действия: ")
        
        if choice == "0":
            print("До свидания!")
            break
            
        elif choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            print("\nСписок компаний и количество вакансий:")
            for company in companies:
                print(f"{company['name']}: {company['vacancy_count']} вакансий")
                
        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            print("\nСписок всех вакансий:")
            print_vacancies(vacancies, limit=10)
            
        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата: {avg_salary:.2f}")
            
        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            print_vacancies(vacancies, limit=10)
            
        elif choice == "5":
            keyword = input("\nВведите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print(f"\nРезультаты поиска по ключевому слову '{keyword}':")
            print_vacancies(vacancies, limit=10)
            
        else:
            print("\nНеверный выбор. Пожалуйста, выберите действие из списка.")
        
        input("\nНажмите Enter для продолжения...")


def main():
    # Список ID компаний для получения данных
    employer_ids = [
        1740,    # Яндекс
        3529,    # Сбер
        78638,   # Тинькофф
        15478,   # VK
        2180,    # Ozon
        84585,   # Авито
        2748,    # Ростелеком
        1122462, # 1С
        3776,    # МТС
        3127     # Мегафон
    ]

    # Инициализация API и менеджера БД
    hh_api = HeadHunterAPI()
    db_manager = DBManager()

    # Создание таблиц
    db_manager.create_tables()

    # Получение и сохранение данных о работодателях и их вакансиях
    for employer_id in employer_ids:
        try:
            # Получение информации о работодателе
            employer = hh_api.get_employer_info(employer_id)
            db_manager.insert_employer(employer)
            print(f"Обработан работодатель: {employer.name}")

            # Получение вакансий работодателя
            vacancies = hh_api.get_employer_vacancies(employer_id)
            for vacancy in vacancies:
                db_manager.insert_vacancy(vacancy)
            print(f"Добавлено {len(vacancies)} вакансий")

            # Задержка для соблюдения ограничений API
            time.sleep(0.25)

        except Exception as e:
            print(f"Ошибка при обработке работодателя {employer_id}: {str(e)}")

    # Запуск интерактивного режима
    user_interaction()


if __name__ == "__main__":
    main() 