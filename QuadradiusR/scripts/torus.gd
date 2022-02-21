extends Control

onready var pickup_sfx = $PickupSFX2D
onready var putdown_sfx = $PutdownSFX2D
onready var light_on = $LightOn
onready var light_off = $LightOff





func _on_click(viewport, event: InputEvent, shape_idx):
	if event is InputEventMouseButton:
		if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
			print(viewport, event, shape_idx)
			pickup_sfx.play()


func _on_hover_start():
	self.light_on.visible = true


func _on_hover_end():
	self.light_on.visible = false
