import socket
import json
import threading

def handle_client(client_socket, addr):

    print(f"Connection established with {addr} ")
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if not msg:
                print(f"Client {addr} disconnected")
                break

            print(f"Received data from  {addr}: {msg}")
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                print("Wrong data format")
                continue

            action = data.get("action")
            username = data.get("username")
            password = data.get("password")

            if action == 'quit':
                print(f"Client {addr} disconnected manually")
                break
            elif action == "reg":
                print(f"User registration: {username}")
            elif action == "auth":
                print(f"User authorization: {username}")
            else:
                print(f"Unknown action from {addr}")

        except ConnectionResetError:
            print(f"Connection with {addr} was closed")
            break
        except Exception as e:
            print(f"Error with {addr}: {e}")
            break
    client_socket.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen()
    print("Server is running...")
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

        print(f"Active connections: {threading.active_count() - 1}")