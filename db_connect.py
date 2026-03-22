import psycopg2
def db_connect():
    try:
        connection = psycopg2.connect(
            dbname="CryptochatDB",
            user="postgres",
            password="12345678",
            host="127.0.0.1",
            port="5432"
        )
        print("Database connection established.")
        return connection

    except Exception as e:
        print(f"Error while connecting to database: {e}")
        return None
