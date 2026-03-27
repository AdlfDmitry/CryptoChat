import psycopg2
from connect_conf import dbname, user, password, host, port

def db_connect():
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print("Database connection established.")
        return connection

    except Exception as e:
        print(f"Error while connecting to database: {e}")
        return None