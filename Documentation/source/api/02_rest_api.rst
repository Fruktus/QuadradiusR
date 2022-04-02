REST API
========

This section describes all of the REST API endpoints.


.. _rest_post_authorize:

``POST /authorize``
-------------------

Obtain a token.

.. code-block:: json
    :caption: Request body

    {
        "username": "{username}",
        "password": "{password}"
    }

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "token": "{token}"
    }


.. _rest_game:

``GET /game/{id}``
------------------

Get information about a game.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "id": "{id}",
        "players": [
            "{player_id_1}",
            "{player_id_2}"
        ],
        "expiration": "{iso_date_time_expiration}",
        "ws_url": "{websocket_url}"
    }


.. _rest_gateway:

``GET /gateway``
----------------

Get information about the gateway connection.
See :ref:`ws_gateway`.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "url": "{gateway_url}"
    }


``GET /health``
---------------

Get server's status.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "status": "up"
    }


``POST /game_invite``
---------------------

Create a new invite for a game.

.. code-block:: json
    :caption: Request body

    {
        "subject": "{user_id}",
        "expiration": "{iso_date_time_expiration}"
    }

.. code-block:: text
    :caption: Response status

    201 Created

.. code-block:: text
    :caption: Response headers

    location: /game_invite/{id}


``DELETE /game_invite/{id}``
----------------------------

Reject or withdraw a game invite.

.. code-block:: text
    :caption: Response status

    204 No Content


``GET /game_invite/{id}``
-------------------------

Get information about a game invite.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "id": "{id}",
        "from": "{user_id}",
        "subject": "{user_id}",
        "expiration": "{iso_date_time_expiration}"
    }


``POST /game_invite/{id}/accept``
---------------------------------

Accept a game invite.
Upon successful acceptance, the user is redirected to the game resource.

.. code-block:: text
    :caption: Response status

    303 See Other

.. code-block:: text
    :caption: Response headers

    location: /game/{id}


``GET /lobby``
--------------

List lobbies.

.. code-block:: text
    :caption: Response status

    200 OK

Response body is an array of lobbies.
See :ref:`rest_lobby` for data structure.


.. _rest_lobby:

``GET /lobby/{lobby_id}``
-------------------------

Get information about lobby.

If ``{lobby_id}`` is equal to ``@main``,
the main lobby is returned.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "id": "{lobby_id}",
        "name": "{lobby_name}"
    }


``POST /user``
--------------

Create a user.

.. code-block:: json
    :caption: Request body

    {
        "username": "{username}",
        "password": "{password}"
    }

.. code-block:: text
    :caption: Response status

    201 Created

.. code-block:: text
    :caption: Response headers

    location: /user/{user_id}


``GET /user/{user_id}``
-----------------------

Get information about a user.
The parameter ``{user_id}`` may be equal to ``@me``
in order to retrieve information about yourself.

.. code-block:: text
    :caption: Response status

    200 OK

.. code-block:: json
    :caption: Response body

    {
        "id": "{id}",
        "username": "{username}"
    }
