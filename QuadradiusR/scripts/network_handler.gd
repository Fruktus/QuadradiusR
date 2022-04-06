extends Node

signal lobby_player_joined(data)  # TODO when new player joins lobby
signal lobby_player_left(data)  # TODO when player leaves lobby
signal lobby_message_posted(data)  # TODO when someone posts message
signal lobby_challenge_received(data)  # TODO when player was challenged
signal lobby_communique_updated(data)  # TODO possibly ignore that and just store this data in this node, make lobby retrieve it every time

onready var rest_api = $RESTApi
onready var ws_api = $WSApi

var url = "http://127.0.0.1:8888"
var token: String
var username: String
var lobby_data: Dictionary


func _ready():
	rest_api.url = url


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
#	ws_api.connect_to('ws://127.0.0.1:8888/gateway', token)


func create_user(username: String, password: String, cb: FuncRef, args: Dictionary):
	rest_api.create_user(username, password, funcref(self, "_create_user_1"), {'cb': cb})

func _create_user_1(message: Message, args: Dictionary):
	pass


func authorize_user(username: String, password: String, cb: FuncRef, args: Dictionary):
	rest_api.authorize(username, password, funcref(self, "_authorize_user_1"), {'cb': cb, 'user_data': args})

func _authorize_user_1(message: Message, args: Dictionary):
	var is_authorized = message.result == 200
	username = args['user_data']['username']  # TODO only if successful
	token = message.body['token'] if is_authorized else ""
	args['cb'].call_func(is_authorized, args['user_data'], message)


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
	

func invite_player(opponent_uuid: String):
	rest_api.invite_player(token, opponent_uuid)
