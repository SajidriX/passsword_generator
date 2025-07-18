from bcrypt import gensalt, hashpw, checkpw

def hash_password(password: str):
    password_enc = password.encode('utf-8')
    salt = gensalt()
    hashed_password = hashpw(password_enc, salt)
    return hashed_password.decode('utf-8')  

def verify_password(hashed_password: str, input_password: str) -> bool:
    try:
        return checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False