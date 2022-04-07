.. _ws_notification:

Notifications
=============

+----------------------------------------+----------------------------------+
| Topic and message                      |           Description            |
+========================================+==================================+
| .. code-block:: json                   | A game invite has been accepted. |
|     :caption: ``game.invite.accepted`` |                                  |
|                                        |                                  |
|     {                                  |                                  |
|         "game_invite_id": "{id}",      |                                  |
|         "game_id": "{game_id}"         |                                  |
|     }                                  |                                  |
+----------------------------------------+----------------------------------+
| .. code-block:: json                   | A game invite has been received. |
|     :caption: ``game.invite.received`` |                                  |
|                                        |                                  |
|     {                                  |                                  |
|         "game_invite_id": "{id}"       |                                  |
|     }                                  |                                  |
+----------------------------------------+----------------------------------+
| .. code-block:: json                   | A game invite has been removed.  |
|     :caption: ``game.invite.removed``  |                                  |
|                                        | The ``reason`` may be one of:    |
|     {                                  | ``canceled``, ``expired``.       |
|         "game_invite_id": "{id}",      |                                  |
|         "reason": "{reason}"           |                                  |
|     }                                  |                                  |
+----------------------------------------+----------------------------------+
| .. code-block:: json                   | Someone joined the lobby.        |
|     :caption: ``lobby.joined``         |                                  |
|                                        |                                  |
|     {                                  |                                  |
|         "lobby_id": "{id}",            |                                  |
|         "user": {                      |                                  |
|             "id": "{id}",              |                                  |
|             "username": "{username}"   |                                  |
|         }                              |                                  |
|     }                                  |                                  |
+----------------------------------------+----------------------------------+
| .. code-block:: json                   | Someone left the lobby.          |
|     :caption: ``lobby.left``           |                                  |
|                                        |                                  |
|     {                                  |                                  |
|         "lobby_id": "{id}",            |                                  |
|         "user_id": "{user_id}"         |                                  |
|     }                                  |                                  |
+----------------------------------------+----------------------------------+
