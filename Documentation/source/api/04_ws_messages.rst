WebSocket Messages
==================


.. _ws_msg_identify:

``IDENTIFY (2)``
----------------

Used by the client to identify themselves.

.. code-block:: json
    :caption: Message format

    {
        "op": 2,
        "d": {
            "token": "{token}"
        }
    }


.. _ws_msg_server_ready:

``SERVER_READY (3)``
--------------------

Used by the server to inform about successful handshake.

.. code-block:: json
    :caption: Message format

    {
        "op": 3,
        "d": {}
    }


.. _ws_msg_notification:

``NOTIFICATION (4)``
--------------------

Notification.

.. code-block:: json
    :caption: Message format

    {
        "op": 4,
        "d": {
            "topic": "{topic}",
            "data": {}
        }
    }


.. _ws_msg_subscribe:

``SUBSCRIBE (5)``
-----------------

Request for notification subscription.

.. code-block:: json
    :caption: Message format

    {
        "op": 5,
        "d": {
            "topic": "{topic_wildcard}"
        }
    }


.. _ws_msg_subscribed:

``SUBSCRIBED (6)``
------------------

Subscription confirmation.

.. code-block:: json
    :caption: Message format

    {
        "op": 6,
        "d": {}
    }


.. _ws_msg_kick:

``KICK (7)``
------------

Information about forceful session closure.

.. code-block:: json
    :caption: Message format

    {
        "op": 7,
        "d": {
            "reason": "{reason}"
        }
    }


.. _ws_msg_send_message:

``SEND_MESSAGE (8)``
--------------------

Send a text message.

.. code-block:: json
    :caption: Message format

    {
        "op": 8,
        "d": {
            "content": "{content}"
        }
    }


.. _ws_msg_game_state:

``GAME_STATE (9)``
------------------

Inform about current game state.

.. code-block:: json
    :caption: Message format

    {
        "op": 9,
        "d": {
            "recipient_id": "{user_id}",
            "game_state": {},
            "etag": "{etag}"
        }
    }

See :ref:`rest_game_state` for data structures.


.. _ws_msg_game_state_diff:

``GAME_STATE_DIFF (10)``
------------------------

Inform about a difference in game state.

.. code-block:: json
    :caption: Message format

    {
        "op": 10,
        "d": {
            "recipient_id": "{user_id}",
            "game_state_diff": {},
            "etag_from": "{etag}",
            "etag_to": "{etag}"
        }
    }

The ``game_state_diff`` property describes difference
in game state structures described in :ref:`ws_msg_game_state`.
The special property ``$delete`` describes items which
were deleted in the diff.


.. _ws_msg_move:

``MOVE (11)``
-------------

Perform a move by the player.

.. code-block:: json
    :caption: Message format

    {
        "op": 11,
        "d": {
            "piece_id": "{piece_id}",
            "tile_id": "{tile_id}"
        }
    }


.. _ws_msg_action_result:

``ACTION_RESULT (12)``
----------------------

Inform about the result of a player's move.

.. code-block:: json
    :caption: Message format

    {
        "op": 12,
        "d": {
            "is_legal": true,
            "reason": "{reason}"
        }
    }


.. _ws_msg_apply_power:

``APPLY_POWER (13)``
--------------------

Apply a power.

.. code-block:: json
    :caption: Message format

    {
        "op": 11,
        "d": {
            "power_id": "{power_id}"
        }
    }
