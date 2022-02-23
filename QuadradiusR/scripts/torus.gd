extends Control

onready var pickup_sfx = $SFXGroup/PickupSFX2D
onready var putdown_sfx = $SFXGroup/PutdownSFX2D
onready var light_on = $LightGroup/LightOn
onready var collision_detector = $MouseDetector/CollisionShape2D

const starting_pos = Vector2(50, 50)

var board: Control
var is_held = false
var can_interact = true
# TODO some way to tell whose torus it is



func _ready():
	set_process(false)


func _process(delta: float):
	self.rect_global_position = get_global_mouse_position() - rect_size/2 * board.rect_scale


func init(board):
	self.board = board
	return self


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if can_interact:
		if event is InputEventMouseButton:
			if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
				_begin_drag()
			else:
				_end_drag()


func _begin_drag():
	is_held = true
	pickup_sfx.play()
	get_tree().call_group("torus", "set_interaction", false)
	get_tree().call_group("board", "_torus_pickup", self)
	self.rect_scale = Vector2(1.1, 1.1)
	set_process(true)


func _end_drag():
	set_process(false)
	get_tree().call_group("torus", "set_interaction", true)
	get_tree().call_group("board", "_torus_putdown")
	is_held = false
	# TODO play putdown sfx, but always or only on tile change?
	self.rect_scale = Vector2(1, 1)
	rect_position = self.starting_pos


func set_interaction(can_interact):
	if not is_held:
		self.can_interact = can_interact
		collision_detector.disabled = !can_interact


func _on_hover_start():
	self.light_on.visible = true


func _on_hover_end():
	self.light_on.visible = false
