import socket
import threading
import ssl
from user_actions import registration, authentication
from network_utils import send_msg, recv_msg

active_users = {}


def handle_client(client_sock, address):
    current_user = None
    print(f"Secure connection established with {address}\n")

    while True:
        try:
            data = recv_msg(client_sock)
            if not data:
                print(f"Client {address} disconnected")
                break

            action = data.get("action")
            username = data.get("username")
            password = data.get("password")

            if action == 'quit':
                print(f"Client {address} disconnected manually")
                if current_user in active_users:
                    del active_users[current_user]
                send_msg(client_sock, {"info": "Disconnected successfully"})
                break

            elif action == "logout":
                if current_user in active_users:
                    del active_users[current_user]
                send_msg(client_sock, {"info": "Logged out successfully"})
                current_user = None

            elif action == "reg":
                if current_user is not None:
                    send_msg(client_sock, {"info": "Already logged in"})
                else:
                    if registration(username, password):
                        current_user = username
                        active_users[current_user] = client_sock
                        send_msg(client_sock, {"info": "Registered successfully"})
                    else:
                        send_msg(client_sock, {"info": "Registration failed"})

            elif action == "auth":
                if current_user is not None:
                    send_msg(client_sock, {"info": "Already logged in"})
                else:
                    if authentication(username, password):
                        send_msg(client_sock, {"info": "Authenticated successfully"})
                        current_user = username
                        active_users[current_user] = client_sock
                    else:
                        send_msg(client_sock, {"info": "Authentication failed"})

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
                        send_msg(dst_sock, forward_data)
                    else:
                        send_msg(client_sock, {"status": "error", "info": "User is offline"})
                else:
                    send_msg(client_sock, {"status": "error", "info": "Not authorized"})

        except ConnectionResetError:
            print(f"Connection with {address} was reset")
            break
        except Exception as e:
            print(f"Error with {address}: {e}")
            break

    if current_user in active_users:
        del active_users[current_user]
    client_sock.close()


if __name__ == "__main__":
    #добавить вывод айпи и порта на котором происходит хост
    #реализовать изменение ключей после каждого сообщения
    #реализовать сохранение сообщений на сервере которые были отправлены офлайн пользователю
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 9999))
    server.listen()

    secure_server = context.wrap_socket(server, server_side=True)

    print("Secure Server (TLS 1.3) is running...")
    while True:
        try:
            client_socket, addr = secure_server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
            print(f"Used encryption with {addr} : {client_socket.cipher()}")
            print(f"Active connections: {threading.active_count() - 1}")

        except ssl.SSLError as e:
            print(f"TLS handshake failed: {e}")
