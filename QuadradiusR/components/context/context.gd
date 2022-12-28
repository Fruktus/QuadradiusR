extends Node

var username: String
var user_id: String
var lobby_data: Dictionary
var game_data: Dictionary
var game_state: GameState
var powerups_data: Dictionary



func is_my_turn() -> bool:
	return game_state.get_current_player() == user_id


func get_other_player() -> Dictionary:
	for player in game_data['players']:
		if player.id != user_id:
			return player
	return {}


func get_power_by_definition_id(power_def_id: String) -> Dictionary:
	return powerups_data[power_def_id]
