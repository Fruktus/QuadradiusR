extends PanelContainer

signal is_released(tile)

onready var slot = $TorusSlot

var is_placeable = true
var position: Vector2



func init(position: Vector2):
	self.position = position
	return self


func set_slot(torus: Control):
	if slot.get_child_count() != 0:
		slot.remove_child(slot.get_child(0))
	
	slot.add_child(torus)


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if event is InputEventMouseButton:
		print(event)
		if event.get_button_index() == BUTTON_LEFT and not event.is_pressed():
			print('active', position)
			get_tree().call_group("board", "_on_tile_release", self)
