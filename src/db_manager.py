import psycopg2
import logging
from typing import List, Dict
from src.config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBManager:
    """Класс для управления данными в базе данных PostgreSQL."""

    def __init__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.set_client_encoding("UTF8")
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def _execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Выполнение SQL запроса с обработкой ошибок"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """Получить список компаний и количество вакансий."""
        query = """
            SELECT e.name, COUNT(v.id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancies_count DESC
        """
        results = self._execute_query(query)
        return [{"name": row[0], "vacancies_count": row[1]} for row in results]

    # ... другие методы класса с аналогичной структурой ...

    def close(self):
        """Закрытие соединения с базой данных."""
        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
                logger.info("Соединение с базой данных закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")
