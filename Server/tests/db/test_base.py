from unittest import TestCase

from quadradiusr_server.db.base import Lobby, clone_db_object, Game, User


class TestBase(TestCase):
    def test_clone_db_object(self):
        db_object = Lobby(id_='asd', name_='lobby_name')
        db_object_clone = clone_db_object(db_object)
        self.assertIsNot(db_object, db_object_clone)
        self.assertEqual(db_object.id_, db_object_clone.id_)
        self.assertEqual(db_object.name_, db_object_clone.name_)

    def test_clone_db_object_deep(self):
        db_object = Game(
            id_='game_id',
            player_a_id_='player_a_id',
            player_b_id_='player_b_id',
            expires_at_='expires_at',
            game_state_='game_state',
            player_a_=User(
                id_='user_id',
                username_='username',
                password_='password',
            ),
            player_b_=User(
                id_='user_id2',
                username_='username2',
                password_='password2',
            ),
        )
        db_object_clone = clone_db_object(db_object)
        self.assertIsNot(db_object, db_object_clone)
        self.assertEqual(db_object.id_, db_object_clone.id_)
        self.assertIsNot(db_object.player_a_, db_object_clone.player_a_)
        self.assertEqual(db_object.player_a_.id_, db_object_clone.player_a_.id_)

        db_object_clone_shallow = clone_db_object(db_object, deep=False)
        self.assertIsNot(db_object, db_object_clone_shallow)
        self.assertEqual(db_object.id_, db_object_clone_shallow.id_)
        self.assertIs(db_object.player_a_, db_object_clone_shallow.player_a_)
