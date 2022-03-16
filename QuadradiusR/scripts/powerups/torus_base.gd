extends PowerupRule

var powerup_type = PowerupRule.powerup_types.TORUS



func get_name():
	return "torus_base"


func get_move_rule():
	return funcref(self, "can_make_move")


func can_make_move(source_tile, dest_tile) -> bool:
	var s_pos: Vector3 = source_tile.get_pos()
	var d_pos: Vector3 = dest_tile.get_pos()
	
	if not dest_tile.is_steppable():
		return false
	
	if d_pos.z - s_pos.z > 1:  # if difference in elevation is greater than 1
		return false
	
	if abs(d_pos.x - s_pos.x) > 1:  # if difference in x is greater than 1
		return false
	
	if abs(d_pos.y - s_pos.y) > 1:  # if difference in y is greater than 1
		return false

	if d_pos.x != s_pos.x and d_pos.y != s_pos.y:  # if both directions changed
		return false
	
	return true
