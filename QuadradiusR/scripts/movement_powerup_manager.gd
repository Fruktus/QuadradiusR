class_name MovementPowerupManager

const torus_base_template = preload("res://scripts/powerups/torus_base.gd")

var move_rules_dict = Dictionary()  # power: Object -> rule: FuncRef



func _init():
	var base = torus_base_template.new()
	move_rules_dict[base.get_name()] = base


func can_make_move(source_tile: Node, dest_tile: Node) -> bool:
	for rule in move_rules_dict.values():
		if rule.can_make_move(source_tile, dest_tile):
			return true
	
	return false
	# movement rulesets should provide callable functions which calculate if they allow movement
	# they should probably also gain access to board
	# if any single one of them allows movement, then we allow it (because they're exclusive (i think all of them)
	# how to handle tile-specific movement bonuses like hotspots? include them in basic check? add them separately?
	# for k, v in move_rules_dict:
	#	if v(src, dst):
	#		return true
	# return false
	
	# hotspot can be both tile and torus powerup (but it would have to be added to all toruses
	# once added, the special rule would look for the hotspot installed on tile
	# if installed, allow movement
	
	# TODO if destroying piece, should return something else than true/false


# tripwire?
# if can make move, check if can (and will) destroy opponent piece
