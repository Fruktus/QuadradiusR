extends Node2D

const LOBBY_SCENE = preload("res://scenes/lobby.tscn")



func _on_login(is_guest, remember_pw, username, password):
	var user_data = {
		"is_guest": is_guest,
		"remember_pw": remember_pw,
		"username": username,
		"password": password
	}

	if is_guest:
		Logger.error('Guest login not suported (yet)')
		return

	NetworkHandler.authorize_user(username, password, funcref(self, "_cb_login_done"), user_data)


func _cb_login_done(is_authorized, user_data, message: Message):
	Logger.info('Logged in')
	Logger.debug('Login info: is_authorized={is_authorized}, user_data={user_data}'.format({
		'is_authorized': is_authorized,
		'user_data': user_data,
	}))

	NetworkHandler.rest_api.get_user_me(NetworkHandler.token, funcref(self, "_dbg_print"))  # DEBUG
	if is_authorized:
		_join_lobby()
	else:
		Logger.warn('Failed to authorize, auto-registering user')
		NetworkHandler.create_user(user_data['username'], user_data['password'], null, {})  # DEBUG
		NetworkHandler.authorize_user(user_data['username'], user_data['password'], funcref(self, "_cb_second_login_done"), user_data)  # DEBUG


func _cb_second_login_done(is_authorized, user_data, message: Message):
	if is_authorized:
		_cb_login_done(true, user_data, message)
	else:
		Logger.error('Failed to auto register')




func _dbg_print(message, data):  # DEBUG
	Logger.debug('Me: {message} + {data}'.format({
		'message': message,
		'data': data,
	}))


func _join_lobby():
	NetworkHandler.join_lobby(funcref(self, "_cb_lobby_joined"))

func _cb_lobby_joined():
	get_tree().change_scene_to(LOBBY_SCENE)
