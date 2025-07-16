import psycopg2
from typing import Optional, List
from src.config import DB_CONFIG
from src.models import Employer, Vacancy
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
            )
            self.conn.set_client_encoding("UTF8")
            self.cur = self.conn.cursor()
            self.create_tables()
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Очистка текста от проблемных символов."""
        if text is None:
            return None
        cleaned = re.sub(r"[^\x00-\x7F]+", " ", text)
        return cleaned.encode("utf-8", "ignore").decode("utf-8")

    def create_tables(self):
        try:
            self.cur.execute(
                """
            CREATE TABLE IF NOT EXISTS employers (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT
            )
            """
            )

            self.cur.execute(
                """
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                employer_id INTEGER REFERENCES employers(id),
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255)
            )
            """
            )
            self.conn.commit()
            logger.info("Таблицы успешно созданы")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            self.conn.rollback()
            raise

    def save_employer(self, employer: Employer):
        try:
            if not employer.name or employer.name.strip() == "":
                logger.warning(
                    f"Попытка сохранить работодателя с пустым именем (ID: {employer.id})"
                )
                return

            cleaned_name = self._clean_text(employer.name)
            cleaned_description = self._clean_text(employer.description)
            cleaned_url = self._clean_text(employer.url)

            self.cur.execute(
                "INSERT INTO employers (id, name, url, description) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, "
                "url = EXCLUDED.url, description = EXCLUDED.description",
                (employer.id, cleaned_name, cleaned_url, cleaned_description),
            )
            self.conn.commit()
            logger.info(f"Работодатель сохранен: {employer.name}")
        except Exception as e:
            logger.error(f"Ошибка сохранения работодателя: {e}")
            self.conn.rollback()
            raise

    def save_vacancy(self, vacancy: Vacancy):
        try:
            cleaned_name = self._clean_text(vacancy.name)
            cleaned_url = self._clean_text(vacancy.url)
            cleaned_currency = self._clean_text(vacancy.currency)

            salary_from = vacancy.salary_from or 0
            salary_to = vacancy.salary_to or 0

            self.cur.execute(
                "INSERT INTO vacancies (id, name, employer_id, salary_from, "
                "salary_to, currency, url) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, "
                "employer_id = EXCLUDED.employer_id, "
                "salary_from = EXCLUDED.salary_from, "
                "salary_to = EXCLUDED.salary_to, "
                "currency = EXCLUDED.currency, "
                "url = EXCLUDED.url",
                (
                    vacancy.id,
                    cleaned_name,
                    vacancy.employer_id,
                    salary_from,
                    salary_to,
                    cleaned_currency,
                    cleaned_url,
                ),
            )
            self.conn.commit()
            logger.info(f"Вакансия сохранена: {vacancy.name}")
        except Exception as e:
            logger.error(f"Ошибка сохранения вакансии: {e}")
            self.conn.rollback()
            raise

    def get_all_employers(self) -> List[Employer]:
        """Получить всех работодателей из базы данных"""
        try:
            self.cur.execute("SELECT id, name, url, description FROM employers")
            employers = []
            for row in self.cur.fetchall():
                employers.append(
                    Employer(id=row[0], name=row[1], url=row[2], description=row[3])
                )
            return employers
        except Exception as e:
            logger.error(f"Ошибка получения списка работодателей: {e}")
            raise

    def close(self):
        """Закрытие соединения с базой данных"""
        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
                logger.info("Соединение с базой данных закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")
