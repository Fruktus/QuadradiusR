extends Node2D

onready var player_list = $PlayerList

const MATCH_SETTINGS_SCENE = preload("res://scenes/match_settings.tscn")



func _ready():
	if not Context.lobby_data['players'].empty():
		for player in Context.lobby_data['players']:
			player_list.add_player(player['username'], player['id'], player['id'] == Context.user_id)


func _on_challenge_accepted(game_invite_id: String, opponent_id: String):
	NetworkHandler.accept_and_join_game(game_invite_id, funcref(self, "_on_game_joined"))


func _on_game_joined():
	get_tree().change_scene_to(MATCH_SETTINGS_SCENE)

# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_invite_accepted(game_invite_id, game_id):
	NetworkHandler.join_game(game_id, funcref(self, "_on_game_joined"))
