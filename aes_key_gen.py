import secrets
def generate_key():
    try:
        key = secrets.token_bytes(32)
        print(f"AES key generated successfully")
        return key

    except Exception as e:
        print(f"Key generation failed",e)
        return None

