extends Popup

onready var powerup_list = $PowerupListContainer/PowerupList

const power_list_row_template = preload("res://components/torus/powerups/piece_power_list_row.tscn")



func add_powerup(power_def_id: String, power_name: String, power_count = 1):
	var power_list_row = power_list_row_template.instance().init(power_def_id, power_name, power_count)
	powerup_list.add_child(power_list_row)


func add_powerup_charges(power_def_id: String, charges: int = 1):
	# TODO Will need to expand the size of the popup or it will close when clicked outside of
	for power_row in powerup_list.get_children():
		if power_row.power_def_id == power_def_id:
			power_row.add_power_charges(charges)


func use_power(power_def_id: String):
	for power_row in powerup_list.get_children():
		if power_row.power_def_id == power_def_id:
			power_row.use_power()
