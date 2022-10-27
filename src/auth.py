import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


class Authhandler():
    security = HTTPBearer()
    ctx = CryptContext(schemes=["sha256_crypt"])

    def get_password_hash(self, password):
        return self.ctx.hash(password)
