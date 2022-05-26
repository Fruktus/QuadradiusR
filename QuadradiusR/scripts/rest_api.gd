class_name RestApi
extends HTTPRequest

const MODULE = 'rest'

var url: String
var use_ssl = false
var request_running = false
var request_callback: FuncRef
var request_callback_args = {}
var current_request = {}
var queued_requests = []



func _process_requests():
	if not request_running and not queued_requests.empty():
		current_request = queued_requests.pop_front()
		request_callback = current_request['cb']
		request_callback_args = current_request['cb_args']
		funcref(self, "request").call_funcv(current_request['args'])
		request_running = true


func _on_request_completed(result: int, status_code: int, headers: PoolStringArray, body: PoolByteArray):
	var data = null
	for header in headers:
		if 'application/json' in header:
			data = JSON.parse(body.get_string_from_utf8()).result
			break
		elif 'text/plain' in header:
			data = body.get_string_from_utf8()
			break

	var message = Message.new().init(status_code, str(result), data, headers)
	
	Logger.verbose('HTTP request completed', MODULE)
	Logger.verbose('Response status code: {status_code}'.format({'status_code': status_code}), MODULE)
	Logger.verbose('Response headers: {headers}'.format({'headers': headers}), MODULE)
	Logger.verbose('Response body: {body}'.format({'body': data}), MODULE)
	
	if _redirect_if_needed(status_code, headers):
		return
	
	if request_callback != null:
		request_callback.call_func(message, request_callback_args)
	
	_clear_state()
	_process_requests()


# Returns whether redirect occurs
func _redirect_if_needed(status_code: int, response_headers: PoolStringArray) -> bool:
	if not status_code in [301, 302, 303, 307, 308]:
		return false	# TODO: No other redirects are currently supported
	
	var new_location = url
	for header in response_headers:
		if header.to_lower().begins_with('location:'):
			new_location += header.substr(len('location:'), len(header)).lstrip(' ')
			break
			
	var redirect_headers = current_request['args'][1]
	var redirect_use_ssl = current_request['args'][2]
	
	var cb = current_request['cb']
	var cb_args = current_request['cb_args']
	
	var args = [new_location, redirect_headers, redirect_use_ssl]
	
	if status_code != 303 and len(current_request['args']) > 3:
		args.append_array(current_request['args'].slice(3, len(current_request['args'] - 1)))
	
	# Due to flow interruption clearing state occurs here
	_clear_state()
	_build_request(args, cb, cb_args)
	return true


func _build_request(args: Array, callback: FuncRef, cb_args: Dictionary):
	queued_requests.append({'args': args, 'cb': callback, 'cb_args': cb_args})
	_process_requests()


func _clear_state():
	request_running = false
	request_callback = null
	request_callback_args = {}
	current_request = {}


func get_gateway(cb: FuncRef = null, cb_args: Dictionary = {}):
	return _build_request(["{url}/gateway".format({"url": url}), [], use_ssl], cb, cb_args)


func create_user(username: String, password: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json"]
	var body = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/user".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, body], cb, cb_args)


func authorize(username: String, password: String, cb: FuncRef = null, cb_args: Dictionary = {}):
	var headers = ["Content-Type: application/json"]
	var body = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/authorize".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, body], cb, cb_args)


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
	var body = JSON.print({'subject_id': opponent_uuid})
	return _build_request(["{url}/game_invite".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, body], cb, cb_args)


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
