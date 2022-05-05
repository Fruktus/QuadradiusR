Network Handler
===============

Network Handler is a high-level Networking API for Quadradius Server.
It uses internally REST API and WS API to handle the networking.
Its main goal is to provide specificaly tailored functions for other nodes, while hiding the implementation details.
For example, when joining lobby you would have to authorize, get the lobby state and connect to WebSocket to complete the process.
Network Handler does all that within `join_lobby` function, while initializing the context for later use.


How it works
------------

Due to how Godot works (and specifically the way it handles HTTP requests), all the code executed has to be asynchronous.
This means that we cannot wait in code for the request to complete.
Rather, we dispatch it and provide a callback that will be executed once the request is completed.
This is the basis for all the functions within the handler.

Let's look at an example case:

.. code-block:: text
    :caption: authorize_user function

    func authorize_user(username: String, password: String, cb: FuncRef, args: Dictionary):
        rest_api.authorize(username, password, funcref(self, "_authorize_user_1"), {'cb': cb, 'user_data': args})

    func _authorize_user_1(message: Message, args: Dictionary):
        # After authorize
        var is_authorized = message.result == 200

        if is_authorized:
            token = message.body['token']
            rest_api.get_user_me(self.token, funcref(self, "_authorize_user_2"), args)
        else:
            args['cb'].call_func(is_authorized, args['user_data'], message)

    func _authorize_user_2(message: Message, args: Dictionary):
        # After get_user_me
        Context.username = message.body['username']
        Context.user_id = message.body['id']
        args['cb'].call_func(true, args['user_data'], message)

The above function has three stages total.
The convention is that entrypoint function (the one publicly available) is named like any Godot function and
every following stage is prefixed by underscore and postfixed by number denoting the order in which it will be called.
The entrypoint function can accept any parameters that will be needed for it later and should (but does not always need to) accept a `FuncRef` callback.
This lets the requestor node provide the function that will be called after the request completes.

The subsequent stages have to follow specific signature --- they have to accept message and args parameters.
They are returned by the REST API client.
The message is a special object containing all data retrieved from the server, while args works like a context.
Args can be provbided when making a request through REST API and it will be returned back when the request completes.
This allows persisting additional data between requests.
This also means that when accepting the callback from the entrypoint, it needs to be put into the args.
As a convention, it should be under `cb` key.

The last stage of each function chain should call this callback function, possibly with additional parameters as required by the nodes that will be using it.
