extends Control


onready var board = $MarginContainer/ScreenHBox/GameBoardPanel/VBoxContainer/BoardMiddle/GameBoardPlaceholder/Board
onready var right_panel = $MarginContainer/ScreenHBox/RightSidePanel

func _ready():
	get_tree().call_group("torus", "set_interaction", Context.is_my_turn())


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_state_diff(data: Dictionary):
	var diff = data['game_state_diff']
	if diff['current_player_id'] == Context.user_id:
		# Play opponent's move
		if 'pieces' in diff['board']:
			for piece_id in diff['board']['pieces'].keys():
				if piece_id[0] == "$":
					continue
				var dest_tile_id = diff['board']['pieces'][piece_id]['tile_id']
				var source_tile_pos = Context.game_state.get_tile_pos_by_piece_id(piece_id)
				var dest_tile_pos = Context.game_state.get_tile_pos_by_tile_id(dest_tile_id)
				board.move_torus_by_tiles(source_tile_pos, dest_tile_pos)
	Context.game_state.apply_gamestate_diff(diff)
	# BUMP ETAGS
	get_tree().call_group("torus", "set_interaction", diff['current_player_id'] == Context.user_id) # WILL BE FIXED AFTER GAMESTATE UPDATE
