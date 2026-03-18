from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

private_key = x25519.X25519PrivateKey.generate()

public_key = private_key.public_key()

private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print("Приватный ключ (PEM):")
print(private_bytes.decode())
print("Публичный ключ (PEM):")
print(public_bytes.decode())