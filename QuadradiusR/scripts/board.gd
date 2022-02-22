extends Control

onready var board = $BoardContainer
const tile_template = preload("res://prefabs/tile.tscn")
const torus_template = preload("res://prefabs/torus.tscn")  # Do we want this to be instanced here? or in manager?

var board_size: int
var active_tile: Node


func _ready():
	init()


func init(board_size: int = 12, player_pieces: int = 20):
	self.board_size = board_size
	board.columns = board_size
	
	for i in range(board_size*board_size):
		var new_tile = tile_template.instance().init(Vector2(i % board_size, i / board_size))
		new_tile.connect("is_released", self, "_on_tile_release")
		board.add_child(new_tile)
	
	for i in range(player_pieces):
			board.get_child(i).set_slot(torus_template.instance().init(self))
			board.get_child(board_size * board_size - 1 - i).set_slot(
				torus_template.instance().init(self))


func _get_child_at_pos(x: int, y: int):
	return get_child(y * board_size + x)


func _on_tile_release(node):
	active_tile = node
