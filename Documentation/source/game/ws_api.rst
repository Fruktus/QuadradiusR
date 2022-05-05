WebSocket API
=============

The WebSocket API handles interaction with QR Server WS Api.
It provides methods for sending data to server, as well as handlers for notifications.


How notifications work
----------------------

The ws_api listens for all subscribed notification types (by default all of them).
It has different handlers for specific types of notifications, which define how they will be handled.
Each notification handler works in similar manner --- it extracts all the necessary data and emits group signal (either `ws_lobby` or `ws_game` depending on notification type)
whose name is the name of notification prefixed with underscore and has all the received data as a parameters.

Nodes which wish to subscribe to those signals need to be added to relevant group and implement a function with exactly the same signature as in the handler.
By convention, we assume that only the root of each scene should subscribe to those listeners and propagate data downward to its children to avoid spaghetti code.
To make it more distinguishable when reading the code, the listeners for those events should be predecessed by following comment block:

.. code-block:: text

    # # # # # # # # #
    # WS Listeners  #
    # # # # # # # # #
