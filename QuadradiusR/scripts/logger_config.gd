extends Node


func _ready():
	Logger.add_module('ws') \
		.set_output_level(Logger.INFO)
	Logger.add_module('rest') \
		.set_output_level(Logger.INFO)
	Logger.add_module('embedded-server') \
		.set_output_level(Logger.INFO)
