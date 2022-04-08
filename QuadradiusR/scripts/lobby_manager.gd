extends Node2D

onready var player_list = $PlayerList



func _ready():
	if not NetworkHandler.lobby_data['players'].empty():
		for player in NetworkHandler.lobby_data['players']:
			player_list.add_player(player['username'], player['id'], false) # TODO: Fix username (param 1)
	player_list.add_player(NetworkHandler.username, "312", true)


func _on_challenge_issued(username):
#	player_list.receive_challenge(username)
	pass
#	get_tree().change_scene("res://scenes/match_settings.tscn")


func _on_challenge_received(uuid):
	pass


func _on_challenge_accepted(game_id, opponent_id):
	NetworkHandler.rest_api.accept_game_invite(NetworkHandler.token, game_id)  # DEBUG implement proper method in NetworkHandler
	get_tree().change_scene("res://scenes/game.tscn")


func _game_invite_accepted(game_invite_id, game_id):
	get_tree().change_scene("res://scenes/game.tscn")
