import time
import client
from client import register, disconnect_server, auth, connect_to_server, write_message, logout
if __name__ == "__main__":
    if connect_to_server():
        close = False
        while not close:
            time.sleep(0.25)
            prompt_text = f"{client.logged_in_user}> " if client.logged_in_user else "> "
            user_input = input(prompt_text).lower().strip()
            match user_input:
                case "reg":
                    req_username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    register(req_username, password)
                case "quit":
                    disconnect_server()
                    close = True
                case "auth":
                    req_username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    auth(req_username, password)
                case "msg":
                    if not client.logged_in_user:
                        print("Please authenticate first.")
                        continue
                    dst_username = input("Enter receiver user name> ").lower()
                    text = input("Enter message> ")
                    write_message(dst_username, text, client.logged_in_user)
                case "logout":
                    logout()
                case _:
                    if user_input != "":
                        print("Unknown command")

    else:
        print("Not connected")