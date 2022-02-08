extends Node2D

onready var anim = $AnimationPlayer
signal clicked



func _on_hover():
	$AnimationPlayer.play("Hover")


func _on_hover_exit():
	$AnimationPlayer.play("Idle")


func _on_button_down():
	$AnimationPlayer.play("Click")
	emit_signal("clicked")


func _on_button_up():
	$AnimationPlayer.play("Hover")
