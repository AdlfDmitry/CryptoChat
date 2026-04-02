import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
def encrypt_data(aes_key, plaintext_str):
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_str.encode('utf-8'), None)
    return nonce+ciphertext

def decrypt_data(aes_key, encrypted_data):
    aesgcm = AESGCM(aes_key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext_bytes.decode('utf-8')

def send_encrypted(sock, aes_key, data_dict):
    json_str = json.dumps(data_dict)
    encrypted_payload = encrypt_data(aes_key, json_str)

    length_prefix = len(encrypted_payload).to_bytes(4, byteorder='big')
    sock.sendall(length_prefix + encrypted_payload)

def recv_encrypted(sock, aes_key):
    length_bytes = recv_exactly(sock, 4)
    if not length_bytes:
        return None
    msg_length = int.from_bytes(length_bytes, byteorder='big')

    encrypted_payload = recv_exactly(sock, msg_length)
    if not encrypted_payload:
        return None

    try:
        json_str = decrypt_data(aes_key, encrypted_payload)
        return json.loads(json_str)
    except Exception as e:
        print(f"Decryption Error: {e}")
        return None

def recv_exactly(sock, num_bytes):
    data = bytearray()
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)