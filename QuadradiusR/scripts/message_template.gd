class_name Message

var result: int  # the result of the executed operation, http code	# TODO: change var name to status code
var message: String  # message returned by the operation (mostly for errors)	# TODO: rename to response
var body  # generic variable for additional data returned by executed operation
var headers: PoolStringArray


func init(status_code: int, response: String, body=null, headers=null):
	self.result = status_code	# TODO: rename field
	self.message = response		# TODO: rename field
	self.body = body
	self.headers = headers
	return self


func _to_string():
	return "Message(result:{result}, message:{message}, body:{body})".format(
		{"result": result, "message": message, "body": body})
