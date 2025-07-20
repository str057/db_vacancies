import psycopg2
from typing import List, Dict


class DBManager:
    """
    Класс для управления данными в PostgreSQL.
    Реализует все методы, указанные в техническом задании.
    """

    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost'):
        """
        Инициализирует подключение к базе данных.

        :param dbname: имя базы данных
        :param user: имя пользователя
        :param password: пароль
        :param host: хост (по умолчанию 'localhost')
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.conn.autocommit = True

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        :return: список словарей формата [{'company': str, 'count': int}]
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT employers.name, COUNT(vacancies.id) 
                FROM employers
                LEFT JOIN vacancies ON employers.id = vacancies.employer_id
                GROUP BY employers.name
            """)
            return [{'company': row[0], 'count': row[1]} for row in cur.fetchall()]

    def get_all_vacancies(self) -> List[Dict]:
        """
        Получает список всех вакансий с указанием:
        - названия компании
        - названия вакансии
        - зарплаты
        - ссылки на вакансию

        :return: список словарей формата [{
            'company': str,
            'title': str,
            'salary': str,
            'link': str
        }]
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    employers.name, 
                    vacancies.name, 
                    CONCAT(
                        COALESCE(vacancies.salary_from, 'Не указана'), ' - ', 
                        COALESCE(vacancies.salary_to, 'Не указана'), ' ', 
                        COALESCE(vacancies.currency, '')
                    ) as salary,
                    vacancies.url
                FROM vacancies
                JOIN employers ON vacancies.employer_id = employers.id
            """)
            return [{
                'company': row[0],
                'title': row[1],
                'salary': row[2],
                'link': row[3]
            } for row in cur.fetchall()]

    def get_avg_salary(self) -> float:
        """
        Рассчитывает среднюю зарплату по вакансиям.

        :return: средняя зарплата (float)
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from + salary_to)/2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
            """)
            return round(float(cur.fetchone()[0]), 2)

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """
        Получает список вакансий с зарплатой выше средней.

        :return: список словарей в формате get_all_vacancies()
        """
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    employers.name, 
                    vacancies.name, 
                    CONCAT(vacancies.salary_from, ' - ', vacancies.salary_to, ' ', vacancies.currency),
                    vacancies.url
                FROM vacancies
                JOIN employers ON vacancies.employer_id = employers.id
                WHERE (vacancies.salary_from + vacancies.salary_to)/2 > %s
            """, (avg_salary,))
            return [{
                'company': row[0],
                'title': row[1],
                'salary': row[2],
                'link': row[3]
            } for row in cur.fetchall()]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """
        Ищет вакансии, в названии которых содержится ключевое слово.

        :param keyword: ключевое слово для поиска
        :return: список словарей в формате get_all_vacancies()
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    employers.name, 
                    vacancies.name, 
                    CONCAT(
                        COALESCE(vacancies.salary_from, 'Не указана'), ' - ', 
                        COALESCE(vacancies.salary_to, 'Не указана'), ' ', 
                        COALESCE(vacancies.currency, '')
                    ),
                    vacancies.url
                FROM vacancies
                JOIN employers ON vacancies.employer_id = employers.id
                WHERE vacancies.name ILIKE %s
            """, (f'%{keyword}%',))
            return [{
                'company': row[0],
                'title': row[1],
                'salary': row[2],
                'link': row[3]
            } for row in cur.fetchall()]

    def __del__(self):
        """Закрывает соединение при удалении объекта"""
        if hasattr(self, 'conn'):
            self.conn.close()