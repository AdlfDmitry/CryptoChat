from client import register, quit, auth, start
from ecdh_key_gen import ecdh_key_gen
if __name__ == "__main__":
    key_pub,key_private = ecdh_key_gen()
    if key_pub is not None and key_private is not None:
        start(key_pub)
        close = False
        while not close:
            user_input = input("> ").lower().strip()
            match user_input:
                case "reg":
                    username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    register(username,password)
                case "quit":
                    quit()
                    close = True
                case "auth":
                    username = input("Enter login> ").lower()
                    password = input("Enter password> ")
                    auth(username, password)
                case _:
                    print("!!")
else:
    print("missing keys")
    close = True
