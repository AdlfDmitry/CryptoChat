import socket
import threading
from ecdh_key_gen import ecdh_key_gen, derive_aes_key
from crypto_utils import send_encrypted, recv_encrypted
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
private_key, public_key = ecdh_key_gen()
aes_key = None

def receive_msg():
    while True:
        try:
            data = recv_encrypted(client_socket, aes_key)
            if not data:
                print("\n Connection lost")
                break

            if data.get("action") == "incoming_msg":
                sender = data["from"]
                text = data["text"]
                print(f"{sender}: {text}")

            else:
                info = data.get("info")
                print(f"Server info: {info}")
            print("> ", end="", flush=True)

        except Exception as e:
            print(f"\nConnection lost: {e}")
            break

def send_ecdh_key():
    client_socket.sendall(public_key)

def get_ecdh_key():
    server_pub_bytes = client_socket.recv(32)
    return server_pub_bytes

def connect_to_server():
    global aes_key
    try:
        client_socket.connect(("localhost", 9999))
        send_ecdh_key()
        server_key = get_ecdh_key()

        if server_key and len(server_key) == 32:
            aes_key = derive_aes_key(private_key, server_key)
        else:
            print("Handshake failed")
            return False

        receive_thread = threading.Thread(target=receive_msg)
        receive_thread.daemon = True
        receive_thread.start()
        return True

    except ConnectionRefusedError:
        print("Connection refused")
        return False

def send_request(payload):
    try:
        if aes_key:
            send_encrypted(client_socket, aes_key, payload)
    except Exception as e:
        print(f"Error while sending message: {e}")

def register(username, password):
    send_request({"action": "reg", "username": username, "password": password})

def auth(username, password):
    send_request({"action": "auth", "username": username, "password": password})

def disconnect_server():
    send_request({"action": "quit"})
    client_socket.close()

def write_message(dst_username, message, username):
    try:
        send_request({"action": "msg", "dst_username": dst_username , "src_username":username, "message":message })
    except Exception as e:
        print(f"Error while sending message: {e}")

def logout():
    send_request({"action": "logout"})