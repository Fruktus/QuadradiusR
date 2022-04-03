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


func req_gw():
	rest_api.get_gateway()
