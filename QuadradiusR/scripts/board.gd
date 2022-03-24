extends Control

onready var board = $BoardContainer
const tile_template = preload("res://prefabs/tile.tscn")
const torus_template = preload("res://prefabs/torus.tscn")  # Do we want this to be instanced here? or in manager?

var board_size: int
var active_torus: Node
var torus_source_slot: Node


func _ready():  # TMP, used to test initialisation
	init()


func init(board_size: int = 10, player_pieces: int = 20):
	self.board_size = board_size
	board.columns = board_size
	
	_init_tiles()
	_init_toruses(player_pieces)


func _get_child_at_pos(x: int, y: int):
	return board.get_child(y * board_size + x)


func _init_tiles():
	for i in range(board_size*board_size):
		var new_tile = tile_template.instance().init(Vector3(i % board_size, i / board_size, 0))
		board.add_child(new_tile)


func _init_toruses(player_pieces: int):
	for i in range(player_pieces):
		var player1_torus = torus_template.instance().init(self, Torus.COLORS.RED)
		var player2_torus = torus_template.instance().init(self, Torus.COLORS.BLUE)
		
		board.get_child(i).set_slot(player1_torus)
		board.get_child(board_size * board_size - 1 - i).set_slot(player2_torus)


# After picking up torus, move it to top of the tree, so it won't get covered
# by other sprites. After putting down, place back on original position, unless
# it was a new tile, in this case move to it
func _torus_pickup(torus: Node):
	self.active_torus = torus
	self.torus_source_slot = torus.get_parent()
	torus_source_slot.remove_child(torus)
	add_child(torus)


func _torus_putdown(torus: Node):
	remove_child(self.active_torus)

	var dest_tile_pos = get_global_mouse_position() / (get_child(0).get_child(0).rect_size * rect_scale)
	var x = int(dest_tile_pos.x)
	var y = int(dest_tile_pos.y)
	
	if 0 > x or x >= board_size or 0 > y or y >= board_size:
		self.torus_source_slot.add_child(self.active_torus)
		return
	
	if torus.should_move_torus(torus_source_slot.get_parent(), _get_child_at_pos(x, y)):
		self._get_child_at_pos(x, y).set_slot(self.active_torus)
		return
	
	self.torus_source_slot.add_child(self.active_torus)
