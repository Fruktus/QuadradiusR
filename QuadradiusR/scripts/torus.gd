class_name Torus
extends Control

enum COLORS {RED, BLUE, GREEN, YELLOW, CYAN, MAGENTA}

onready var pickup_sfx = $SFXGroup/PickupSFX2D
onready var putdown_sfx = $SFXGroup/PutdownSFX2D
onready var anim = $AnimationPlayer
onready var light_on = $LightGroup/LightOn
onready var light_off = $LightGroup/LightOff
onready var shadow = $TorusShadow
onready var collision_detector = $MouseDetector/CollisionShape2D

const starting_pos = Vector2(50, 50)
const color_asset_path = "res://original_assets/game/sprites/{color}/{mode}.png"
const color_textures = {COLORS.RED: "DefineSprite_412_Decoration0",
						COLORS.BLUE: "DefineSprite_415_Decoration1",
						COLORS.GREEN: "DefineSprite_418_Decoration2",
						COLORS.YELLOW: "DefineSprite_421_Decoration3",
						COLORS.CYAN: "DefineSprite_856_Decoration4",
						COLORS.MAGENTA: "DefineSprite_859_Decoration5"}

var movement_powerup_manager = preload("res://scripts/movement_powerup_manager.gd").new()
var board: Control
var piece_id: String
var player_id: String
var color = COLORS.RED
var current_tile: Tile
var is_held = false
var can_interact = true
var powerup_id_to_definition_id = {}



func _ready():
	set_process(false)
	light_off.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 1}))
	light_on.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 2}))
	update_shadow(get_parent().get_parent().get_parent().tile_pos)


func _process(delta: float):
	self.rect_global_position = get_global_mouse_position() - rect_min_size/2 * board.rect_scale


func init(board: Control, tile: Tile, player_id: String, piece_id: String, color: int = COLORS.RED):
	self.player_id = player_id
	self.board = board
	self.color = color
	self.current_tile = tile
	self.piece_id = piece_id
	return self


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if can_interact and Context.user_id == player_id:
		if event is InputEventMouseButton:
			if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
				_begin_drag()
			else:
				_end_drag()


func _begin_drag():
	anim.play("Pickup")	
	is_held = true
	
	get_tree().call_group("torus", "set_interaction", false)
	get_tree().call_group("board", "_torus_pickup", self)
	get_tree().call_group("tile", "_torus_pickup", current_tile)

	set_process(true)


func _end_drag():
	set_process(false)
	anim.play("Putdown")

	get_tree().call_group("torus", "set_interaction", true)
	get_tree().call_group("board", "_torus_putdown", self)
	get_tree().call_group("tile", "_torus_putdown", current_tile)
	
	is_held = false

	rect_position = self.starting_pos


func set_interaction(can_interact):
	if not is_held:
		self.can_interact = can_interact
		collision_detector.disabled = !can_interact


func _on_hover_start():
	self.light_on.visible = true


func _on_hover_end():
	self.light_on.visible = false


func _get_parent_tile():
	return self.get_parent().get_parent()


func update_shadow(pos: Vector3):
	var distance_from_center = pos - Vector3(board.board_size.x, board.board_size.y, 0) / 2.0
	distance_from_center /= Vector3(board.board_size.x, board.board_size.y, 5)
	shadow.position = Vector2(distance_from_center.x, distance_from_center.y) * 100
	# TODO handle scale relative to elevation, check shadow alpha and offset values - whether matches original
#	shadow.scale = Vector2(distance_from_center.z * 2, distance_from_center.z * 2)


func should_move_torus(source_tile: Tile, target_tile: Tile) -> bool:
	# check if can make move
	if not movement_powerup_manager.can_make_move(source_tile, target_tile):
		return false  # no need to check further
	# check if move will cause collision with piece
	if target_tile.has_piece():
		var target_piece = target_tile.get_piece()
		if target_piece.player_id == self.player_id:
			return false
		# TODO check if can step on opponent
			# 	if there is other piece, check if can collide with it
	# 		if can collide, dont check the conditions again later, but
	#		do check in board or somewhere if collision occurs and if so delete piece,
	
	# 	if no other piece, return true
	return true

func make_move(source_tile: Tile, target_tile: Tile, is_colliding: bool = false) -> void:
	update_shadow(target_tile.tile_pos)
	self.current_tile = target_tile
	
	if is_colliding:
		target_tile.del_piece()
		anim.play("DestroyOpponent")

# TODO maybe add method destroy() which would handle aftermath
# OR destroy_piece(torus) which would make one piece destroy the other, so it could handle
# all the consequences


func add_power(power_id: String, power_definition_id):
	if power_definition_id.empty():
		anim.queue("CollectPowerup")
	powerup_id_to_definition_id[power_id] = power_definition_id
