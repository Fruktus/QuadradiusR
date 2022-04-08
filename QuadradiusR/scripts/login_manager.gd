extends Node2D

const LOBBY_SCENE = preload("res://scenes/lobby.tscn")



func _on_login(is_guest, remember_pw, username, password):
	var user_data = {
		"is_guest": is_guest,
		"remember_pw": remember_pw,
		"username": username,
		"password": password
	}
	NetworkHandler.create_user('asd', '', null, {})
	NetworkHandler.create_user('test', '', null, {})
	NetworkHandler.authorize_user(username, password, funcref(self, "_cb_login_done"), user_data)


func _cb_login_done(is_authorized, user_data, message: Message):
	print('login done ', is_authorized, ' ', user_data)
	NetworkHandler.rest_api.get_user_me(NetworkHandler.token, funcref(self, "_dbg_print"))  # DEBUG
	if is_authorized:
		_join_lobby()
	else:
		print('failed to authorize: ', message['result'])

func _dbg_print(message, data):  # DEBUG
	print('me: ', message, ' + ', data)  # DEBUG

func _join_lobby():
	NetworkHandler.join_lobby(funcref(self, "_cb_lobby_joined"))


func _cb_lobby_joined():
	get_tree().change_scene_to(LOBBY_SCENE)
