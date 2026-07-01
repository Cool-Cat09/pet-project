import bcrypt

def hash_pass(password: str) -> bytes:
    """modify password to hash"""


    byted_pass = password.encode('utf-8')

    return bcrypt.hashpw(byted_pass, bcrypt.gensalt())


def check_pass(password: str, hashed_password: str | bytes | None) -> bool:
    """check string password and hashed password from database"""


    byted_pass = password.encode('utf-8')

    if isinstance(hashed_password, str):
        byted_hash: bytes = hashed_password.encode('utf-8')
    elif isinstance(hashed_password, bytes):
        byted_hash = hashed_password
    else:
        return False

    return bcrypt.checkpw(byted_pass, byted_hash)