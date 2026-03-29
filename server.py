import socket
import json
import threading
from user_actions import registration, authentication
from ecdh_key_gen import ecdh_key_gen
active_users = {}

def handle_client(client_sock, address):
    current_user = None
    print(f"Connection established with {address} ")
    try:
        private_key, public_key = ecdh_key_gen()
        client_pub_bytes = client_sock.recv(32)
        print(client_pub_bytes)
        client_sock.sendall(public_key)
    except ConnectionResetError:
        print(f"Connection with {address} was closed")
        return

    if len(client_pub_bytes) < 32:
        print(f"Failed to receive key from {address}")
        client_sock.close()
        return

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

            elif action == "logout":
                if current_user in active_users:
                    del active_users[current_user]
                client_sock.sendall(json.dumps({"info": "Logged out successfully"}).encode('utf-8'))
                current_user = None

            elif action == "reg":
                if current_user is not None:
                    client_sock.sendall(json.dumps({"info": "Already logged in"}).encode('utf-8'))
                    print(f"Client {address} already logged in")
                else:
                    try:
                        if registration(username, password):
                            current_user = username
                            active_users[current_user] = client_sock
                            client_sock.sendall(json.dumps({"info": "Registered successfully"}).encode('utf-8'))
                    except Exception as e:
                        print(f"Error with {address} registration : {e}")
                        client_sock.sendall(json.dumps({"info": "Registration failed"}).encode('utf-8'))

            elif action == "auth":
                if current_user is not None:
                    client_sock.sendall(json.dumps({"info": "Already logged in"}).encode('utf-8'))
                    print(f"Client {address} already logged in")
                else:
                    try:
                        if authentication(username, password):
                            client_sock.sendall(json.dumps({"info": "Authenticated successfully"}).encode('utf-8'))
                            current_user = username
                            active_users[current_user] = client_sock

                    except Exception as e:
                        print(f"Error with {address} authentication : {e}")
                        client_sock.sendall(json.dumps({"info": "Authenticated failed"}).encode('utf-8'))

            elif action == "msg":
                if current_user:
                    dst_username = data.get("dst_username")
                    message_text = data.get("message")
                    if dst_username in active_users:
                        dst_sock = active_users[dst_username]
                        forward_data = {
                            "action": "incoming_msg",
                            "from": current_user,
                            "text": message_text
                        }
                        dst_sock.sendall(json.dumps(forward_data).encode('utf-8'))
                    else:
                        client_sock.sendall(json.dumps({"status": "error", "info": "User is offline"}).encode('utf-8'))
                else:
                    client_sock.sendall(json.dumps({"status": "error", "info": "Not authorized"}).encode('utf-8'))
                    print(f"Client {address} is not authorized")

        except ConnectionResetError:
            print(f"Connection with {address} was closed")
            break
        except Exception as e:
            print(f"Error with {address}: {e}")
            break
    if current_user in active_users:
        del active_users[current_user]
    client_sock.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 9999))
    server.listen()
    print("Server is running...")
    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target = handle_client, args = (client_socket, addr))
        client_thread.start()

        print(f"Active connections: {threading.active_count() - 1}")
