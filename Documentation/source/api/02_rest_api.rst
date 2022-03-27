REST API
========

This section describes all of the REST API endpoints.


.. _rest_post_authorize:

``POST /authorize``
-------------------

Obtain a token.

.. code-block:: json
    :caption: Request

    {
        "username": "{username}",
        "password": "{password}"
    }

.. code-block:: text
    :caption: Status

    200 OK

.. code-block:: json
    :caption: Response

    {
        "token": "{token}"
    }


``GET /gateway``
----------------

Get information about the gateway connection.
See :ref:`ws_gateway`.

.. code-block:: text
    :caption: Status

    200 OK

.. code-block:: json
    :caption: Response

    {
        "url": "{gateway_url}"
    }


``GET /health``
---------------

Get server's status.

.. code-block:: text
    :caption: Status

    200 OK

.. code-block:: json
    :caption: Response

    {
        "status": "up"
    }


``POST /user``
--------------

Create a user.

.. code-block:: json
    :caption: Request

    {
        "username": "{username}",
        "password": "{password}"
    }

.. code-block:: text
    :caption: Status

    201 Created

.. code-block:: text
    :caption: Headers

    location: /user/{user_id}


``GET /user/{user_id}``
-----------------------

Get information about a user.
The parameter ``{user_id}`` may be equal to ``@me``
in order to retrieve information about yourself.

.. code-block:: text
    :caption: Status

    200 OK

.. code-block:: json
    :caption: Response

    {
        "id": "{id}",
        "username": "{username}"
    }
