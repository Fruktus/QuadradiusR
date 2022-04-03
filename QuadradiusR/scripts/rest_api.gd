class_name RestApi
extends HTTPRequest

var url
var use_ssl = false
var request_callbacks = []



func _on_request_completed(result, response_code, headers, body):
	var json = JSON.parse(body.get_string_from_utf8())
	print(result)
	print(response_code)
	print(headers)
	print(json.result)
	request_callbacks.pop_front().call_func(response_code, json.result)


func get_gateway():
	request_callbacks.append(funcref(self, "_handle_get_gateway"))
	request("{url}/gateway".format({"url": url}), [], use_ssl)

func _handle_get_gateway(response_code: int, result: Dictionary):
	# TODO parse the json to get out gateway and return it
	pass


func create_user(username: String, password: String):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	
	request_callbacks.append(funcref(self, "_handle_create_user"))
	request("{url}/user".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query)

func _handle_create_user(response_code: int, result: Dictionary):
	# 201 if worked
	# 400 if did not
	pass


func authorize(username: String, password: String):
	var headers = ["Content-Type: application/json"]
	var query = JSON.print({'username': username, 'password': password})
	
	request_callbacks.append(funcref(self, "_handle_authorize"))
	request("{url}/authorize".format({"url": url}), headers, use_ssl, HTTPClient.METHOD_POST, query)

func _handle_authorize(response_code: int, result: Dictionary):
	pass


func get_lobby(token: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	request_callbacks.append(funcref(self, "_handle_get_lobby"))
	request("{url}/lobby".format({"url": url}), headers, use_ssl)

func _handle_get_lobby(response_code: int, result: Array):
	# result is an array instead of dict
	# looks like this [{id:@main, name:Main}]
	pass


func get_user(token: String, user_id: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	request_callbacks.append(funcref(self, "_handle_get_lobby"))
	request("{url}/user/{user_id}".format({"url": url, "user_id": user_id}), headers, use_ssl)

func _handle_get_user(response_code: int, result: Dictionary):
	pass


func get_user_me(token: String):
	var headers = ["Authorization:{token}".format({"token": token})]
	request_callbacks.append(funcref(self, "_handle_get_lobby"))
	request("{url}/user/@me".format({"url": url}), headers, use_ssl)

func _handle_get_user_me(response_code: int, result: Dictionary):
	pass
