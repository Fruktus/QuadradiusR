extends Node2D

const GAME_SCENE = preload("res://scenes/game.tscn")



func _ready():
	get_tree().change_scene_to(GAME_SCENE)  # DEBUG
