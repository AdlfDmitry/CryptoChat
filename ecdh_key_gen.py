from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def ecdh_key_gen():
    try:
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes_raw()

        return private_key, public_key_bytes
    except Exception as e:
        print(f"Key generation error: {e}")
        return None,None

def derive_aes_key(private_key, public_key):
    try:
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(public_key)

        shared_secret = private_key.exchange(peer_public_key)
        aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'cryptochat_handshake'
        ).derive(shared_secret)
        return aes_key
    except Exception as e:
        print(f"AES key derivation error: {e}")
        return None