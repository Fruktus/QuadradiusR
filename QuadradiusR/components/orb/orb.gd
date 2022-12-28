extends Node2D

onready var anim = $AnimationPlayer



func spawn():
	anim.play("OrbAppear")


func collect():
	anim.play("OrbCollect")


func rehash():
	pass


func destroy():
	anim.play("OrbDestroy")
