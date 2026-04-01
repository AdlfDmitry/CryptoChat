from client import register, disconnect_server, auth, connect_to_server, write_message, logout
if __name__ == "__main__":
    if connect_to_server():
        close = False
        username = None
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
                case "msg":
                    dst_username = input("Enter receiver user name> ").lower()
                    text = input("Enter message> ")
                    write_message(dst_username, text, username)
                case "logout":
                    logout()
                case _:
                    if user_input != "":
                        print("Unknown command")

    else:
        print("Not connected")
