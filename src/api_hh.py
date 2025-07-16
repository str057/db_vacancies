import requests
import logging
from typing import Dict, List, Optional

# Добавляем настройку логгера в начале файла
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HeadHunterAPI:
    """Класс для работы с API HeadHunter."""

    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": "HH-API-Client/1.0"}
        self.timeout = 10

    def _make_request(self, url: str, params: dict = None) -> Optional[Dict]:
        """Выполнение HTTP запроса с обработкой ошибок"""
        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
            return None

    def get_employers(self, employer_ids: List[str]) -> List[Dict]:
        """Получить данные о компаниях по их ID."""
        employers = []
        for employer_id in employer_ids:
            url = f"{self.base_url}/employers/{employer_id}"
            data = self._make_request(url)
            if data:
                if not data.get("name"):
                    logger.warning(f"У работодателя {employer_id} отсутствует название")
                    continue
                employers.append(data)
        return employers

    def get_vacancies(self, employer_id: str) -> List[Dict]:
        """Получить вакансии компании по её ID."""
        url = f"{self.base_url}/vacancies"
        params = {"employer_id": employer_id, "per_page": 100}
        data = self._make_request(url, params)
        return data.get("items", []) if data else []