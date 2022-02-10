class_name Message

var result: bool  # the result of the executed operation
var message: String  # message returned by the operation (mostly for errors)
var body  # generic variable for additional data returned by executed operation



func init(result: bool, message: String, body=null):
	self.result = result
	self.message = message
	self.body = body
