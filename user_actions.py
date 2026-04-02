from db_connect import db_connect
from hash import hash_password, check_password
db_connection = db_connect()


def registration(username, password):
    if db_connection is None:
        print("Database is disconnected")
        return False

    try:
        with db_connection.cursor() as cursor:
            insert_query = """
                           INSERT INTO users (username, password)
                           VALUES (%s, %s) RETURNING user_id; 
                           """
            user_data = (username, hash_password(password))
            cursor.execute(insert_query, user_data)
            db_connection.commit()
            print(f"User {username} registered successfully.")
            return True

    except Exception as e:
        if db_connection:
            db_connection.rollback()
        print(f"Registration error: {e}")
        return False

def authentication(username, password):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

        if result and check_password(password, result[0]):
            print(f"User {username} authenticated successfully.")
            return True
        else:
            print(f"User {username} not authenticated, wrong password or username")
            return False

    except Exception as e:
        print(f"Error while authentication: {e}")
        return False

