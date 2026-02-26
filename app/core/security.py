# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from app.core.config import settings
# from passlib.context import CryptContext
# SECRET_KEY = settings.SECRET_KEY
# ALGORITHM = settings.ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(days=7)) 
#     to_encode.update({"exp": expire, "type": "refresh"})  

#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[settings.ALGORITHM])
#         return payload
#     except JWTError:
#         return None


from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings
from passlib.context import CryptContext

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: dict,
    roles: list[str] = [],
    scopes: list[str] = [],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "roles": roles,
        "scopes": scopes,  #  embed scopes
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token1(
    data: dict,
    roles: list[str] = [],
    permissions: list[str] = [],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "roles": roles,            #  embed roles
        "permissions": permissions #  embed permissions
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({
        "exp": expire,
        "type": "refresh"  #  mark as refresh token
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_email_verification_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": email, "exp": expire, "type": "email_verification"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(
        {"sub": email, "exp": expire, "type": "password_reset"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None