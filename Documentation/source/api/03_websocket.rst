=============
WebSocket API
=============


WebSocket basics
================

All data in each WS connection to the server is sent using text frames.
Each frame contains a JSON object which consists of two keys:

#. ``op`` --- opcode,
#. ``d`` --- data.

Opcode defines semantics for the message, whereas data contains all
the data the message needs.
For instance, a message ``ERROR`` may have the following contents:

.. code-block:: json

    {
        "op": 1,
        "d": {
            "message": "Unknown error",
            "fatal": false
        }
    }


Handshake protocol
==================

Each WS connection to the server is a subject to the handshake protocol.
The first message sent to the server on a WebSocket
must be :ref:`ws_msg_identify`.
Sending any other message will result in an error.
If authorization fails, the communication also ends with an error.

When identification succeeds, the server sends :ref:`ws_msg_server_ready`.
Only after receiving this message the client
may send any requests to the server.


Common API
==========

This section describes the common API shared between all WS connections.


Subscribing to notifications
----------------------------

+----------------+--------------------------+---------+
| Direction      | Message                  | Comment |
+================+==========================+=========+
| Client->Server | :ref:`ws_msg_subscribe`  |         |
+----------------+--------------------------+---------+
| Server->Client | :ref:`ws_msg_subscribed` |         |
+----------------+--------------------------+---------+


.. _ws_gateway:

Gateway connection
==================

The gateway is the main two-way connection
used to communicate with the server.
In order to obtain the gateway URL, the endpoint
:ref:`rest_gateway` must be used.


.. _ws_game:

Game connection
===============

Game connection represents an active participation in a game.
In order to obtain the game connection URL, the endpoint
:ref:`rest_game` must be used.


Messages
========

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
