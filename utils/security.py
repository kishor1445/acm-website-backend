from passlib.context import CryptContext

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_(password: str):
    return pass_context.hash(password)


def verify(password: str, hashed_password: str):
    return pass_context.verify(password, hashed_password)
