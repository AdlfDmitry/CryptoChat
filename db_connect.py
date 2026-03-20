import psycopg2

try:
    connection = psycopg2.connect(
        dbname="CryptochatDB",
        user="postgres",
        password="12345678",
        host="127.0.0.1",
        port="5432"
    )
    print("Підключення успішне!")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users;")
    record = cursor.fetchall()
    print(f"{record}")

except Exception as error:
    print(f"Помилка при роботі з PostgreSQL: {error}")

finally:
    if connection:
        cursor.close()
        connection.close()
        print("З'єднання з базою даних закрито.")