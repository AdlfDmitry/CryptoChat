import json

def send_msg(sock, data_dict):
    if data_dict.get("action") == "msg":
        if not data_dict.get("message") and not data_dict.get("ciphertext"):
            print("Cannot send an empty message.")
            return
        if data_dict.get("src_username") == data_dict.get("dst_username"):
            print("Cannot send messages to yourself.")
            return

    json_str = json.dumps(data_dict)
    payload = json_str.encode('utf-8')
    length_prefix = len(payload).to_bytes(4, byteorder='big')
    sock.sendall(length_prefix + payload)

def recv_exactly(sock, num_bytes):
    data = bytearray()
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

def recv_msg(sock):
    length_bytes = recv_exactly(sock, 4)
    if not length_bytes:
        return None
    msg_length = int.from_bytes(length_bytes, byteorder='big')

    if msg_length > 5 * 1024 * 1024:
        raise ValueError("Payload is too large!")

    payload = recv_exactly(sock, msg_length)
    if not payload:
        return None

    try:
        return json.loads(payload.decode('utf-8'))
    except Exception as e:
        print(f"JSON Decode Error: {e}")
        return None