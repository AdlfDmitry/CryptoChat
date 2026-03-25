from client import register, disconnect_server, auth, connect_to_server
if __name__ == "__main__":
    if connect_to_server():
        close = False
        while not close:
            user_input = input("> ").lower().strip()
            match user_input:
                case "reg":
                    username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    register(username, password)
                case "quit":
                    disconnect_server()
                    close = True
                case "auth":
                    username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    auth(username, password)
                case _:
                    if user_input != "":
                        print("Unknown command")
    else:
        print("Not connected")
