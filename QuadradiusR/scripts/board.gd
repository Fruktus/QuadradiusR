extends Control

onready var board = $BoardContainer
const tile_template = preload("res://prefabs/tile.tscn")
const torus_template = preload("res://prefabs/torus.tscn")  # Do we want this to be instanced here? or in manager?

var board_size: int
var active_torus: Node
var torus_parent: Node


func _ready():  # TMP, used to test initialisation
	init()


func init(board_size: int = 10, player_pieces: int = 20):
	self.board_size = board_size
	board.columns = board_size
	
	_init_tiles()
	_init_toruses(player_pieces)


func _get_child_at_pos(x: int, y: int):
	return get_child(y * board_size + x)


func _init_tiles():
	for i in range(board_size*board_size):
		var new_tile = tile_template.instance().init(Vector2(i % board_size, i / board_size))
		board.add_child(new_tile)


func _init_toruses(player_pieces: int):
	for i in range(player_pieces):
		var player1_torus = torus_template.instance().init(self)
		var player2_torus = torus_template.instance().init(self)
		
		board.get_child(i).set_slot(player1_torus)
		board.get_child(board_size * board_size - 1 - i).set_slot(player2_torus)


# After picking up torus, move it to top of the tree, so it won't get covered
# by other sprites. After putting down, place back on original position, unless
# it was a new tile, in this case move to it
func _torus_pickup(torus: Node):
	self.active_torus = torus
	self.torus_parent = torus.get_parent()
	print('from', torus_parent.get_parent().position)  # DEBUG
	torus.get_parent().remove_child(torus)
	add_child(torus)


func _torus_putdown():
	print('putting down')  # DEBUG
	remove_child(self.active_torus)
	torus_parent.add_child(active_torus)


func _on_tile_release(active_tile: Node):
	print('putting down new tile')  # DEBUG
	self.active_torus.get_parent().remove_child(self.active_torus)
	active_tile.set_slot(self.active_torus)
