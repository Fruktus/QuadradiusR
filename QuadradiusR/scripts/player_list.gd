extends Node2D

signal challenge_accepted(game_invite_id, opponent_id)
signal player_hover_start(username)
signal player_hover_end(username)

onready var player_vbox = $ScrollContainer/PlayerListVBox
onready var player_joined_sfx = $PlayerJoinedSFX
onready var new_player_joined_sfx = $NewPlayerJoinedSFX
onready var player_left_sfx = $PlayerLeftSFX

const player_template = preload("res://prefabs/player_list_row.tscn")
var uuid_to_active_invites = {}  # uuid -> game invite


func receive_challenge(uuid: String):
	for child in player_vbox.get_children():
		if child.uuid == uuid:
			child.receive_challenge()


func add_player(username: String, uuid: String, is_current=false):
	var new_player = player_template.instance().init(username, uuid, is_current)

	new_player.connect("player_hover_start", self, "_on_hover_start")
	new_player.connect("player_hover_end", self, "_on_hover_end")
	new_player.connect("player_clicked", self, "_on_player_clicked")
	
	if is_current:
		player_joined_sfx.play()
	else:
		new_player_joined_sfx.play()
	
	player_vbox.add_child(new_player)


func remove_player(uuid: String):
	for child in player_vbox.get_children():
		if child.uuid == uuid:
			player_left_sfx.play()
			child.queue_free()


func _on_hover_start(username: String):
	emit_signal("player_hover_start", username)


func _on_hover_end(username: String):
	emit_signal("player_hover_end", username)


func _on_player_clicked(uuid: String):
	if uuid_to_active_invites.has(uuid):
		emit_signal("challenge_accepted", uuid_to_active_invites[uuid], uuid)
	else:
		NetworkHandler.invite_player(uuid)


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _lobby_joined(lobby_id: String, user_id: String, user_username: String):
	add_player(user_username, user_id, false)

func _lobby_left(lobby_id: String, user_id: String):
	uuid_to_active_invites.erase(user_id)
	remove_player(user_id)

func _game_invite_received(game_invite_id: String, from_id: String,
		from_username: String, subject_id: String, subject_username: String):
	uuid_to_active_invites[from_id] = game_invite_id
	receive_challenge(from_id)
