extends Node2D

signal challenge_issued(username)
signal player_hover_start(username)
signal player_hover_end(username)

onready var player_vbox = $ScrollContainer/PlayerListVBox
onready var player_joined_sfx = $PlayerJoinedSFX
onready var new_player_joined_sfx = $NewPlayerJoinedSFX
onready var player_left_sfx = $PlayerLeftSFX

const player_template = preload("res://prefabs/player_list_row.tscn")



func receive_challenge(username):
	for child in player_vbox.get_children():
		if child.username == username:
			child.receive_challenge()


func add_player(username: String, is_current = false):
	var new_player = player_template.instance()
	new_player.username = username

	new_player.connect("player_hover_start", self, "_on_hover_start")
	new_player.connect("player_hover_end", self, "_on_hover_start")
	
	if is_current:
		new_player.is_self_player = true
		player_joined_sfx.play()
	else:
		new_player_joined_sfx.play()
	player_vbox.add_child(new_player)


func remove_player(username: String):
	for child in player_vbox.get_children():
		if child.username == username:
			player_left_sfx.play()
			child.queue_free()


func _on_hover_start(username):
	emit_signal("player_hover_start", username)


func _on_hover_end(username):
	emit_signal("player_hover_end")
