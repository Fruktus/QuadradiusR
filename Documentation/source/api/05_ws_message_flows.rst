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

+-----------------+--------------------------+-------------------------------------------+
| Direction       | Message                  | Comment                                   |
+=================+==========================+===========================================+
| Client0->Server | :ref:`ws_msg_subscribe`  | Client sends a request for subscription.  |
+-----------------+--------------------------+-------------------------------------------+
| Server->Client0 | :ref:`ws_msg_subscribed` | Server acknowledges that the subscription |
|                 |                          | has been processed and the client will    |
|                 |                          | receive notifications on this topic from  |
|                 |                          | now on.                                   |
+-----------------+--------------------------+-------------------------------------------+


Receiving notifications
-----------------------

Available in:

* :ref:`ws_gateway`
* :ref:`ws_game`
* :ref:`ws_lobby`

+-----------------+----------------------------+--------------------------------------------+
| Direction       | Message                    | Comment                                    |
+=================+============================+============================================+
| Server->Client0 | :ref:`ws_msg_notification` | Server notifies the client about an event. |
+-----------------+----------------------------+--------------------------------------------+


Being kicked from the session
-----------------------------

Available in:

* :ref:`ws_game`
* :ref:`ws_lobby`

+-----------------+--------------------+----------------------------------------------+
| Direction       | Message            | Comment                                      |
+=================+====================+==============================================+
| Server->Client0 | :ref:`ws_msg_kick` | Server notifies the client that it's being   |
|                 |                    | disconnected from the session.               |
|                 |                    | After this message the connection is closed. |
+-----------------+--------------------+----------------------------------------------+


Sending a message
-----------------

Available in:

* :ref:`ws_lobby`

+-----------------+----------------------------+---------------------------+
| Direction       | Message                    | Comment                   |
+=================+============================+===========================+
| Client0->Server | :ref:`ws_msg_send_message` | Client sends the message. |
+-----------------+----------------------------+---------------------------+


Receiving initial game state
----------------------------

Available in:

* :ref:`ws_game`

+-----------------+----------------------------+---------------------------+
| Direction       | Message                    | Comment                   |
+=================+============================+===========================+
| Server->Client0 | :ref:`ws_msg_game_state`   | Server informs about the  |
|                 |                            | current game state.       |
+-----------------+----------------------------+---------------------------+


Performing a move
-----------------

Available in:

* :ref:`ws_game`

+-----------------+-------------------------------+------------------------------+
| Direction       | Message                       | Comment                      |
+=================+===============================+==============================+
| Client0->Server | :ref:`ws_msg_move`            | Client performs a move.      |
+-----------------+-------------------------------+------------------------------+
| Server->Client0 | :ref:`ws_msg_action_result`   | Server informs whether the   |
|                 |                               | move was legal.              |
|                 |                               |                              |
|                 |                               | If the move was illegal,     |
|                 |                               | communication stops.         |
+-----------------+-------------------------------+------------------------------+
| Server->Client* | :ref:`ws_msg_game_state_diff` | Server informs about what    |
|                 |                               | changed.                     |
+-----------------+-------------------------------+------------------------------+


Applying a power
----------------

Available in:

* :ref:`ws_game`

+-----------------+-------------------------------+------------------------------+
| Direction       | Message                       | Comment                      |
+=================+===============================+==============================+
| Client0->Server | :ref:`ws_msg_apply_power`     | Client applies a power.      |
+-----------------+-------------------------------+------------------------------+
| Server->Client0 | :ref:`ws_msg_action_result`   | Server informs whether the   |
|                 |                               | application was legal.       |
|                 |                               |                              |
|                 |                               | If it was illegal,           |
|                 |                               | communication stops.         |
+-----------------+-------------------------------+------------------------------+
| Server->Client* | :ref:`ws_msg_game_state_diff` | Server informs about what    |
|                 |                               | changed.                     |
+-----------------+-------------------------------+------------------------------+
