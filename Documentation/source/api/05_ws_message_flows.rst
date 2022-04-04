WebSocket Message Flows
=======================

This section describes message flows encountered
when being connected to WebSocket sessions.


Subscribing to notifications
----------------------------

Available in:

* :ref:`ws_gateway`
* :ref:`ws_game`
* :ref:`ws_lobby`

See :ref:`ws_notification` for list of possible notifications.

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

Available in:

* :ref:`ws_gateway`
* :ref:`ws_game`
* :ref:`ws_lobby`

+----------------+----------------------------+--------------------------------------------+
| Direction      | Message                    | Comment                                    |
+================+============================+============================================+
| Server->Client | :ref:`ws_msg_notification` | Server notifies the client about an event. |
+----------------+----------------------------+--------------------------------------------+

Being kicked from the session
-----------------------------

Available in:

* :ref:`ws_game`
* :ref:`ws_lobby`

+----------------+--------------------+----------------------------------------------+
| Direction      | Message            | Comment                                      |
+================+====================+==============================================+
| Server->Client | :ref:`ws_msg_kick` | Server notifies the client that it's being   |
|                |                    | disconnected from the session.               |
|                |                    | After this message the connection is closed. |
+----------------+--------------------+----------------------------------------------+
