import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9999))
server.listen()

client, addr = server.accept()
done = False
while not done:
    msg = client.recv(1024).decode('utf-8')
    if not msg:
        break  # якщо клієнт відключився
    print(f"Отримано дані: {msg}")  # ОЦЕ виведеться в термінал
    if msg == 'quit':
        done = True
