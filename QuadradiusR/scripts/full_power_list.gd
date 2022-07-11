extends PanelContainer

onready var scroll_container = $ ScrollContainer
onready var powers_list = $ScrollContainer/PowerListContainer

const full_power_list_row_template = preload("res://prefabs/full_power_list_row.tscn")

var powerup_def_id_to_piece_ids = {}  # power_def_id: String -> {piece_id: String -> charges: int}



func _ready():
	scroll_container.get_h_scrollbar().visible = false


func add_powerup(power_def_id: String, power_name: String, piece_id: String, power_count = 1):
	if powerup_def_id_to_piece_ids.has(power_def_id):
		var power_def_entry = powerup_def_id_to_piece_ids[power_def_id]
		
		if power_def_entry.has(piece_id):
			power_def_entry[piece_id] += power_count
		else:
			power_def_entry[piece_id] = power_count
		
		for power_row in powers_list.get_children():
			if power_row.power_def_id == power_def_id:
				power_row.add_power_charges(power_count)
	else:
		powerup_def_id_to_piece_ids[power_def_id] = {piece_id: 1}
		
		var full_power_list_row = full_power_list_row_template.instance().init(
			power_def_id, power_name, power_count)
		powers_list.add_child(full_power_list_row)


func select_power(power_def_id: String):
	# TODO later on will be used to highlight all pieces containing specified power
	pass


func use_powerup(power_def_id: String, piece_id: String):
	powerup_def_id_to_piece_ids[power_def_id][piece_id] -= 1
	
	for power_row in powers_list.get_children():
		if power_row.power_def_id == power_def_id:
			power_row.use_power()
