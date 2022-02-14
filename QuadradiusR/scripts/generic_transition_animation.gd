extends Node2D

onready var anim = $AnimationPlayer
signal animation_finished(animation_name)

const ANIMATION_NAME = "default"



func play_animation(animation_name: String  = ANIMATION_NAME):
	anim.play(animation_name)	
	
func _on_animation_finished(anim_name: String):
	# Propagate the signal
	emit_signal("animation_finished", anim_name)
