extends PanelContainer

onready var user1_input = $Control/User1Input
onready var user2_input = $Control/User2Input

onready var user1_decoration_active = $Control/User1DecorationActive
onready var user2_decoration_active = $Control/User2DecorationActive


func _ready():
	user1_input.text = Context.username
	user2_input.text = Context.get_other_player()['username']
	
	_update_current_player(Context.game_state.get_current_player())

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


# # # # # # # # #
# WS Listeners  #
# # # # # # # # #
func _game_state_diff(data: Dictionary):
	_update_current_player(data['game_state_diff']['current_player_id'])
