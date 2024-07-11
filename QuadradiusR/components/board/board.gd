extends Control

onready var board = $BoardContainer
const tile_template = preload("res://components/tile/tile.tscn")
const torus_template = preload("res://components/torus/torus.tscn")

var toruses_by_id = {}
var tiles_by_id = {}
var orb_tiles_by_id = {}
var board_size: Vector2
var active_torus: Node



func _ready():
	var board_size = Context.game_state.get_board_size()
	var player_pieces = Context.game_state.get_pieces()
	
	self.board_size = Vector2(board_size['x'], board_size['y'])
	board.columns = board_size.x
	
	_init_tiles()
	_init_toruses(player_pieces)


# # # # #
# INIT  #
# # # # #
func _init_tiles():
	for i in range(board_size.x * board_size.y):
		var new_tile = tile_template.instance().init(Vector3(i % int(board_size.x), int(i / board_size.x), 0))
		board.add_child(new_tile)
	
	var tiles = Context.game_state.get_tiles()
	for tile_id in tiles.keys():
		var pos = tiles[tile_id]['position']
		var tile = _get_child_at_pos(pos['x'], pos['y'])
		tile.tile_id = tile_id
		tile.tile_pos.z = tiles[tile_id]['elevation']
		tiles_by_id[tile_id] = tile


func _init_toruses(player_pieces: Dictionary):
	for piece_id in player_pieces.keys():
		var piece_data = player_pieces[piece_id]
		var tile = get_tile_by_id(piece_data['tile_id'])
		var color = Torus.COLORS.RED if piece_data['owner_id'] == Context.user_id else Torus.COLORS.BLUE
		var torus = torus_template.instance().init(self, tile, piece_data['owner_id'], piece_id, color)
		_get_child_at_pos(tile.tile_pos.x, tile.tile_pos.y).set_slot(torus)
		toruses_by_id[piece_id] = torus


# # # # #
# UTILS #
# # # # #
func _get_child_at_pos(x: int, y: int):
	return board.get_child(y * board_size.x + x)


func _get_child_at_idx(idx: int):
	return board.get_child(idx)


func get_torus_by_id(piece_id: String) -> Torus:
	return toruses_by_id[piece_id]


func get_tile_by_id(tile_id: String) -> Tile:
	return tiles_by_id[tile_id]


func get_tile_by_orb_id(orb_id: String) -> Tile:
	return orb_tiles_by_id[orb_id]


func move_torus_by_tiles(source_pos: Vector2, dest_pos: Vector2):
	var src_tile = _get_child_at_pos(source_pos.x, source_pos.y)
	var dest_tile = _get_child_at_pos(dest_pos.x, dest_pos.y)
	var moved_torus = src_tile.get_piece()
	var is_colliding = dest_tile.has_piece()
	src_tile.del_piece()
	dest_tile.set_slot(moved_torus)
	moved_torus.make_move(src_tile, dest_tile, is_colliding)


func spawn_orb_on_tile_id(orb_id: String, tile_id: String):
	var tile = get_tile_by_id(tile_id)
	tile.spawn_orb()
	orb_tiles_by_id[orb_id] = tile


# # # # # # # # # # # # #
# BOARD GROUP HANDLERS  #
# # # # # # # # # # # # #
func _torus_pickup(torus: Node):
	# After picking up torus, move it to top of the tree, so it won't get covered
	# by other sprites. After putting down, place back on original position, unless
	# it was a new tile, in this case move to it
	self.active_torus = torus
	torus.current_tile.del_piece()
	add_child(torus)


func _torus_putdown(torus: Node):
	remove_child(self.active_torus)

	var dest_tile_pos = (get_global_mouse_position() - rect_global_position) / (get_child(0).get_child(0).rect_size * rect_scale)
	var x = int(dest_tile_pos.x)
	var y = int(dest_tile_pos.y)
	
	if 0 > x or x >= board_size.x or 0 > y or y >= board_size.y:
		self.active_torus.current_tile.set_slot(self.active_torus)
		return
	
	var target_tile: Tile = _get_child_at_pos(x, y)
	if self.active_torus.current_tile == target_tile:
		self._get_child_at_pos(x, y).set_slot(self.active_torus)
		return
	if torus.should_move_torus(self.active_torus.current_tile, target_tile):
		var is_colliding = target_tile.has_piece()
		self._get_child_at_pos(x, y).set_slot(self.active_torus)
		torus.make_move(self.active_torus.current_tile, target_tile, is_colliding)
		NetworkHandler.ws_api.make_move(torus.piece_id, target_tile.tile_id)
		return
	
	self.active_torus.current_tile.set_slot(self.active_torus)
