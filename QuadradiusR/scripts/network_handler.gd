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
var username: String
var user_id: String
var lobby_data: Dictionary
var game_state: GameState



func _ready():
	rest_api.url = url


# # # # # # # #
# CREATE USER #
# # # # # # # #
func create_user_and_connect_ws(cb: FuncRef):  # for testing the control flow, not meant to be left like that
	print('cr user 0') # DEBUG
	rest_api.create_user('test', 'asdf', funcref(self, "_create_user_and_connect_ws_1"), {'cb': cb})

func _create_user_and_connect_ws_1(message: Message, args: Dictionary):
	print('cr user 1 ', message) # DEBUG
	rest_api.authorize('test', 'asdf', funcref(self, "_create_user_and_connect_ws_2"), args)

func _create_user_and_connect_ws_2(message: Message, args: Dictionary):
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
	var is_authorized = message.result == 200

	if is_authorized:
		token = message.body['token'] if is_authorized else ""
		rest_api.get_user_me(self.token, funcref(self, "_authorize_user_2"), args)
	else:
		args['cb'].call_func(is_authorized, args['user_data'], message)

func _authorize_user_2(message: Message, args: Dictionary):
	username = message.body['username']
	user_id = message.body['id']
	args['cb'].call_func(true, args['user_data'], message)


# # # # # # # #
# JOIN LOBBY  #
# # # # # # # #
func join_lobby(cb: FuncRef):
	rest_api.get_lobby(token, funcref(self, "_join_lobby_1"), {'cb': cb})

func _join_lobby_1(message: Message, args: Dictionary):
	if message.result == 200:
		lobby_data = message.body
		print(message.body["ws_url"])
		ws_api.connect_to(message.body["ws_url"], token)
	else:
		print('failed to obtain the lobby:', message.result)
		var test = "ws://127.0.0.1:8888/lobby/@main/connect"
		ws_api.connect_to(test, token)

	args['cb'].call_func()


# # # # # # # # #
# INVITE PLAYER #
# # # # # # # # #
func invite_player(opponent_uuid: String):
	rest_api.invite_player(token, opponent_uuid)


# # # # # # # # # # # # #
# ACCEPT AND JOIN GAME  #
# # # # # # # # # # # # #
func accept_and_join_game(game_invite_id, cb: FuncRef):
	rest_api.accept_game_invite(self.token, game_invite_id, funcref(self, "_accept_and_join_game_1"), {"game_invite_id": game_invite_id, 'cb': cb})

func _accept_and_join_game_1(message: Message, args: Dictionary):
	var game_id = message.headers[0].substr(16, len(message.headers[0]))
	join_game(game_id, args['cb'])


# # # # # # #
# JOIN GAME #
# # # # # # #
func join_game(game_id, cb: FuncRef):
	rest_api.get_game(self.token, game_id, funcref(self, "_join_game_1"), {'cb': cb})

func _join_game_1(message: Message, args: Dictionary):
	if message.result == 200:
		ws_api.close("Moving from lobby to game")
		ws_api.connect_to(message.body["ws_url"], self.token)
		rest_api.get_game_state(self.token, message.body['id'], funcref(self, "_join_game_2"), args)
	else:
		print('ERROR WHEN GETTING GAME DATA')
	
func _join_game_2(message: Message, args: Dictionary):
	game_state = GameState.new().init(message.body)
	args['cb'].call_func()
