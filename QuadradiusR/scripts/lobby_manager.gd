extends Node2D

onready var player_list = $PlayerList



func _ready():
	player_list.add_player("Stefan GUEST", "123", true)
	player_list.add_player(NetworkHandler.username, "312", false)
	if not NetworkHandler.lobby_data['players'].empty():
		for player in NetworkHandler.lobby_data['players']:
			player_list.add_player("username-" + player['id'], player['id'], false) # TODO: Fix username (param 1)


func _on_challenge_issued(username):
	player_list.receive_challenge(username)
	get_tree().change_scene("res://scenes/match_settings.tscn")
