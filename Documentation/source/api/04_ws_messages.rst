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
