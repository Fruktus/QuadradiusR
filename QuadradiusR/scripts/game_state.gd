class_name GameState

var game_data: Dictionary



func init(game_data: Dictionary):
	self.game_data = game_data
	return self


func set_data(game_data: Dictionary):
	self.game_data = game_data


func get_board_size():
	return self.game_data['settings']['board_size']


func get_pieces():
	return self.game_data['board']['pieces']


func get_tiles():
	return self.game_data['board']['tiles']


func get_tile_by_id(tile_id: String, board: Node) -> Tile:
	var pos = game_data['board']['tiles'][tile_id]['position']
	return board._get_child_at_pos(pos['x'], pos['y'])
