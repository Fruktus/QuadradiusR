extends Node2D

onready var anim = $AnimationPlayer
signal clicked



func _on_hover():
	anim.play("Hover")


func _on_hover_exit():
	anim.play("Idle")


func _on_button_down():
	anim.play("Click")
	emit_signal("clicked")


func _on_button_up():
	anim.play("Hover")
