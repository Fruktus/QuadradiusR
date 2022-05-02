class_name GameState

var game_data: Dictionary
var etag: String


func init(game_data: Dictionary, etag: String):
	self.game_data = game_data
	self.etag = etag
	return self



func get_board_size() -> Dictionary:
	return self.game_data['settings']['board_size']


func get_pieces() -> Array:
	return self.game_data['board']['pieces']


func get_tiles() -> Array:
	return self.game_data['board']['tiles']


func get_current_player() -> String:
	return self.game_data['current_player_id']


func get_tile_by_id(tile_id: String, board: Node) -> Tile:
	var pos = game_data['board']['tiles'][tile_id]['position']
	return board._get_child_at_pos(pos['x'], pos['y'])


func get_tile_pos_by_tile_id(tile_id: String) -> Vector2:
	var tile_pos = game_data['board']['tiles'][tile_id]['position']
	return Vector2(tile_pos['x'], tile_pos['y'])


func get_tile_pos_by_piece_id(piece_id: String) -> Vector2:
	var tile_id = game_data['board']['pieces'][piece_id]['tile_id']
	return get_tile_pos_by_tile_id(tile_id)


func apply_gamestate_diff(diff: Dictionary):
	_apply_diff(game_data, diff)


func _apply_diff(original: Dictionary, diff: Dictionary):
	for key in diff.keys():
		if key == '$delete':
			for del_key in diff[key]:
				original.erase(del_key)
		elif typeof(diff[key]) == TYPE_DICTIONARY:
			if not original.has(key):
				original[key] = {}
			_apply_diff(original[key], diff[key])
		else:
			original[key] = diff[key]
