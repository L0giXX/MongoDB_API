from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from dotenv import dotenv_values
from .models import AuthModel

config = dotenv_values("src/.env")

oauth2 = OAuth2PasswordBearer(tokenUrl="login")
ctx = CryptContext(schemes=["sha256_crypt"])
secret_key = config["SECRET_KEY"]
ALGORITHM = "HS256"


def verify_password(plain_password, hashed_password):
    return ctx.verify(plain_password, hashed_password)


def get_password_hash(password):
    return ctx.hash(password)


def register_user(db, data):
    if db.find_one({"username": data["username"]}):
        raise HTTPException(
            status_code=400, detail="Username already taken")
    if db.find_one({"email": data["email"]}):
        raise HTTPException(
            status_code=400, detail="Email already taken")
    try:
        validate_email(data["email"], check_deliverability=True)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    else:
        hashed_pwd = get_password_hash(data["password"])
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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if db.find_one({"username": user}):
        for x in db.find({"username": user}):
            tmp.append(x)
    else:
        raise credentials_exception
    if not verify_password(password, tmp[0]["password"]):
        raise credentials_exception
    else:
        return tmp[0]["username"]


def create_access_token(user):
    payload = {
        # issued at (CET)
        "iat": datetime.utcnow() + timedelta(hours=1),
        # expiration time (CET+2h)
        "exp": datetime.utcnow() + timedelta(hours=1) + timedelta(hours=2),
        # subject
        "sub": user
    }
    encoded_jwt = jwt.encode(
        payload, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if user is None:
            raise credentials_exception
        else:
            return user
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user: AuthModel = Depends(
    get_current_user)): return current_user


def change_password(db, user, password):
    tmp = []
    if get_user(db, user) == None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username")
    else:
        hashed_pw = get_password_hash(password)
        filter = {"username": user}
        db.update_one(filter, {"$set": {"password": hashed_pw}})
        for x in db.find(filter):
            tmp.append(x)
        return tmp
