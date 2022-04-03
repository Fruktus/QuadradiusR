class_name WSApi
extends Node


var ws: WebSocketClient = WebSocketClient.new()
var identified = false


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

func _on_connection_error():
	print('connection error')

func _on_connection_established(protocol: String):
	print('im in')
	if not identified:
		ws.get_peer(1).put_packet('{"op": 2}'.to_utf8())
		identified = true

func _on_data_received():
	print('data received:', ws.get_peer(1).get_packet().get_string_from_utf8())

func _on_server_close_request(code: int, reason: String):
	print('server closed. reason: ', reason, ' code: ', code)


# # # # # # # #
# API Methods #
# # # # # # # #
func connect_to(url: String):
	ws.connect_to_url(url)
	set_process(true)