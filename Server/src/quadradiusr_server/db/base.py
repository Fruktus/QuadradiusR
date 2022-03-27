from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DbUser(Base):
    __tablename__ = 'user'
    id_ = Column(String, primary_key=True)
    username_ = Column(String, unique=True)
    password_ = Column(String)

    def __repr__(self):
        return \
            f'User(' \
            f'id_={self.id_!r}, ' \
            f'username_={self.username_!r}' \
            f')'