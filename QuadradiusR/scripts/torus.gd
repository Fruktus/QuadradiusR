extends Control

onready var pickup_sfx = $SFXGroup/PickupSFX2D
onready var putdown_sfx = $SFXGroup/PutdownSFX2D
onready var light_on = $LightGroup/LightOn
onready var light_off = $LightGroup/LightOff

var board_scale = Vector2(1, 1)
var starting_pos: Vector2
var original_parent: Node
var board: Node
# TODO some way to tell whose torus it is


func _ready():
	set_process(false)


func _process(delta):
	self.rect_global_position = get_global_mouse_position() - rect_size/2 * board_scale


func init(board):
	self.board_scale = board.rect_scale
	self.board = board
	return self


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if event is InputEventMouseButton:
		if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
			pickup_sfx.play()
			
			original_parent = get_parent()
			print('from', original_parent.get_parent().position)
			get_parent().remove_child(self)
			print(board.rect_size)
			board.add_child(self)
			
			starting_pos = rect_position
			self.rect_scale = Vector2(1.1, 1.1)
			set_process(true)
		else:
			set_process(false)
			self.rect_scale = Vector2(1, 1)
			board.remove_child(self)
			board.active_tile.slot.add_child(self)
#			original_parent.add_child(self)
			rect_position = starting_pos


func _on_hover_start():
	self.light_on.visible = true
	print(rect_position)


func _on_hover_end():
	self.light_on.visible = false
