import bcrypt

def hash_password(password):
    input_bytes = password.encode("utf-8")
    hashed_bytes = bcrypt.hashpw(input_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def check_password(password, hashed_password):
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)