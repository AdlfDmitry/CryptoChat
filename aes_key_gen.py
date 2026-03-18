import secrets
key = secrets.token_bytes(32)
key_hex = secrets.token_hex(32)
print(f"Ключ: {key_hex}")