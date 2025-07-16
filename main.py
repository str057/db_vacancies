import sys
import logging
from pathlib import Path
from src.api_hh import HeadHunterAPI
from src.models import Employer, Vacancy
from src.database import Database
from src.db_manager import DBManager
from src.config import EMPLOYER_IDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_environment():
    """Настройка окружения"""
    try:
        sys.path.append(str(Path(__file__).parent))
        logger.info("Настройка окружения завершена")
    except Exception as e:
        logger.error(f"Ошибка настройки окружения: {e}")
        raise


def initialize_database() -> Database:
    """Инициализация базы данных"""
    try:
        db = Database()
        db.create_tables()
        logger.info("База данных успешно инициализирована")
        return db
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise


def load_employers_data(hh_api: HeadHunterAPI, db: Database) -> bool:
    """Загрузка данных о работодателях"""
    try:
        employers_data = hh_api.get_employers(EMPLOYER_IDS)
        if not employers_data:
            logger.error("Не удалось получить данные о компаниях")
            return False

        for employer_data in employers_data:
            try:
                employer = Employer(
                    id=int(employer_data.get("id")),
                    name=employer_data.get("name", ""),
                    url=employer_data.get("site_url", ""),
                    description=employer_data.get("description", ""),
                )
                db.save_employer(
                    employer
                )  # Используем save_employer вместо insert_employer
                logger.info(f"Добавлен работодатель: {employer.name}")
            except Exception as e:
                logger.error(
                    f"Ошибка обработки компании {employer_data.get('id')}: {e}"
                )
                continue

        return True
    except Exception as e:
        logger.error(f"Критическая ошибка загрузки работодателей: {e}")
        return False


def load_vacancies_data(hh_api: HeadHunterAPI, db: Database) -> bool:
    """Загрузка данных о вакансиях"""
    try:
        employers = db.get_all_employers()
        for employer in employers:
            try:
                vacancies_data = hh_api.get_vacancies(str(employer.id))
                for vacancy_data in vacancies_data:
                    try:
                        salary_data = vacancy_data.get("salary")
                        if salary_data:
                            salary_from = salary_data.get("from")
                            salary_to = salary_data.get("to")
                            currency = salary_data.get("currency")
                        else:
                            salary_from = None
                            salary_to = None
                            currency = None

                        vacancy = Vacancy(
                            id=int(vacancy_data.get("id")),
                            name=vacancy_data.get("name", ""),
                            employer_id=employer.id,
                            salary_from=salary_from,
                            salary_to=salary_to,
                            currency=currency,
                            url=vacancy_data.get("alternate_url", ""),
                        )
                        db.save_vacancy(vacancy)
                        logger.info(f"Добавлена вакансия: {vacancy.name}")
                    except Exception as e:
                        logger.error(
                            f"Ошибка обработки вакансии {vacancy_data.get('id')}: {e}"
                        )
                        continue
            except Exception as e:
                logger.error(f"Ошибка получения вакансий для {employer.id}: {e}")
                continue

        return True
    except Exception as e:
        logger.error(f"Критическая ошибка загрузки вакансий: {e}")
        return False


def main():
    """Основная функция программы"""
    db = None
    try:
        setup_environment()

        logger.info("Загрузка данных с HeadHunter...")
        hh_api = HeadHunterAPI()
        db = initialize_database()

        if not load_employers_data(hh_api, db):
            raise RuntimeError("Не удалось загрузить данные о работодателях")

        if not load_vacancies_data(hh_api, db):
            raise RuntimeError("Не удалось загрузить данные о вакансиях")

        logger.info("Данные успешно загружены в базу данных")

        # Запуск интерфейса пользователя
        db_manager = DBManager()
        # Здесь можно добавить вызовы методов DBManager для работы с пользователем
        # Например:
        companies = db_manager.get_companies_and_vacancies_count()
        logger.info(f"Компании и количество вакансий: {companies}")

    except Exception as e:
        logger.error(f"Критическая ошибка в работе программы: {e}")
        sys.exit(1)
    finally:
        if db is not None:
            db.close()
        logger.info("Работа программы завершена")


if __name__ == "__main__":
    main()
