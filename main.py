from bcrypt import gensalt,hashpw,checkpw

def hash_password(password):
    password_enc = password.encode()
    salt = gensalt()
    hash_password = hashpw(password_enc,salt)
    return hash_password

def verify_password(password, input_password) -> bool:
    input_password_enc = input_password.encode()
    return checkpw(input_password_enc,password)

print("Здравствуйте! Это программа для хэширования и проверки вашего пароля.")

password = input("Введите ваш пароль: ")
hashed_password = hash_password(password)

print("Давайте проверим ваш пароль.")
password_check = input("Введите пароль повторно: ")

if verify_password(hashed_password,password_check) == True:
    print(f"Ваш пароль верный! Ваш хэшированный пароль: {hashed_password}")
else:
    print("Ваш пароль не верный.")