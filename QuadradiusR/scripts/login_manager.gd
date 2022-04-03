extends Node2D



func _on_login(is_guest, remember_pw, username, password):
	NetworkHandler.create_user_and_connect_ws()
#	get_tree().change_scene("res://scenes/lobby.tscn")
