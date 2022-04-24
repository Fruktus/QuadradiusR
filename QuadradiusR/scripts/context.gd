extends Node

var username: String
var user_id: String
var lobby_data: Dictionary
var game_state: GameState

func is_my_turn() -> bool:
	return game_state.get_current_player() == user_id
