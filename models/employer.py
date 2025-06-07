from dataclasses import dataclass
from typing import Optional

@dataclass
class Employer:
    """Класс для представления работодателя"""
    id: int
    name: str
    description: Optional[str]
    site_url: Optional[str]
    hh_url: Optional[str]

    @classmethod
    def from_hh_data(cls, data: dict) -> 'Employer':
        """Создает объект Employer из данных API hh.ru"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            site_url=data.get('site_url', ''),
            hh_url=data.get('alternate_url', '')
        ) 