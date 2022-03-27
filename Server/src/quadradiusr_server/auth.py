import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from quadradiusr_server.config import AuthConfig


class User:
    def __init__(self, id_: str) -> None:
        self._id = id_

    @property
    def id_(self):
        return self._id

    def to_json(self):
        return {
            'id': self.id_,
        }

    @classmethod
    def from_json(cls, json):
        return User(json['id'])


class Auth:
    def __init__(self, config: AuthConfig) -> None:
        self.config = config
        self.__secret = str(uuid.uuid4())
        self.__algorithm = 'HS256'

    def issue_token(self, user: User) -> str:
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(seconds=self.config.token_exp)
        token_data = {
            'exp': exp,
            'iat': now,
            'nbf': now,
            'usr': user.to_json(),
        }
        return jwt.encode(
            token_data,
            self.__secret,
            algorithm=self.__algorithm,
        )

    def authenticate(self, token: str) -> Optional[User]:
        try:
            decoded = jwt.decode(
                token,
                self.__secret,
                algorithms=[self.__algorithm],
                leeway=self.config.token_leeway,
                options={'require': ['exp', 'iat', 'nbf', 'usr']},
            )
            return User.from_json(decoded['usr'])
        except jwt.InvalidTokenError:
            return None
