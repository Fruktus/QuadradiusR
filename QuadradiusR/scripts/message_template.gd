class_name Message

var result: int  # the result of the executed operation, http code
var message: String  # message returned by the operation (mostly for errors)
var body  # generic variable for additional data returned by executed operation



func init(result: int, message: String, body=null):
	self.result = result
	self.message = message
	self.body = body
	return self


func _to_string():
	return "Message(result:{result}, message:{message}, body:{body})".format(
		{"result": result, "message": message, "body": body})
