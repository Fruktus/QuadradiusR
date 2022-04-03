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
var current_tile: Tile
var color = COLORS.RED
var player = 0
var is_held = false
var can_interact = true



func _ready():
	set_process(false)
	light_off.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 1}))
	light_on.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 2}))
	update_shadow(get_parent().get_parent().get_parent().tile_pos)


func _process(delta: float):
	self.rect_global_position = get_global_mouse_position() - rect_min_size/2 * board.rect_scale


func init(board: Control, tile: Tile, player=0, color=COLORS.RED):
	self.player = player
	self.board = board
	self.color = color
	self.current_tile = tile
	return self


func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if can_interact:
		if event is InputEventMouseButton:
			if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
				_begin_drag()
			else:
				_end_drag()


func _begin_drag():
	is_held = true
	pickup_sfx.play()
	shadow.visible = false
	get_tree().call_group("torus", "set_interaction", false)
	get_tree().call_group("board", "_torus_pickup", self)
	yield(get_tree(), "idle_frame")  # needed for the scaling to work properly
	self.rect_scale = Vector2(1.5, 1.5)
	set_process(true)


func _end_drag():
	set_process(false)
	shadow.visible = true
	get_tree().call_group("torus", "set_interaction", true)
	get_tree().call_group("board", "_torus_putdown", self)
	is_held = false
	putdown_sfx.play()
	self.rect_scale = Vector2(1, 1)
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
	print(distance_from_center)
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
		if target_piece.player == self.player:
			return false
		# TODO check if can step on opponent
			# 	if there is other piece, check if can collide with it
	# 		if can collide, dont check the conditions again later, but
	#		do check in board or somewhere if collision occurs and if so delete piece,
	#		run animation, sound etc
	
	# 	if no other piece, return true
	return true

func make_move(source_tile: Tile, target_tile: Tile, is_colliding: bool = false) -> void:
	update_shadow(target_tile.tile_pos)
	self.current_tile = target_tile
	
	if is_colliding:
		target_tile.del_piece()
		anim.play("DestroyOpponent")
	# TODO move the sound playing to here maybe to handle dropping the piece
	pass
	
# TODO maybe add method destroy() which would handle aftermath
# OR destroy_piece(torus) which would make one piece destroy the other, so it could handle
# all the consequences
