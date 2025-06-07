from dataclasses import dataclass
from typing import Optional

@dataclass
class Vacancy:
    """Класс для представления вакансии"""
    id: int
    employer_id: int
    title: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    currency: Optional[str]
    url: str
    requirement: Optional[str]
    responsibility: Optional[str]

    @classmethod
    def from_hh_data(cls, data: dict) -> 'Vacancy':
        """Создает объект Vacancy из данных API hh.ru"""
        salary = data.get('salary', {})
        return cls(
            id=data['id'],
            employer_id=data['employer']['id'],
            title=data['name'],
            salary_from=salary.get('from'),
            salary_to=salary.get('to'),
            currency=salary.get('currency'),
            url=data['alternate_url'],
            requirement=data.get('snippet', {}).get('requirement'),
            responsibility=data.get('snippet', {}).get('responsibility')
        ) 