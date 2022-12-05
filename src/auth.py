from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import dotenv_values
from .models import AuthModel

config = dotenv_values("src/.env")


oauth2 = OAuth2PasswordBearer(tokenUrl="login")
ctx = CryptContext(schemes=["sha256_crypt"])
secret_key = config["SECRET_KEY"]
algo = config["ALGORITHM"]


def verify_password(plain_password, hashed_password):
    return ctx.verify(plain_password, hashed_password)


def get_password_hash(password):
    return ctx.hash(password)


def register_user(db, user, pwd):
    if db.find_one({"username": user}):
        raise HTTPException(
            status_code=400, detail="Username bereits vergeben")
    else:
        hashed_pwd = get_password_hash(pwd)
        return hashed_pwd


def get_user(db, user):
    tmp = []
    if db.find_one({"username": user}):
        for x in db.find({"username": user}):
            tmp.append(x)
        return tmp[0]["username"]
    else:
        return None


def authenticate_user(db, user, password):
    tmp = []
    if db.find_one({"username": user}):
        for x in db.find({"username": user}):
            tmp.append(x)
    else:
        return False
    if not tmp[0]["password"]:
        return False
    if not verify_password(password, tmp[0]["password"]):
        return False
    else:
        return tmp[0]["username"]


def create_access_token(user):
    payload = {
        # issued at
        "iat": datetime.utcnow(),
        # expiration time
        "exp": datetime.utcnow() + timedelta(minutes=120),
        # subject
        "sub": user
    }
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algo)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])
        user = payload.get("sub")
        if user is None:
            raise credentials_exception
        else:
            return user
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user: AuthModel = Depends(get_current_user)):
    return current_user
