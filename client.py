import socket
from controls import register
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9999))

done = False
while not done:
    user = register()
    data = f"{user}"
    client.send(data.encode('utf-8'))