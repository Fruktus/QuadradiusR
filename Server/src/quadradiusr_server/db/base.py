from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, DateTime, String, PickleType, TypeDecorator, Integer
from sqlalchemy.orm import declarative_base, relationship, class_mapper

Base = declarative_base()


def clone_db_object(obj, deep=True):
    clazz = type(obj)
    attrs = [p.key for p in class_mapper(clazz).iterate_properties]
    props = {}
    for attr in attrs:
        prop = getattr(obj, attr)
        if deep and isinstance(prop, Base):
            prop = clone_db_object(prop, deep=True)
        props[attr] = prop
    return clazz(**props)


# noinspection PyAbstractClass
class DateTimeUTC(TypeDecorator):
    impl = DateTime
    cache_ok = True
    LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            raise ValueError('Tried to bind datetime without tz')

        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)


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

    @property
    def friendly_name(self):
        return f'{self.username_} ({self.id_})'


class GameInvite(Base):
    __tablename__ = 'game_invite'
    id_ = Column(String, nullable=False, primary_key=True)
    from_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    subject_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    expires_at_ = Column(DateTimeUTC, nullable=False)

    from_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[from_id_])
    subject_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[subject_id_])

    def get_other_player(self, this_player: User) -> User:
        if self.from_id_ == this_player.id_:
            return self.subject_
        elif self.subject_id_ == this_player.id_:
            return self.from_
        else:
            raise ValueError(
                f'User {this_player} does not participate in this invite')

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
    rev_ = Column(Integer, nullable=False)
    player_a_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    player_b_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    expires_at_ = Column(DateTimeUTC, nullable=False)
    game_state_ = Column(PickleType, nullable=False)

    player_a_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[player_a_id_])
    player_b_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[player_b_id_])

    __mapper_args__ = {
        'version_id_col': rev_
    }

    def get_other_player_id(self, player_id):
        ids = {self.player_a_id_, self.player_b_id_}
        ids.remove(player_id)
        return list(ids)[0]

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'player_a_id_={self.player_a_id_!r}' \
            f'player_b_id_={self.player_b_id_!r}' \
            f')'


class Lobby(Base):
    __tablename__ = 'lobby'
    id_ = Column(String, nullable=False, primary_key=True)
    name_ = Column(String, nullable=False)

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'name_={self.name_!r}' \
            f')'


class LobbyMessage(Base):
    __tablename__ = 'lobby_message'
    id_ = Column(String, nullable=False, primary_key=True)
    user_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    lobby_id_ = Column(String, ForeignKey('lobby.id_'), nullable=False)
    content_ = Column(String, nullable=False)
    created_at_ = Column(DateTimeUTC, nullable=False)

    user_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[user_id_])
    lobby_ = relationship(
        'Lobby',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[lobby_id_])

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'user_id_={self.user_id_!r}' \
            f'lobby_id_={self.lobby_id_!r}' \
            f'content_={self.content_!r}' \
            f'created_at_={self.created_at_!r}' \
            f')'


class AccessToken(Base):
    __tablename__ = 'access_token'
    id_ = Column(String, nullable=False, primary_key=True)
    user_id_ = Column(String, ForeignKey('user.id_'), nullable=False)
    token_ = Column(String, nullable=False)
    created_at_ = Column(DateTimeUTC, nullable=False)
    accessed_at_ = Column(DateTimeUTC, nullable=False)

    user_ = relationship(
        'User',
        lazy='joined',
        cascade='expunge',
        foreign_keys=[user_id_])

    def __repr__(self):
        return \
            f'{type(self).__name__}(' \
            f'id_={self.id_!r}, ' \
            f'user_id_={self.user_id_!r}' \
            f'token_id_={self.token_!r}' \
            f'created_at_={self.created_at_!r}' \
            f'accessed_at_={self.accessed_at_!r}' \
            f')'
