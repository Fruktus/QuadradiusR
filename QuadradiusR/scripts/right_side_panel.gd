extends PanelContainer

onready var user1_input = $Control/User1Input
onready var user2_input = $Control/User2Input

onready var user1_decoration_active = $Control/User1DecorationActive
onready var user2_decoration_active = $Control/User2DecorationActive

onready var moves_played_counter = $Control/MovesPlayedCounter


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

# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_state_diff(data: Dictionary):
	_update_current_player(data['game_state_diff']['current_player_id'])
	_update_moves_played(data['game_state_diff'].get('moves_played', -1))
