import socket
from aes_key_gen import generate_key
from db_connect import db_connect
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9999))
server.listen()
key = generate_key()
db_connection = db_connect()
if key is not None and db_connection is not None:
    print("Server is running...")
    print(key)
    while True:
        client_socket, addr = server.accept()
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            print(f"Data received: {msg}")

            if msg == 'quit':
                print("Closing connection...")
                client_socket.close()
                continue
            action, username, password = msg.split(':')
            if action == "reg":
            #Написать запрос к БД для записи нового пользователя
                print(action)
            elif action == "auth":
            #Написать запрос к БД для авторизации
                print(action)
            else:
                print("Invalid action")
                client_socket.close()
        except Exception as e:
            print(f"Connection Error{e}")
            client_socket.close()
            continue
