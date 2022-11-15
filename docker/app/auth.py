import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import dotenv_values

config = dotenv_values(".env")


class AuthHandler():
    security = HTTPBearer()
    ctx = CryptContext(schemes=["sha256_crypt"])
    secret_key = config["SECRET_KEY"]

    def get_password_hash(self, pwd):
        return self.ctx.hash(pwd)

    def verify_password(self, pwd, hashed_pwd):
        return self.ctx.verify(pwd, hashed_pwd)

    def encode_token(self, user, type):
        payload = {
            # issued at
            "iat": datetime.utcnow(),
            # subject
            "sub": user
        }
        # Expiration time
        if type == "access":
            payload.update({"exp": datetime.utcnow()+timedelta(minutes=5)})
        elif type == "refresh":
            payload.update({"exp": datetime.utcnow()+timedelta(hours=2)})
        else:
            raise HTTPException(status_code=401, detail="Invalid type")
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms="HS256")
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)
