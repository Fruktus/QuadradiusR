class_name PowerupRule

enum powerup_types {EFFECT, TORUS, TILE}
# check if the tile change is one of four cardinals
# if the tile is steppable
# if elevations is correct
# if it contains opponent or own toruses
#	and if so if can stand there

# TODO split into methods as much as possible, so that other inheriting rules
# will be able to reuse the code (for ex for torus destruction)

func get_name():
	pass


func can_make_move(source_tile: Node, dest_tile: Node) -> bool:
	return false
