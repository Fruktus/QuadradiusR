extends Node

signal lobby_player_joined(data)  # TODO when new player joins lobby
signal lobby_player_left(data)  # TODO when player leaves lobby
signal lobby_message_posted(data)  # TODO when someone posts message
signal lobby_challenge_received(data)  # TODO when player was challenged
signal lobby_communique_updated(data)  # TODO possibly ignore that and just store this data in this node, make lobby retrieve it every time

onready var rest_api = $RESTApi
onready var ws_api = $WSApi

var url = "http://127.0.0.1:8888"



func _ready():
	rest_api.url = url


func create_user_and_connect_ws():
	print('cr user 0') # DEBUG
	rest_api.create_user('test', 'asdf', funcref(self, "_create_user_and_connect_ws_1"))

func _create_user_and_connect_ws_1(message: Message):
	print('cr user 1 ', message) # DEBUG
	var req_id = rest_api.authorize('test', 'asdf', funcref(self, "_create_user_and_connect_ws_2"))

func _create_user_and_connect_ws_2(message: Message):
	print('cr user 2 ', message) # DEBUG
	var token = message.body['token']
	ws_api.connect_to('ws://127.0.0.1:8888/gateway', token)


