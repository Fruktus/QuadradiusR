from sqlalchemy import Column, ForeignKey, DateTime, String, PickleType
from sqlalchemy.orm import declarative_base, relationship

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


class GameInvite(Base):
    __tablename__ = 'game_invite'
    id_ = Column(String, nullable=False, primary_key=True)
    from_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    subject_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    expiration_ = Column(DateTime, nullable=False)

    from_ = relationship(
        'User',
        foreign_keys=[from_id_])
    subject_ = relationship(
        'User',
        foreign_keys=[subject_id_])

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'from_id_={self.from_id_!r}' \
            f'subject_id_={self.subject_id_!r}' \
            f')'


class Game(Base):
    __tablename__ = 'game'
    id_ = Column(String, nullable=False, primary_key=True)
    player_a_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    player_b_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    expiration_ = Column(DateTime, nullable=False)
    game_data_ = Column(PickleType, nullable=False)

    player_a_ = relationship(
        'User',
        foreign_keys=[player_a_id_])
    player_b_ = relationship(
        'User',
        foreign_keys=[player_b_id_])

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'player_a_id_={self.player_a_id_!r}' \
            f'player_b_id_={self.player_b_id_!r}' \
            f')'
