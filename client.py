import socket
import ssl
import threading
from network_utils import send_msg, recv_msg
from ecdh_key_gen import ecdh_key_gen, derive_aes_key, save_key_to_file, load_key_from_file
from crypto_utils import encrypt_data, decrypt_data

client_socket = None
logged_in_user = None
pending_user = None
my_private_key = None
fetched_pub_keys = {}
pub_key_event = threading.Event()
my_public_key_hex = None

def receive_msg():
    global logged_in_user, pending_user
    while True:
        try:
            data = recv_msg(client_socket)
            if not data:
                print("\nConnection lost")
                break
            if data.get("action") == "pub_key_response":
                fetched_pub_keys[data["target_user"]] = data["pub_key"]
                pub_key_event.set()

            elif data.get("action") == "incoming_msg":
                sender = data["from"]

                ciphertext_hex = data["ciphertext"]
                sender_pub_key_hex = data["sender_pub_key"]

                try:
                    aes_key = derive_aes_key(my_private_key,bytes.fromhex(sender_pub_key_hex))
                    plaintext_hex = decrypt_data(aes_key, bytes.fromhex(ciphertext_hex))
                    print(f"{sender}: {plaintext_hex}")
                except Exception as e:
                    print(f"Error while decrypting message from {sender}: {e}")
            else:
                info = data.get("info")

                if info in ["Authenticated successfully", "Registered successfully"]:
                    logged_in_user = pending_user
                elif info in ["Logged out successfully", "Disconnected successfully"]:
                    logged_in_user = None

                print(f"\nServer info: {info}")

        except Exception as e:
            print(f"\nConnection lost: {e}")
            break

def connect_to_server():
    global client_socket
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.load_verify_locations('server.crt')

        context.check_hostname = False

        client_socket = context.wrap_socket(raw_socket, server_hostname="localhost")
        client_socket.connect(("localhost", 9999))

        cipher = client_socket.cipher()
        print(f"Secure connection established.")
        print(f"TLS Protocol: {cipher[1]}")
        print(f"Cipher Suite: {cipher[0]}")

        cert = client_socket.getpeercert()
        if cert:
            print(f"Server Certificate received")
        else:
            print("No server certificate found")

        receive_thread = threading.Thread(target=receive_msg)
        receive_thread.daemon = True
        receive_thread.start()
        return True

    except ConnectionRefusedError:
        print("Connection refused")
        return False
    except ssl.SSLError as e:
        print(f"TLS Certificate validation failed: {e}")
        return False

def send_request(payload):
    try:
        if client_socket:
            send_msg(client_socket, payload)
    except Exception as e:
        print(f"Error while sending message: {e}")

def register(username, password):
    global pending_user, my_private_key, my_public_key_hex
    pending_user = username
    priv, pub = ecdh_key_gen()

    save_key_to_file(priv, username)

    my_private_key = priv
    my_public_key_hex = pub.hex()
    save_key_to_file(my_private_key, username)
    send_request({
        "action": "reg",
        "username": username,
        "password": password,
        "pub_key": pub.hex()
        })

def auth(username, password):
    global pending_user, my_private_key, my_public_key_hex
    pending_user = username
    priv, pub = load_key_from_file(username)

    if priv is None:
        print("Local private key not found")
        priv, pub = ecdh_key_gen()
        save_key_to_file(priv, username)

    my_private_key = priv
    my_public_key_hex = pub.hex()

    send_request({
        "action": "auth",
        "username": username,
        "password": password,
        "pub_key": pub.hex()
    })

def disconnect_server():
    send_request({"action": "quit"})
    if client_socket:
        client_socket.close()

def write_message(dst_username, message, username):
    global my_private_key, my_public_key_hex
    pub_key_event.clear()

    send_request({"action": "get_pub_key", "target_user": dst_username})

    if not pub_key_event.wait(timeout=5.0):
        print("Cannot get receiver pub_key")
        return
    target_pub_key_hex = fetched_pub_keys.get(dst_username)

    if not target_pub_key_hex:
        print("User or users key not found")
        return
    try:
        aes_key = derive_aes_key(my_private_key,bytes.fromhex(target_pub_key_hex))
        ciphertext_bytes =encrypt_data(aes_key,message)
    except Exception as e:
        print(f"Error while encrypting message: {e}")
        return

    send_request({
        "action": "msg",
        "dst_username": dst_username,
        "ciphertext": ciphertext_bytes.hex(),
        "sender_pub_key": my_public_key_hex,
        "message": message
    })

    priv, pub = ecdh_key_gen()
    my_private_key = priv
    my_public_key_hex = pub.hex()

    save_key_to_file(my_private_key, username)

    send_request({
        "action": "update_pub_key",
        "pub_key": my_public_key_hex
    })

def logout():
    send_request({
        "action": "logout"})