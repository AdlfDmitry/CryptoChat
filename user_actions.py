from db_connect import db_connect
db_connection = db_connect()
from hash import evaluate_hash
def registration(username,password,address):
    if db_connection is not None:
        print(f"User registration: {username}")
    try:
            with db_connection.cursor() as cursor:
                insert_query = """
                               INSERT INTO users (username, password, last_seen_ip)
                               VALUES (%s, %s, %s) RETURNING user_id; 
                               """
                user_data = (username, evaluate_hash(password), address)
                cursor.execute(insert_query, user_data)
                db_connection.commit()
    except Exception as e:
        print(f"Error while connecting to database: {e}")
    return None


def authentication(username,password):
    if db_connection is not None:
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                result = cursor.fetchone()
            if result and result[0] == evaluate_hash(password):
                print(f"User {username} authenticated")
            else:
                print(f"User {username} not authenticated, wrong password or username")
        except Exception as e:
            print(f"Error while connecting to database: {e}")
