extends Node

signal lobby_player_joined(data)  # TODO when new player joins lobby
signal lobby_player_left(data)  # TODO when player leaves lobby
signal lobby_message_posted(data)  # TODO when someone posts message
signal lobby_challenge_received(data)  # TODO when player was challenged
signal lobby_communique_updated(data)  # TODO possibly ignore that and just store this data in this node, make lobby retrieve it every time

var message_template = load("res://scripts/message_template.gd")



# # # # # # # # # # # # # # # #
# Login/Lobby related methods #
# # # # # # # # # # # # # # # #

func join_lobby(username: String, password: String, is_guest: bool) -> Message:
	# accepts username, password and info if user is guest
	# Returns: true if operation succeeded, false if operation failed
	
	var message: Message = message_template.new()
	message.init(true, "ok")
	
	return message


func get_lobby_state():
	# TODO: will return players currently in lobby, their communique etc.
	pass


func get_scoreboard(month):
	# TODO: will retrieve the scoreboard for the given month.
	# Decide how to pass month as.
	# If not specified, will get the current month's data
	pass


func broadcast_message(message):
	# TODO: will send the message to the global lobby chat
	pass


func set_communique(message):
	# TODO: will set the player's communique status
	pass


func challenge_player(player):
	# TODO: will issue challenge to specified player
	pass

# # # # # # # # # # # # #
# Match related methods #
# # # # # # # # # # # # #

