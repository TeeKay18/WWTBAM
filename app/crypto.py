from cryptography.fernet import Fernet

secret_key = "only_main_developer_knows"


def load_key():
    return secret_key.encode()


def decryption(msg: str) -> str:
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(msg)
    return str(decrypted_message.decode())


def encryption(msg: str) -> str:
    key = load_key()
    encoded_message = msg.encode()
    f = Fernet(key)
    return f.encrypt(encoded_message)


"""
def write_to_file() -> None:
    questions = Game._get_questions_file_content()
    generate_key()
    copy_path = Path("app") / "questions" / "questions_copy.txt"
    with open(copy_path, "w") as f:
        f.write(str(encrypt(questions)))
"""
