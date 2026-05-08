from db_connect import db_connect
from hash import hash_password, check_password
db_connection = db_connect()

def registration(username, password, pub_key):
    if db_connection is None:
        print("Database is disconnected")
        return False

    try:
        with db_connection.cursor() as cursor:
            insert_query = """
                           INSERT INTO users (username, password,pub_key)
                           VALUES (%s, %s, %s) RETURNING user_id; 
                           """
            user_data = (username, hash_password(password), pub_key)
            cursor.execute(insert_query, user_data)
            db_connection.commit()
            print(f"User {username} registered successfully.")
            return True

    except Exception as e:
        if db_connection:
            db_connection.rollback()
        print(f"Registration error: {e}")
        return False

def authentication(username, password,pub_key):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

        if result and check_password(password, result[0]):
            print(f"User {username} authenticated successfully.")
            with db_connection.cursor() as cursor:
                cursor.execute("UPDATE users SET pub_key = %s WHERE username = %s", (pub_key,username))
            db_connection.commit()
            print(f"User {username} authenticated successfully.")
            return True
        else:
            print(f"User {username} not authenticated, wrong password or username")
            return False

    except Exception as e:
        print(f"Error while authentication: {e}")
        return False

def get_user_key(username):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT pub_key FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"Error while getting user key: {e}")
        return None

def update_pub_key(username, pub_key):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("UPDATE users SET pub_key = %s WHERE username = %s", (pub_key,username))
            db_connection.commit()
    except Exception as e:
        print(f"Error while updating public user key: {e}")

def save_offline_message(sender,receiver,ciphertext,sender_pub_key):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            query = """INSERT INTO messages (sender, receiver, ciphertext, pub_key) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (sender, receiver, ciphertext, sender_pub_key))
            db_connection.commit()
    except Exception as e:
        if db_connection:
            db_connection.rollback()
        print(f"DB Error save offline msg: {e}")

def get_offline_message(username):
    if db_connection is None:
        print("Database is disconnected")
        return False
    try:
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT sender, ciphertext, pub_key FROM messages WHERE receiver = %s", (username,))
            messages = cursor.fetchall()
            cursor.execute("DELETE FROM messages WHERE receiver = %s", (username,))
            db_connection.commit()
            return messages

    except Exception as e:
        print(f"DB Error get offline msg: {e}")
        return []
