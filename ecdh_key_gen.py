from cryptography.hazmat.primitives.asymmetric import x25519

def ecdh_key_gen():
    try:
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes_raw()

        return private_key, public_key_bytes
    except Exception as e:
        print(f"Key generation error: {e}")
        return None,None