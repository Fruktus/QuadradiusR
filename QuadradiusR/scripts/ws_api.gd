class_name WSApi
extends Node

const IDENTIFY = 2
const SERVER_READY = 3
const NOTIFICATION = 4
const SUBSCRIBE = 5
const SUBSCRIBED = 6
const KICK = 7

var op_handlers = {
	SERVER_READY: funcref(self, "_handle_server_ready"),
	NOTIFICATION: funcref(self, "_handle_notification"),
	SUBSCRIBED: funcref(self, "_handle_subscribed"),
	KICK: funcref(self, "_handle_kick"),
}
var topic_handlers = {
	"game.invite.accepted": funcref(self, "_handle_game_invite_accepted"),
	"game.invite.received": funcref(self, "_handle_game_invite_received"),
	"game.invite.removed": funcref(self, "_handle_game_invite_removed"),
	"lobby.joined": funcref(self, "_handle_lobby_joined"),
	"lobby.left": funcref(self, "_handle_lobby_left"),
}
var ws: WebSocketClient = WebSocketClient.new()
var token



func _ready():
	ws.connect("connection_closed", self, "_on_connection_closed")
	ws.connect("connection_error", self, "_on_connection_error")
	ws.connect("connection_established", self, "_on_connection_established")
	ws.connect("data_received", self, "_on_data_received")
	ws.connect("server_close_request", self, "_on_server_close_request")
	set_process(false)


func _process(delta):
	ws.poll()


# # # # # # # # # #
# Signal Handlers #
# # # # # # # # # #
func _on_connection_closed(was_clean: bool):
	print('connection closed, clean: ', was_clean)
	set_process(false)

func _on_connection_error():
	print('connection error')
	set_process(false)

func _on_connection_established(protocol: String):
	print('im in')  # DEBUG
	_send_data({'op': IDENTIFY, 'd': {"token": token}})  # authorize with the server before doing anything else

func _on_data_received():
	var data = _get_data()
	print('data received:', data)  # DEBUG
	op_handlers[int(data['op'])].call_func(data['d'])

func _on_server_close_request(code: int, reason: String):
	print('server closed. reason: ', reason, ' code: ', code)
	set_process(false)


# # # # # # # #
# OP Handlers #
# # # # # # # #
func _handle_server_ready(data: Dictionary):
	subscribe_to("*")  # DEBUG

func _handle_notification(data: Dictionary):
	topic_handlers[data['topic']].call_func(data['data'])

func _handle_subscribed(data: Dictionary):
	pass

func _handle_kick(data: Dictionary):
	pass


# # # # # # # # # #
# Topic Handlers  #
# # # # # # # # # #
# NOTE: All the parameters are always passed as String, so typehints for those will be skipped
func _handle_game_invite_accepted(data: Dictionary):
	var game_invite_id = data['game_invite_id']
	var game_id = data['game']['id']
	get_tree().call_group("ws_lobby", "_game_invite_accepted", game_invite_id, game_id)

func _handle_game_invite_received(data: Dictionary):
	var game_id = data['game_invite']['id']
	var from_id = data['game_invite']['from']['id']
	var from_username = data['game_invite']['from']['username']
	var subject_id = data['game_invite']['subject']['id']
	var subject_username = data['game_invite']['subject']['username']
	# IDK why but adding "expires" causes it to stop working
	get_tree().call_group("ws_lobby", "_game_invite_received", game_id, from_id, from_username, subject_id, subject_username)

func _handle_game_invite_removed(data: Dictionary):
	var game_invite_id = data['game_invite_id']
	var reason = data['reason']
	get_tree().call_group("ws_lobby", "_game_invite_removed", game_invite_id, reason)

func _handle_lobby_joined(data: Dictionary):
	var lobby_id = data['lobby_id']
	var user_id = data['user']['id']
	var user_username = data['user']['username']
	get_tree().call_group("ws_lobby", "_lobby_joined", lobby_id, user_id, user_username)

func _handle_lobby_left(data: Dictionary):
	var lobby_id = data['lobby_id']
	var user_id = data['user_id']
	get_tree().call_group("ws_lobby", "_lobby_left", lobby_id, user_id)


# # # # # # # #
# API Methods #
# # # # # # # #
func connect_to(url: String, token):
	self.token = token
	ws.connect_to_url(url)
	ws.get_peer(1).set_write_mode(WebSocketPeer.WRITE_MODE_TEXT)
	set_process(true)


func subscribe_to(topic: String):
	var query = {"op": SUBSCRIBE, "d": {"topic": topic}}
	_send_data(query)


# # # # # # #
# Utilities #
# # # # # # #
func _send_data(data: Dictionary):
	# TODO check if connection was established
	ws.get_peer(1).put_packet(JSON.print(data).to_utf8())


func _get_data() -> Dictionary:
	var packet = ws.get_peer(1).get_packet().get_string_from_utf8()
	return JSON.parse(packet).result
