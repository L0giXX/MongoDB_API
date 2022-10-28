import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


class Authhandler():
    security = HTTPBearer()
    ctx = CryptContext(schemes=["sha256_crypt"])

    def hash_password(self, pwd):
        return self.ctx.hash(pwd)

    def verify_password(self, pwd, hashed_pwd):
        return self.ctx.verify(pwd, hashed_pwd)
