class_name RestApi
extends HTTPRequest

signal request_processed(req_id, message)

var url
var use_ssl = false
var request_running = false
var current_req_id = 0
var queued_requests = []



func _process_requests():
	if not request_running and not queued_requests.empty():
		var req = queued_requests.pop_front()
		current_req_id = req['req_id']
		funcref(self, "request").call_funcv(req['args'])
		request_running = true


func _on_request_completed(result: int, response_code: int, headers: PoolStringArray, body: PoolByteArray):
	var json = JSON.parse(body.get_string_from_utf8())
	var message = Message.new().init(response_code, str(result), json.result)

	print('rq cpl ', response_code) # DEBUG
	print('rq cpl ', headers) #  DEBUG
	print('rq cpl ', json.result) # DEBUG
	
	emit_signal("request_processed", current_req_id, message)
	request_running = false
	current_req_id = 0
	_process_requests()


func _build_request(args: Array):
	var req_id = OS.get_ticks_msec()
	queued_requests.append({'req_id': req_id, 'args': args})
	_process_requests()
	return req_id


func get_gateway():
	return _build_request(["{url}/gateway".format({"url": url}), [], use_ssl])


func create_user(username: String, password: String):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/user".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query])


func authorize(username: String, password: String):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/authorize".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query])


func get_lobby(token: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/lobby".format({"url": url}), headers, use_ssl])


func get_user(token: String, user_id: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/{user_id}".format({"url": url, "user_id": user_id}), headers, use_ssl])


func get_user_me(token: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/@me".format({"url": url}), headers, use_ssl])
