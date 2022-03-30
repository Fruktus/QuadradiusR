Getting started
===============

The server's API consists of two main parts:

#. REST API, and
#. WebSocket API.

Resources such as users, games, etc. are provided using the REST API.
WebSocket API exists to handle full-duplex real-time communication
such as messaging or the game itself.

Authorization
-------------

Requests to the server are globally authorized using a JWT token.
Some REST endpoints require authorization and when no authorization
is provided (or the provided authorization is invalid),
they return a ``401 Unauthorized`` response.

In order to provide authorization to a request, an ``Authorization``
header must be present, with the value of the token.
In order to obtain a token, the endpoint :ref:`rest_post_authorize`
must be used.
