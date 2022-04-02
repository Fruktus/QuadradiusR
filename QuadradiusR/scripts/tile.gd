class_name Tile
extends PanelContainer

onready var slot = $TorusSlot
onready var dirt_a = $DirtA
onready var dirt_b = $DirtB

const square_dirts_asset_path = "res://original_assets/game/sprites/{dirt}/1.png"
const square_dirts = {0: "DefineSprite_283_SquareDirt1",
					  1: "DefineSprite_285_SquareDirt2",
					  2: "DefineSprite_287_SquareDirt3",
					  3: "DefineSprite_289_SquareDirt4",
					  4: "DefineSprite_259_SquareDirt5",
					  5: "DefineSprite_291_SquareDirt6"} 
# TODO game's source code mentions dirt styles 7 & 8 too, but I was not able to find them anywhere 

var is_steppable = true
var tile_pos: Vector3  # Z - elevation, from -2 to +2, total 5 levels



func _ready():
	randomize()
	_set_random_dirt()


func init(tile_pos: Vector3):
	self.tile_pos = tile_pos
	return self


func _set_random_dirt():
	var dirt_a_random = randi() % 10
	var dirt_b_random = randi() % 10

	if dirt_a_random < 6:
		dirt_a.texture = load(square_dirts_asset_path.format({"dirt": square_dirts[dirt_a_random]}))
		dirt_a.rotation_degrees =  (randi() % 4) * 90
		dirt_a.self_modulate.a = (randi() % 6 + 5) / 100.0
	
	if dirt_b_random < 5:
		dirt_b.texture = load(square_dirts_asset_path.format({"dirt": square_dirts[dirt_b_random]}))
		dirt_b.rotation_degrees = (randi() % 4) * 90
		dirt_b.self_modulate.a = (randi() % 6 + 5) / 100.0


func get_pos() -> Vector3:
	return tile_pos


func is_steppable() -> bool:
	return is_steppable


func has_piece() -> bool:
	return slot.get_child_count() != 0


func get_piece():  # will return the first piece that was added to tile (FIFO)
	return slot.get_child(0)


func del_piece():
	if has_piece():
		slot.remove_child(slot.get_child(0))


func set_slot(torus: Control):
	slot.add_child(torus)
