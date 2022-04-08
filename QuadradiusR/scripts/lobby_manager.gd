extends Node2D

onready var player_list = $PlayerList



func _ready():
	if not NetworkHandler.lobby_data['players'].empty():
		for player in NetworkHandler.lobby_data['players']:
			player_list.add_player(player['username'], player['id'], false)
	player_list.add_player(NetworkHandler.username, "", true)  # TODO add uuid properly


func _on_challenge_accepted(game_id, opponent_id):
	NetworkHandler.rest_api.accept_game_invite(NetworkHandler.token, game_id)  # DEBUG implement proper method in NetworkHandler
	get_tree().change_scene("res://scenes/game.tscn")


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_invite_accepted(game_invite_id, game_id):
	get_tree().change_scene("res://scenes/game.tscn")
