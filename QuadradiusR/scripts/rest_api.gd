class_name RestApi
extends HTTPRequest


var url
var use_ssl = false
var request_running = false
var request_callback: FuncRef
var queued_requests = []



func _process_requests():
	if not request_running and not queued_requests.empty():
		var req = queued_requests.pop_front()
		request_callback = req['cb']
		funcref(self, "request").call_funcv(req['args'])
		request_running = true


func _on_request_completed(result: int, response_code: int, headers: PoolStringArray, body: PoolByteArray):
	var json = JSON.parse(body.get_string_from_utf8())
	var message = Message.new().init(response_code, str(result), json.result)
	
	print('rq cpl ', response_code) # DEBUG
	print('rq cpl ', headers) #  DEBUG
	print('rq cpl ', json.result) # DEBUG
	
	if request_callback != null:
		request_callback.call_func(message)
	
	request_running = false
	request_callback = null
	_process_requests()


func _build_request(args: Array, callback: FuncRef):
	queued_requests.append({'args': args, 'cb': callback})
	_process_requests()


func get_gateway(cb: FuncRef = null):
	return _build_request(["{url}/gateway".format({"url": url}), [], use_ssl], cb)


func create_user(username: String, password: String, cb: FuncRef = null):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/user".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query], cb)


func authorize(username: String, password: String, cb: FuncRef = null):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	return _build_request(["{url}/authorize".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query], cb)


func get_lobby(token: String, cb: FuncRef = null):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/lobby".format({"url": url}), headers, use_ssl], cb)


func get_user(token: String, user_id: String, cb: FuncRef = null):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/{user_id}".format({"url": url, "user_id": user_id}), headers, use_ssl], cb)


func get_user_me(token: String, cb: FuncRef = null):
	var headers = ["Authorization:{token}".format({"token": token})]
	return _build_request(["{url}/user/@me".format({"url": url}), headers, use_ssl], cb)
