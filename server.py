import socket
import threading
import ssl
from user_actions import registration, authentication, get_offline_message, save_offline_message, update_pub_key, get_user_key
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
            pub_key = data.get("pub_key")

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
                    if registration(username, password,pub_key):
                        current_user = username
                        active_users[current_user] = client_sock
                        send_msg(client_sock, {"info": "Registered successfully"})
                    else:
                        send_msg(client_sock, {"info": "Registration failed"})

            elif action == "auth":
                if current_user is not None:
                    send_msg(client_sock, {"info": "Already logged in"})
                else:
                    if authentication(username, password, pub_key):
                        send_msg(client_sock, {"info": "Authenticated successfully"})
                        current_user = username
                        active_users[current_user] = client_sock
                        offline_msgs = get_offline_message(current_user)
                        for msg in offline_msgs:
                            send_msg(client_sock,{
                                "action": "incoming_msg",
                                "from": msg[0],
                                "ciphertext": msg[1],
                                "sender_pub_key": msg[2]
                            })
                    else:
                        send_msg(client_sock, {"info": "Authentication failed"})

            elif action == "get_pub_key":
                if current_user in active_users:
                    target_user = data.get("target_user")
                    pub_key = get_user_key(target_user)
                    send_msg(client_sock,
                             {"action": "pub_key_response", "target_user": target_user, "pub_key": pub_key})
                else:
                    send_msg(client_sock, {"info": "An error occurred while getting target public key"})
            elif action == "update_pub_key":
                if current_user in active_users:
                    update_pub_key(current_user, data.get("pub_key"))

            elif action == "msg":
                if current_user:
                    dst_username = data.get("dst_username")
                    ciphertext = data.get("ciphertext")
                    sender_pub_key = data.get("sender_pub_key")

                    forward_data = {
                        "action": "incoming_msg",
                        "from": current_user,
                        "ciphertext": ciphertext,
                        "sender_pub_key": sender_pub_key
                    }

                    if dst_username in active_users:
                        dst_sock = active_users[dst_username]
                        send_msg(dst_sock, forward_data)
                    else:
                        save_offline_message(current_user,dst_username,ciphertext, sender_pub_key)
                        send_msg(client_sock, {"info": f"User {dst_username} is offline. Message securely stored"})
                else:
                    send_msg(client_sock, {"status": "error", "info": "Not authorized"})

        except Exception as ee:
            print(f"Error with {address}: {ee}")
            break

    if current_user in active_users:
        del active_users[current_user]
    client_sock.close()

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 9999))
    server.listen()
    host_ip, host_port = server.getsockname()
    secure_server = context.wrap_socket(server, server_side=True)

    print(f"Server is hosted at {host_ip}:{host_port}...")
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
