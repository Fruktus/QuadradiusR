extends PanelContainer

onready var bg = $BG
onready var power_charges_label = $HBoxContainer/PowerCount
onready var power_name_label = $HBoxContainer/PowerName
onready var help_sign = $HBoxContainer/HelpSign

const INACTIVE_COLOR = Color(1.0, 0.0, 0.0, 1.0)
const ACTIVE_COLOR = Color("#381b16")

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
	# TODO emit signal or smth

func _on_hover_enter():
	bg.visible = true
	power_charges_label.add_color_override("font_color", ACTIVE_COLOR)
	power_name_label.add_color_override("font_color", ACTIVE_COLOR)
	help_sign.add_color_override("font_color", ACTIVE_COLOR)


func _on_hover_exit():
	bg.visible = false
	power_charges_label.add_color_override("font_color", INACTIVE_COLOR)
	power_name_label.add_color_override("font_color", INACTIVE_COLOR)
	help_sign.add_color_override("font_color", INACTIVE_COLOR)


func _on_click():
	use_power()
