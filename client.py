import socket
import json
def send_request(data_string):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 9999))
        client.send(data_string.encode('utf-8'))
        client.close()
    except ConnectionRefusedError:
        print("❌Connection refused")
    pass
def register(username, password):
    payload = {
        "action": "reg",
        "username": username,
        "password": password
    }
    data = json.dumps(payload)
    send_request(data)

def auth(username, password):
    payload = {
        "action": "auth",
        "username": username,
        "password": password
    }
    data = json.dumps(payload)
    send_request(data)

def quit():
    payload = {"action": "quit"}
    data = json.dumps(payload)
    send_request(data)
