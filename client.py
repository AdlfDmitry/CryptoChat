import socket
import ssl
import threading
from network_utils import send_msg, recv_msg

client_socket = None

def receive_msg():
    #
    while True:
        try:
            data = recv_msg(client_socket)
            if not data:
                print("\n Connection lost")
                break

            if data.get("action") == "incoming_msg":
                sender = data["from"]
                text = data["text"]
                print(f"\n{sender}: {text}")
            else:
                info = data.get("info")
                print(f"\nServer info: {info}")
            print("> ", end="", flush=True)

        except Exception as e:
            print(f"\nConnection lost: {e}")
            break


def connect_to_server():
    #реализовать вывод в терминал ведомостей о используемом протоколе шифрования метод cipher() из библиотеки ssl tls 1.3
    #добавить вывод в терминал ведомостей о сертификате сервера .x501


    global client_socket
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.load_verify_locations('server.crt')

        client_socket = context.wrap_socket(raw_socket, server_hostname="localhost")
        client_socket.connect(("localhost", 9999))

        receive_thread = threading.Thread(target=receive_msg)
        receive_thread.daemon = True
        receive_thread.start()
        return True

    except ConnectionRefusedError:
        print("Connection refused")
        return False
    except ssl.SSLError as e:
        print(f"TLS Error (Certificate validation failed?): {e}")
        return False

def send_request(payload):
    try:
        if client_socket:
            send_msg(client_socket, payload)
    except Exception as e:
        print(f"Error while sending message: {e}")


def register(username, password):
    send_request({"action": "reg", "username": username, "password": password})


def auth(username, password):
    send_request({"action": "auth", "username": username, "password": password})


def disconnect_server():
    send_request({"action": "quit"})
    if client_socket:
        client_socket.close()


def write_message(dst_username, message, username):
    send_request({"action": "msg", "dst_username": dst_username, "src_username": username, "message": message})


def logout():
    send_request({"action": "logout"})