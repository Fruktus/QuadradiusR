import base64
import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from quadradiusr_server.config import AuthConfig
from quadradiusr_server.db.base import User
from quadradiusr_server.db.repository import Repository


class Auth:
    def __init__(self, config: AuthConfig, repository: Repository) -> None:
        self.config = config
        self.repository = repository
        self.__secret = str(uuid.uuid4())
        self.__algorithm = 'HS256'

    async def login(self, username: str, password: bytes) -> Optional[User]:
        user_repository = self.repository.user_repository
        user: User = await user_repository.get_by_username(username)
        if not user:
            return None

        if is_password_valid(password, user.password_):
            return user
        else:
            return None

    def issue_token(self, user: User) -> str:
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(seconds=self.config.token_exp)
        token_data = {
            'exp': exp,
            'iat': now,
            'nbf': now,
            'usr': {
                'id': user.id_,
            },
        }
        return jwt.encode(
            token_data,
            self.__secret,
            algorithm=self.__algorithm,
        )

    def authenticate(self, token: str) -> Optional[str]:
        try:
            decoded = jwt.decode(
                token,
                self.__secret,
                algorithms=[self.__algorithm],
                leeway=self.config.token_leeway,
                options={'require': ['exp', 'iat', 'nbf', 'usr']},
            )
            return decoded['usr'].get('id')
        except jwt.InvalidTokenError:
            return None

    async def get_user(self, user_id: str) -> Optional[User]:
        return await self.repository.user_repository.get_by_id(user_id)


def __scrypt(password, salt):
    return hashlib.scrypt(password, salt=salt, n=16 * 1024, r=8, p=1)


def hash_password(password: bytes) -> str:
    salt = os.urandom(16)
    hashed = __scrypt(password, salt)

    salt_b64 = base64.b64encode(salt).decode()
    hashed_b64 = base64.b64encode(hashed).decode()

    return f'{salt_b64}!{hashed_b64}'


def is_password_valid(password: bytes, hash_: str) -> bool:
    [salt_b64, hashed_b64] = hash_.split('!', 2)
    salt = base64.b64decode(salt_b64)
    hashed = base64.b64decode(hashed_b64)
    return __scrypt(password, salt) == hashed
