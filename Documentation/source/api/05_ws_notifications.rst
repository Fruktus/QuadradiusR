Notifications
=============

+----------------------------------------+----------------------------------+
| Topic and message                      |           Description            |
+========================================+==================================+
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
