extends Node

onready var anim = $AnimationPlayer
signal toggled(button_pressed)



func pressed() -> bool:
	return $Button.pressed


func _on_toggled(button_pressed):
	if button_pressed:
		anim.play("Pressed")
		emit_signal("toggled", true)
	else:
		anim.play("Depressed")
		emit_signal("toggled", false)
