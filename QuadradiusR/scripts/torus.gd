extends Control

onready var pickup_sfx = $SFXGroup/PickupSFX2D
onready var putdown_sfx = $SFXGroup/PutdownSFX2D
onready var light_on = $LightGroup/LightOn
onready var light_off = $LightGroup/LightOff

var starting_pos: Vector2



func _ready():
	set_process(false)


func _process(delta):
	self.rect_global_position = get_global_mouse_position() - rect_size/2


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if event is InputEventMouseButton:
		if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
			pickup_sfx.play()
			starting_pos = rect_position
			self.rect_scale = Vector2(1.1, 1.1)
			set_process(true)
		else:
			self.rect_scale = Vector2(1, 1)
			set_process(false)
			rect_position = starting_pos


func _on_hover_start():
	self.light_on.visible = true


func _on_hover_end():
	self.light_on.visible = false
