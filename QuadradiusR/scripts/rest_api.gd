class_name RestApi
extends HTTPRequest

var url: String
var use_ssl = false
var request_running = false
var request_callback: FuncRef
var request_callback_args = {}
var queued_requests = []



func _process_requests():
	if not request_running and not queued_requests.empty():
		var req = queued_requests.pop_front()
		request_callback = req['cb']
		request_callback_args = req['cb_args']
		funcref(self, "request").call_funcv(req['args'])
		request_running = true


func _on_request_completed(result: int, response_code: int, headers: PoolStringArray, body: PoolByteArray):
	var data = null
	for header in headers:
		if 'application/json' in header:
			data = JSON.parse(body.get_string_from_utf8()).result
			break
		elif 'text/plain' in header:
			data = body.get_string_from_utf8()
			break

	var message = Message.new().init(response_code, str(result), data, headers)
	
	print('rq cpl:', response_code, ', headers:', headers, ', data:', data) # DEBUG
	
	if request_callback != null:
		request_callback.call_func(message, request_callback_args)
	
	request_running = false
	request_callback = null
	request_callback_args = {}
	_process_requests()


func _build_request(args: Array, callback: FuncRef, cb_args: Dictionary):
	queued_requests.append({'args': args, 'cb': callback, 'cb_args': cb_args})
	_process_requests()


func get_gateway(cb: FuncRef = null, cb_args: Dictionary = {}):
	return _build_request(["{url}/gateway".format({"url": url}), [], use_ssl], cb, cb_args)


func create_user(username: String, password: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/user".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query], cb, cb_args)


func authorize(username: String, password: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/authorize".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query], cb, cb_args)


func get_lobby(token: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/lobby/@main".format({"url": url}), headers, use_ssl], cb, cb_args)


func get_user(token: String, user_id: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/{user_id}".format({"url": url, "user_id": user_id}), headers, use_ssl], cb, cb_args)


func get_user_me(token: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/@me".format({"url": url}), headers, use_ssl], cb, cb_args)


func invite_player(token: String, opponent_uuid: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json", "Authorization:{token}".format({"token": token})]
	var query = JSON.print({'subject_id': opponent_uuid})
	return _build_request(["{url}/game_invite".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query], cb, cb_args)


func get_game_invite(token: String, game_id: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json", "Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/game_invite/{id}".format({"url": url, "id": game_id}), headers, use_ssl, HTTPClient.METHOD_GET, ""], cb, cb_args)


func accept_game_invite(token: String, game_id: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json", "Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/game_invite/{id}/accept".format({"url": url, "id": game_id}), headers, use_ssl, HTTPClient.METHOD_POST, ""], cb, cb_args)


func get_game(token: String, game_id: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json", "Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/game/{id}".format({"url": url, "id": game_id}), headers, use_ssl, HTTPClient.METHOD_GET, ""], cb, cb_args)


func get_game_state(token: String, game_id: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json", "Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/game/{id}/state".format({"url": url, "id": game_id}), headers, use_ssl, HTTPClient.METHOD_GET, ""], cb, cb_args)
