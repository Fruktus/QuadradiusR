class_name Tile
extends PanelContainer

onready var tile_content = $TileContent
onready var slot = $TileContent/TorusSlot
onready var dirt_a = $TileContent/DirtA
onready var dirt_b = $TileContent/DirtB
onready var anim = $AnimationPlayer
onready var orb = $Orb

const square_dirts_asset_path = "res://original_assets/game/sprites/{dirt}/1.png"
const square_dirts = {0: "DefineSprite_283_SquareDirt1",
					  1: "DefineSprite_285_SquareDirt2",
					  2: "DefineSprite_287_SquareDirt3",
					  3: "DefineSprite_289_SquareDirt4",
					  4: "DefineSprite_259_SquareDirt5",
					  5: "DefineSprite_291_SquareDirt6"} 
# TODO game's source code mentions dirt styles 7 & 8 too, but I was not able to find them anywhere 
const MAX_ELEVATION = 2
const MIN_ELEVATION = -2
const ELEVATION_OFFSET = -50

var tile_id: String
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


func _update_tile_elevation():
	var elevation = self.tile_pos.z
	tile_content.rect_position = Vector2(ELEVATION_OFFSET * elevation,
										 ELEVATION_OFFSET * elevation)


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


func set_elevation(elevation: int):
	self.tile_pos.z = clamp(elevation, MIN_ELEVATION, MAX_ELEVATION)
	self._update_tile_elevation()
	# TODO: play SFX


func raise():
	self.set_elevation(self.tile_pos.z + 1)


func lower():
	self.set_elevation(self.tile_pos.z - 1)


func _torus_pickup(current_tile: Tile):
	if current_tile == self:
		anim.play("HighlightOn")


func _torus_putdown(current_tile: Tile):
	if current_tile == self:
		anim.play("HighlightOff")
