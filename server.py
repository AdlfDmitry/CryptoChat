import socket
import json
import threading
from user_actions import *

def handle_client(client_sock, address):
    authorized = False
    print(f"Connection established with {address} ")
    while True:
        try:
            msg = client_sock.recv(1024).decode('utf-8')
            if not msg:
                print(f"Client {address} disconnected")
                break

            print(f"Received data from  {address}: {msg}")
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                print("Wrong data format")
                continue

            action = data.get("action")
            username = data.get("username")
            password = data.get("password")

            if action == 'quit':
                print(f"Client {address} disconnected manually")
                break

            elif action == "reg":
                try:
                    registration(username, password, address[0])
                except Exception as e:
                    print(f"Error with {address} registration : {e}")

            elif action == "auth":
                try:
                    authentication(username, password)
                except Exception as e:
                    print(f"Error with {address} authentication : {e}")

        except ConnectionResetError:
            print(f"Connection with {address} was closed")
            break
        except Exception as e:
            print(f"Error with {address}: {e}")
            break
    client_sock.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen()
    print("Server is running...")
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target= handle_client, args=(client_socket, addr))
        client_thread.start()

        print(f"Active connections: {threading.active_count() - 1}")