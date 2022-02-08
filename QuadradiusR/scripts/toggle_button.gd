extends Node

onready var anim = $AnimationPlayer
signal toggled(button_pressed)




func _on_toggled(button_pressed):
	if button_pressed:
		$AnimationPlayer.play("Pressed")
		emit_signal("toggled", true)
	else:
		$AnimationPlayer.play("Depressed")
		emit_signal("toggled", false)
