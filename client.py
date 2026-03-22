import socket
def send_request(data_string):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 9999))
        client.send(data_string.encode('utf-8'))
        client.close()
    except ConnectionRefusedError:
        print("Connection refused")

def register(username, password):
    data = f"reg:{username}:{password}"
    send_request(data)

def auth(username, password):
    data = f"auth:{username}:{password}"
    send_request(data)

def quit():
    send_request("quit")
def start(key_pub):
    send_request(key_pub)