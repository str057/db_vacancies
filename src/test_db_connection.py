import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="hh_vacancies",
        user="postgres",
        password="8993106",  # Замените на реальный пароль
        options="-c client_encoding=UTF8",
    )
    print("Подключение успешно!")
except Exception as e:
    print(f"Ошибка подключения: {e}")
