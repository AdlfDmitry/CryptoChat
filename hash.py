import bcrypt
def evaluate_hash(string):
    input_string = string.encode("utf-8")
    hashed_string = bcrypt.hashpw(input_string, bcrypt.gensalt())
    return hashed_string