close = False

def register():
    username = input("Enter login> ").lower()
    return username

def auth():
    username = input("Логін: ").lower()
    password = input("Пароль: ")
    return username, password

def register():
    username = input("Enter login> ").lower()
    return username



if __name__ == "__main__":

    close = False
    while not close:
        user_input = input("> ").lower().strip()
        match user_input:
            case "register":
                register()

            case "auth":
                auth()

            case "message":
                recipient = input("Кому: ").lower()
                text = input("Повідомлення: ")

            case "exit":
                close = True
                print("Exiting...")

            case _:
                print("ТИ шо довбойоб?!!")