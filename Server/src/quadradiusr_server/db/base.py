from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id_ = Column(String, nullable=False, primary_key=True)
    username_ = Column(String, nullable=False, unique=True)
    password_ = Column(String, nullable=False)

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'username_={self.username_!r}' \
            f')'
