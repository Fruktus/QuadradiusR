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
onready var powers_list = $PowerupPopup

const starting_pos = Vector2(50, 50)
const color_asset_path = "res://original_assets/game/sprites/{color}/{mode}.png"
const color_textures = {
	COLORS.RED: "DefineSprite_412_Decoration0",
	COLORS.BLUE: "DefineSprite_415_Decoration1",
	COLORS.GREEN: "DefineSprite_418_Decoration2",
	COLORS.YELLOW: "DefineSprite_421_Decoration3",
	COLORS.CYAN: "DefineSprite_856_Decoration4",
	COLORS.MAGENTA: "DefineSprite_859_Decoration5"
}
const color_tint_codes = {
	COLORS.RED: Color("ffd7d7"),  # all of those values are eyeballed, correct if needed
	COLORS.BLUE: Color("b2c5ff"),
	COLORS.GREEN: Color("aeffbe"),
	COLORS.YELLOW: Color("fbffae"),
	COLORS.CYAN: Color("aefff7"),
	COLORS.MAGENTA: Color("ffaefa")
}

var movement_powerup_manager = preload("res://scripts/movement_powerup_manager.gd").new()
var board: Control
var piece_id: String
var player_id: String
var powerup_id_to_definition_id = {}  # all powerups owned by player with their types
var powerup_definition_id_to_count = {}  # shorthand for count of powerups by type
var color = COLORS.RED
var current_tile: Tile  # the tile on which the piece stands
var is_held = false  # is player currently dragging this piece
var can_interact = true  # can player move the piece
var powers_list_open = false  # is the popup with powers open
var selected = false  # has player clicked the piece



# # # # #
# Init  #
# # # # #
func _ready():
	set_process(false)
	_set_color(self.color)
	_update_shadow(current_tile.tile_pos)


func _process(delta: float):
	self.rect_global_position = get_global_mouse_position() - rect_min_size/2 * board.rect_scale


func init(board: Control, tile: Tile, player_id: String, piece_id: String, color: int = COLORS.RED):
	self.player_id = player_id
	self.board = board
	self.color = color
	self.current_tile = tile
	self.piece_id = piece_id
	return self


# # # # # # # # # # #
# Mouse Interaction #
# # # # # # # # # # #
func _on_mouse_event(viewport: Node, event: InputEvent, shape_idx: int):
	if can_interact and Context.user_id == player_id:
		if event is InputEventMouseButton:
			if event.get_button_index() == BUTTON_LEFT and event.is_pressed():
				_begin_drag()
			elif event.get_button_index() == BUTTON_LEFT and not event.is_pressed():
				if powers_list_open:
					_toggle_powers_list()
				if selected:
					selected = false
					anim.play("RESET")
				_end_drag()
			
			if event.get_button_index() == BUTTON_RIGHT and event.is_pressed():
				# bonus popup opener, later maybe use left mouse button
				selected = not selected
				if selected:
					anim.play("Selected")
					if not powers_list_open:
						powers_list_open = true
						_toggle_powers_list()
				else:
					anim.play("RESET")
					if powers_list_open:
						powers_list_open = false
						_toggle_powers_list()



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


# # # # #
# Utils #
# # # # #
func set_interaction(can_interact):
	if not is_held:
		self.can_interact = can_interact
#		collision_detector.disabled = !can_interact


func _on_hover_start():
	self.light_on.visible = true
	if Context.user_id == player_id:
		if not selected and not powers_list_open:
			_toggle_powers_list()


func _on_hover_end():
	self.light_on.visible = false
	if Context.user_id == player_id:
		if not selected and powers_list_open:
				_toggle_powers_list()


func _get_parent_tile():
	return self.get_parent().get_parent()


func update_shadow(pos: Vector3):
	var distance_from_center = pos - Vector3(board.board_size.x, board.board_size.y, 0) / 2.0
	distance_from_center /= Vector3(board.board_size.x, board.board_size.y, 5)
	shadow.position = Vector2(distance_from_center.x, distance_from_center.y) * 100
	# TODO handle scale relative to elevation, check shadow alpha and offset values - whether matches original
#	shadow.scale = Vector2(distance_from_center.z * 2, distance_from_center.z * 2)


# # # # # # #
# Movement  #
# # # # # # #
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
	_update_shadow(target_tile.tile_pos)
	self.current_tile = target_tile
	
	if is_colliding:
		target_tile.del_piece()
		anim.play("DestroyOpponent")

# TODO maybe add method destroy() which would handle aftermath
# OR destroy_piece(torus) which would make one piece destroy the other, so it could handle
# all the consequences

# # # # # # #
# Powerups  #
# # # # # # #
func add_power(power_id: String, power_def_id):
	if powerup_id_to_definition_id.empty():
		anim.queue("Tint" + player_id)
	powerup_id_to_definition_id[power_id] = power_def_id

	if not power_def_id: # the client is not permitted to view the power
		return

	if not powerup_definition_id_to_count.has(power_def_id):
		powerup_definition_id_to_count[power_def_id] = 1
		powers_list.add_powerup(power_def_id, Context.get_power_by_definition_id(power_def_id)['name'])
	else:
		powerup_definition_id_to_count[power_def_id] += 1
		powers_list.add_powerup_charges(power_def_id, Context.get_power_by_definition_id(power_def_id)['name'], 1)


func use_power(power_id: String):
	powers_list.use_power(powerup_id_to_definition_id[power_id])
	# TODO Actually use the power, send data to server etc.


func _toggle_powers_list():
#	if powerup_id_to_definition_id.empty():
#		return

	if not powers_list_open:
		powers_list_open = true
		powers_list.rect_scale = board.rect_scale * Vector2(1.2, 1.2)  # FIXME temporary scaling before asset dimensions are fixed
		powers_list.rect_global_position = self.rect_global_position
		powers_list.popup()
	else:
		powers_list_open = false
		powers_list.visible = false


# # # # # # 
# Visual  #
# # # # # #
func _update_shadow(pos: Vector3):
	var distance_from_center = pos - Vector3(board.board_size.x, board.board_size.y, 0) / 2.0
	distance_from_center /= Vector3(board.board_size.x, board.board_size.y, 5)
	shadow.position = Vector2(distance_from_center.x, distance_from_center.y) * 100
	# TODO handle scale relative to elevation, check shadow alpha and offset values - whether matches original
	# shadow.scale = Vector2(distance_from_center.z * 2, distance_from_center.z * 2)


func _set_color(color: int):
	light_off.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 1}))
	light_on.texture = load(color_asset_path.format({"color": color_textures[color], "mode": 2}))
	
	# Edit the tint animation to change piece color to the correct one (animation can't have params)
	if player_id == Context.user_id:
		# Will use TintSelf as source animation
		var tint_track_id = anim.get_animation("TintSelf").find_track("TorusBase:self_modulate")
		anim.get_animation("TintSelf").track_set_key_value(tint_track_id, 1, color_tint_codes[color])
		anim.rename_animation("TintSelf", "Tint" + player_id)
	else:
		# Will use TintOpponent as source animation
		var tint_track_id = anim.get_animation("TintOpponent").find_track("TorusBase:self_modulate")
		anim.get_animation("TintOpponent").track_set_key_value(tint_track_id, 1, color_tint_codes[color])
		anim.rename_animation("TintOpponent", "Tint" + player_id)
