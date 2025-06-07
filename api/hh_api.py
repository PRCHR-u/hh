import requests
from typing import List, Dict, Any
from models.employer import Employer
from models.vacancy import Vacancy

class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""
    
    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }

    def get_employer_info(self, employer_id: int) -> Employer:
        """Получение информации о работодателе"""
        url = f"{self.base_url}/employers/{employer_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return Employer.from_hh_data(response.json())

    def get_employer_vacancies(self, employer_id: int) -> List[Vacancy]:
        """Получение вакансий работодателя"""
        url = f"{self.base_url}/vacancies"
        params = {
            "employer_id": employer_id,
            "per_page": 100,
            "page": 0
        }
        all_vacancies = []
        
        while True:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            vacancies = [
                Vacancy.from_hh_data(item) 
                for item in data.get("items", [])
            ]
            all_vacancies.extend(vacancies)
            
            if not data.get("pages") or params["page"] >= data["pages"] - 1:
                break
                
            params["page"] += 1
            
        return all_vacancies 