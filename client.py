import socket
import json
import threading
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def receive_msg():
    while True:
        try:
            msg = client_socket.recv(1024).decode("utf-8")
            if not msg:
                print("\n Connection lost")
                break
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                print("\nWrong data format")
                continue

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


def connect_to_server():
    try:
        client_socket.connect(("localhost", 9999))
        print("Connection established")
        receive_thread = threading.Thread(target=receive_msg)
        receive_thread.daemon = True
        receive_thread.start()
        return True
    except ConnectionRefusedError:
        print("Connection refused")
        return False

def send_request(payload):
    try:
        data = json.dumps(payload)
        client_socket.send(data.encode('utf-8'))
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