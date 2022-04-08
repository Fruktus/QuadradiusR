.. _ws_notification:

Notifications
=============


``game.invite.accepted``
------------------------

A game invite has been accepted.

.. code-block:: json

    {
        "game_invite_id": "{id}",
        "game": {}
    }

See :ref:`rest_game` for data structures.


``game.invite.received``
------------------------

A game invite has been received.

.. code-block:: json

    {
        "game_invite": {}
    }

See :ref:`rest_game_invite` for data structures.


``game.invite.removed``
-----------------------

A game invite has been removed.

The ``reason`` may be one of:
``canceled``, ``expired``.

.. code-block:: json

    {
        "game_invite_id": "{id}",
        "reason": "{reason}"
    }


``lobby.joined``
----------------

Someone joined the lobby.

.. code-block:: json

    {
        "lobby_id": "{id}",
        "user": {}
    }

See :ref:`rest_user` for data structures.


``lobby.left``
--------------

Someone left the lobby.

.. code-block:: json

    {
        "lobby_id": "{id}",
        "user_id": "{user_id}"
    }
