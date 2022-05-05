extends Node

signal lobby_player_joined(data)  # TODO when new player joins lobby
signal lobby_player_left(data)  # TODO when player leaves lobby
signal lobby_message_posted(data)  # TODO when someone posts message
signal lobby_challenge_received(data)  # TODO when player was challenged
signal lobby_communique_updated(data)  # TODO possibly ignore that and just store this data in this node, make lobby retrieve it every time

onready var rest_api: RestApi = $RESTApi
onready var ws_api: WSApi = $WSApi

var url = "http://127.0.0.1:8888"
var token: String

func _ready():
	if OS.has_feature('JavaScript'):
		url = JavaScript.eval('window.location.href')
		if not url.ends_with('/'):
			url = url.rsplit('/', true, 1)[0]
	rest_api.url = url
	# use_threads=true does not work for HTML5
	rest_api.use_threads = false
	rest_api.max_redirects = 0


func set_url(url: String):
	rest_api.url = url

# # # # # # # #
# CREATE USER #
# # # # # # # #
func create_user_and_connect_ws(cb: FuncRef):  # for testing the control flow, not meant to be left like that
	print('cr user 0') # DEBUG
	rest_api.create_user('test', 'asdf', funcref(self, "_create_user_and_connect_ws_1"), {'cb': cb})

func _create_user_and_connect_ws_1(message: Message, args: Dictionary):
	# After create_user
	print('cr user 1 ', message) # DEBUG
	rest_api.authorize('test', 'asdf', funcref(self, "_create_user_and_connect_ws_2"), args)

func _create_user_and_connect_ws_2(message: Message, args: Dictionary):
	# After authorize
	print('cr user 2 ', message) # DEBUG
	var token = message.body['token']
	args['cb'].call_func(message)


func create_user(username: String, password: String, cb: FuncRef, args: Dictionary):
	rest_api.create_user(username, password, funcref(self, "_create_user_1"), {'cb': cb})

func _create_user_1(message: Message, args: Dictionary):
	pass


# # # # # # # # # #
# AUTHORIZE USER  #
# # # # # # # # # #
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


# # # # # # # #
# JOIN LOBBY  #
# # # # # # # #
func join_lobby(cb: FuncRef):
	rest_api.get_lobby(token, funcref(self, "_join_lobby_1"), {'cb': cb})

func _join_lobby_1(message: Message, args: Dictionary):
	# After get_lobby
	if message.result == 200:
		Context.lobby_data = message.body
		print(message.body["ws_url"])
		ws_api.connect_to(message.body["ws_url"], token)
	else:
		print('failed to obtain the lobby:', message.result)
		var test = "ws://127.0.0.1:8888/lobby/@main/connect"
		ws_api.connect_to(test, token)

	rest_api.get_lobby(token, funcref(self, "_join_lobby_2"), args)

func _join_lobby_2(message: Message, args: Dictionary):
	if message.result == 200:
		Context.lobby_data = message.body

	args['cb'].call_func()


# # # # # # # # #
# INVITE PLAYER #
# # # # # # # # #
func invite_player(opponent_uuid: String):
	rest_api.invite_player(token, opponent_uuid)


# # # # # # # # # # # # #
# ACCEPT AND JOIN GAME  #
# # # # # # # # # # # # #
func accept_and_join_game(game_invite_id: String, cb: FuncRef):
	rest_api.accept_game_invite(self.token, game_invite_id, funcref(self, "_accept_and_join_game_1"), {"game_invite_id": game_invite_id, 'cb': cb})

func _accept_and_join_game_1(message: Message, args: Dictionary):
	# After accept_game_invite
	var game_id = ""
	# FIXME: clean up this mess, HTML5 and executables
	#   have different behaviors when it comes to redirects
	if message.result == 200:
		game_id = message.body['id']
	elif message.result == 303:
		for header in message.headers:
			if 'location' in header:
				game_id = header.substr(16, len(message.headers[0]))
				break
	join_game(game_id, args['cb'])


# # # # # # #
# JOIN GAME #
# # # # # # #
func join_game(game_id: String, cb: FuncRef):
	rest_api.get_game(self.token, game_id, funcref(self, "_join_game_1"), {'cb': cb})

func _join_game_1(message: Message, args: Dictionary):
	# After get_game
	if message.result == 200:
		ws_api.close("Moving from lobby to game")
		ws_api.connect_to(message.body["ws_url"], self.token)
		rest_api.get_game_state(self.token, message.body['id'], funcref(self, "_join_game_2"), args)
	else:
		print('ERROR WHEN GETTING GAME DATA')
	
func _join_game_2(message: Message, args: Dictionary):
	# After get_game_state
	var etag = ""
	for header in message.headers:
		if "etag" in header:
			etag = header.substr(7, 18)
	Context.game_state = GameState.new().init(message.body, etag)
	args['cb'].call_func()
