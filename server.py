import socket
import threading
from user_actions import registration, authentication
from ecdh_key_gen import ecdh_key_gen,derive_aes_key
from crypto_utils import send_encrypted, recv_encrypted
active_users = {}

def handle_client(client_sock, address):
    current_user = None
    aes_key = None
    print(f"Connection established with {address} ")

    try:
        private_key, public_key = ecdh_key_gen()
        client_pub_bytes = client_sock.recv(32)
        client_sock.sendall(public_key)

        if len(client_pub_bytes) ==32:
            aes_key = derive_aes_key(private_key, client_pub_bytes)
        else:
            raise ValueError("Invalid key length")

    except Exception as e:
        print(f"Handshake failed with {address}: {e}")
        client_sock.close()
        return

    while True:
        try:
            data = recv_encrypted(client_sock, aes_key)
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
                send_encrypted(client_sock, aes_key, {"info": "Disconnected successfully"})
                current_user = None
                break

            elif action == "logout":
                if current_user in active_users:
                    del active_users[current_user]
                send_encrypted(client_sock, aes_key, {"info": "Logged out successfully"})
                current_user = None

            elif action == "reg":
                if current_user is not None:
                    send_encrypted(client_sock, aes_key, {"info": "Already logged in"})
                    print(f"Client {address} already logged in")
                else:
                    if registration(username, password):
                        current_user = username
                        active_users[current_user] = {"sock": client_sock, "key": aes_key}
                        send_encrypted(client_sock, aes_key, {"info": "Registered successfully"})
                    else:
                        send_encrypted(client_sock, aes_key, {"info": "Registration failed"})

            elif action == "auth":
                if current_user is not None:
                    send_encrypted(client_sock, aes_key, {"info": "Already logged in"})
                    print(f"Client {address} already logged in")
                else:
                    try:
                        if authentication(username, password):
                            send_encrypted(client_sock, aes_key, {"info": "Authenticated successfully"})
                            current_user = username
                            active_users[current_user] = {"sock": client_sock, "key": aes_key}
                        else:
                            send_encrypted(client_sock, aes_key, {"info": "Authentication failed"})
                    except Exception as e:
                        print(f"Error with {address} authentication : {e}")
                        send_encrypted(client_sock, aes_key, {"info": "Authentication failed"})

            elif action == "msg":
                if current_user:
                    dst_username = data.get("dst_username")
                    message_text = data.get("message")

                    if dst_username in active_users:
                        dst_data = active_users[dst_username]
                        dst_sock = dst_data["sock"]
                        dst_key = dst_data["key"]

                        forward_data = {
                            "action": "incoming_msg",
                            "from": current_user,
                            "text": message_text
                        }
                        send_encrypted(dst_sock, dst_key, forward_data)
                    else:
                        send_encrypted(client_sock, aes_key, {"status": "error", "info": "User is offline"})
                else:
                    send_encrypted(client_sock, aes_key, {"status": "error", "info": "Not authorized"})
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
