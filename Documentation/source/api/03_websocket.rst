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


Common flows
============

This section describes the common message flows
shared between all WS connections.


Subscribing to notifications
----------------------------

+----------------+--------------------------+-------------------------------------------+
| Direction      | Message                  | Comment                                   |
+================+==========================+===========================================+
| Client->Server | :ref:`ws_msg_subscribe`  | Client sends a request for subscription.  |
+----------------+--------------------------+-------------------------------------------+
| Server->Client | :ref:`ws_msg_subscribed` | Server acknowledges that the subscription |
|                |                          | has been processed and the client will    |
|                |                          | receive notifications on this topic from  |
|                |                          | now on.                                   |
+----------------+--------------------------+-------------------------------------------+


Receiving notifications
-----------------------

+----------------+----------------------------+--------------------------------------------+
| Direction      | Message                    | Comment                                    |
+================+============================+============================================+
| Server->Client | :ref:`ws_msg_notification` | Server notifies the client about an event. |
+----------------+----------------------------+--------------------------------------------+


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
