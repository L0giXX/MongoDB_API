from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from .models import AuthModel


SECRET_KEY = "4aa771add5cf42f9ade97b260699172d6eb12efe9327a45621c0ac92c753c5d0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username):
    tmp = []
    if db.find_one({"username": username}):
        for x in db.find({"username": username}):
            tmp.append(x)
        return tmp[0]["username"]
    else:
        return None


def authenticate_user(db, username, password):
    tmp = []
    if db.find_one({"username": username}):
        for x in db.find({"username": username}):
            tmp.append(x)
    else:
        return False
    if not tmp[0]["password"]:
        return False
    if not verify_password(password, tmp[0]["password"]):
        return False
    else:
        return tmp[0]["username"]


def create_access_token(username):
    payload = {
        # issued at
        "iat": datetime.utcnow(),
        # expiration time
        "exp": datetime.utcnow() + timedelta(minutes=120),
        # subject
        "sub": username
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: AuthModel = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
