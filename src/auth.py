import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta


class Authhandler():
    security = HTTPBearer()
    ctx = CryptContext(schemes=["sha256_crypt"])
    secret_key = "4aa771add5cf42f9ade97b260699172d6eb12efe9327a45621c0ac92c753c5d0"

    def get_password_hash(self, pwd):
        return self.ctx.hash(pwd)

    def verify_password(self, pwd, hashed_pwd):
        return self.ctx.verify(pwd, hashed_pwd)

    def encode_token(self, user):
        payload = {
            # expiration time
            "exp": datetime.utcnow() + timedelta(days=0, minutes=5),
            # issued at
            "iat": datetime.utcnow(),
            # subject
            "sub": user
        }
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
