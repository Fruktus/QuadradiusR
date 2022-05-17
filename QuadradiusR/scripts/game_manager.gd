extends Control


onready var board = $MarginContainer/ScreenHBox/GameBoardPanel/VBoxContainer/BoardMiddle/GameBoardPlaceholder/Board
onready var right_panel = $MarginContainer/ScreenHBox/RightSidePanel



func _ready():
	get_tree().call_group("torus", "set_interaction", Context.is_my_turn())


# # # # # # # # # # # # #
# GameState Processing  #
# # # # # # # # # # # # #
func _process_pieces(pieces: Dictionary):
	for piece_id in pieces.keys():
		if piece_id[0] == "$":
			continue
		
		var piece = pieces[piece_id]
		if board.get_torus_by_id(piece_id).player_id == Context.user_id:
			continue
		
		var source_tile_pos = Context.game_state.get_tile_pos_by_piece_id(piece_id)
		var dest_tile_pos = Context.game_state.get_tile_pos_by_tile_id(piece['tile_id'])
		
		board.move_torus_by_tiles(source_tile_pos, dest_tile_pos)


func _process_powers(powers: Dictionary):
	for orb_id in powers:
		var orb = powers[orb_id]
		
		if orb['tile_id']:
			board.spawn_orb_on_tile_id(orb_id, orb['tile_id'])
		if orb['piece_id']:
			board.get_tile_by_orb_id(orb_id).collect_orb()
			board.get_torus_by_id(orb['piece_id']).add_power(
				orb_id, Context.game_state.get_powerup_by_id(orb_id)['power_definition_id'])


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_state_diff(data: Dictionary):
	var diff = data['game_state_diff']

	if 'pieces' in diff['board']:
		_process_pieces(diff['board']['pieces'])
	
	Context.game_state.apply_gamestate_diff(diff)
	
	if 'powers' in diff['board']:
		_process_powers(diff['board']['powers'])
	
	# TODO BUMP ETAGS
	get_tree().call_group("torus", "set_interaction", diff['current_player_id'] == Context.user_id) # WILL BE FIXED AFTER GAMESTATE UPDATE
