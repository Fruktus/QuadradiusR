extends HBoxContainer

onready var power_charges_label = $PowerCount
onready var power_name_label = $PowerName

var power_charges: int
var power_name: String
var power_def_id: String



func _ready():
	power_charges_label.text = str(power_charges)
	power_name_label.text = power_name


func init(power_def_id: String, power_name: String, charges=1):
	self.power_def_id = power_def_id
	self.power_charges = charges
	self.power_name = power_name
	return self


func add_power_charges(charges=1):
	power_charges += charges
	power_charges_label.text = str(power_charges)


func use_power():
	power_charges -= 1
	
	if power_charges == 0:
		queue_free()

	power_charges_label.text = str(power_charges)
