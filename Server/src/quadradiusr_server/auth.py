import base64
import hashlib
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from quadradiusr_server.config import AuthConfig
from quadradiusr_server.db.base import User, AccessToken
from quadradiusr_server.db.repository import Repository


class Auth:
    def __init__(self, config: AuthConfig, repository: Repository) -> None:
        self.config = config
        self.repository = repository

    async def login(self, username: str, password: bytes) -> Optional[User]:
        user_repository = self.repository.user_repository
        user: User = await user_repository.get_by_username(username)
        if not user:
            return None

        if self.is_password_valid(password, user.password_):
            return user
        else:
            return None

    async def issue_token(self, user: User) -> str:
        repo = self.repository.access_token_repository
        now = datetime.now(tz=timezone.utc)
        expires_at = now + (
            timedelta(seconds=self.config.token_exp)
            if self.config.token_exp > 0
            else timedelta(days=500))
        access_expires_at = now + (
            timedelta(seconds=self.config.token_access_exp)
            if self.config.token_access_exp > 0
            else timedelta(days=500))
        token = AccessToken(
            id_=str(uuid.uuid4()),
            user_=user,
            token_=self._random_token(),
            created_at_=now,
            accessed_at_=now,
            expires_at_=expires_at,
            access_expires_at_=access_expires_at,
        )
        await repo.add(token)
        return token.token_

    def _random_token(self):
        return str(uuid.uuid4())

    async def authenticate(self, token: str) -> Optional[User]:
        now = datetime.now(tz=timezone.utc)
        repo = self.repository.access_token_repository
        access_token: AccessToken = await repo.get(token)
        if access_token:
            access_token.accessed_at_ = now
            access_token.access_expires_at_ = now + timedelta(seconds=self.config.token_access_exp)
            return access_token.user_

    def _get_token_created_later_than(self):
        if self.config.token_exp <= 0:
            return None
        exp_delta = timedelta(seconds=self.config.token_exp)
        return datetime.now(tz=timezone.utc) - exp_delta

    def _get_token_accessed_later_than(self):
        if self.config.token_access_exp <= 0:
            return None
        access_exp_delta = timedelta(seconds=self.config.token_access_exp)
        return datetime.now(tz=timezone.utc) - access_exp_delta

    def __scrypt(self, password, salt):
        return hashlib.scrypt(
            password, salt=salt,
            n=self.config.scrypt_n,
            r=self.config.scrypt_r,
            p=self.config.scrypt_p)

    def hash_password(self, password: bytes) -> str:
        salt = os.urandom(16)
        hashed = self.__scrypt(password, salt)

        salt_b64 = base64.b64encode(salt).decode()
        hashed_b64 = base64.b64encode(hashed).decode()

        return f'{salt_b64}!{hashed_b64}'

    def is_password_valid(self, password: bytes, hash_: str) -> bool:
        [salt_b64, hashed_b64] = hash_.split('!', 2)
        salt = base64.b64decode(salt_b64)
        hashed = base64.b64decode(hashed_b64)
        return self.__scrypt(password, salt) == hashed
