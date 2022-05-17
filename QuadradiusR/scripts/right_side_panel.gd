extends PanelContainer

onready var user1_input = $Control/User1Input
onready var user2_input = $Control/User2Input

onready var user1_decoration_active = $Control/User1DecorationActive
onready var user2_decoration_active = $Control/User2DecorationActive

onready var moves_played_counter = $Control/MovesPlayedCounter

var powerup_id_to_definition_id = {}  # all powerups owned by player with their types
var powerup_definition_id_to_count = {}  # shorthand for count of powerups by type



func _ready():
	user1_input.text = Context.username
	user2_input.text = Context.get_other_player()['username']
	
	_update_current_player(Context.game_state.get_current_player())
	_update_moves_played(Context.game_state.get_moves_played())


func _update_current_player(id: String):
	if id == null:
		user1_decoration_active.visible = false
		user2_decoration_active.visible = false
	elif id == Context.user_id:
		user1_decoration_active.visible = true
		user2_decoration_active.visible = false
	else:
		user1_decoration_active.visible = false
		user2_decoration_active.visible = true


func _update_moves_played(moves_played: int):
	if moves_played >= 0:
		moves_played_counter.text = str(moves_played)


func _add_powerup(power_id: String, power_def_id: String):
	# Since this is used exclusively for players own powerups,
	# the definition id cannot be null
	powerup_id_to_definition_id[power_id] = power_def_id
	if powerup_definition_id_to_count.has(power_def_id):
		powerup_definition_id_to_count[power_def_id] += 1
		# TODO increment count in powerlist
	else:
		powerup_definition_id_to_count[power_def_id] = 1
		# TODO add to powerlist
	


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_state_diff(data: Dictionary):
	_update_current_player(data['game_state_diff']['current_player_id'])
	_update_moves_played(data['game_state_diff'].get('moves_played', -1))
