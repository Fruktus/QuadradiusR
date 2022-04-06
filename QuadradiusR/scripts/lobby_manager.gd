extends Node2D

onready var player_list = $PlayerList



func _ready():
	player_list.add_player("Stefan GUEST", true)
	player_list.add_player(NetworkHandler.username, false)
	if not NetworkHandler.lobby_data['players'].empty():
		for i in NetworkHandler.lobby_data['players']:
			player_list.add_player(i['id'], false)  # TODO request own id too


func _on_challenge_issued(username):
	player_list.receive_challenge(username)
	get_tree().change_scene("res://scenes/match_settings.tscn")
