extends PanelContainer

signal player_hover_start(username)
signal player_hover_end(username)
signal player_clicked(username)

onready var label = $HBoxContainer/UsernameLabel
onready var hover_sfx = $HoverSFX
onready var challenge_issued_sfx = $ChallengeIssuedSFX
onready var challenge_received_sfx = $ChallengeReceivedSFX
onready var dot = $HBoxContainer/DotContainer/Dot
onready var bg = $BG

const INACTIVE_COLOR = Color(1.0, 0.0, 0.0, 1.0)
const ACTIVE_COLOR = Color("#381b16")
const CHALLENGE_ISSUED = preload("res://original_assets/lobby/shapes/1.png")
const CHALLENGE_RECEIVED = preload("res://original_assets/lobby/shapes/3.png")

export var username = "asd GUEST"
var is_self_player = false  # denotes if this is the entry corresponding to the curent player



func _ready():
	label.text = username


func init(username: String, is_self_player: bool=false):
	self.username = username
	self.is_self_player = is_self_player
	return self


func receive_challenge():
	challenge_received_sfx.play()
	dot.texture = CHALLENGE_RECEIVED


func _on_hover_enter():
	hover_sfx.play(0)
	bg.visible = true
	label.add_color_override("font_color", ACTIVE_COLOR)
	emit_signal("player_hover_start", self.username)


func _on_hover_exit():
	bg.visible = false
	label.add_color_override("font_color", INACTIVE_COLOR)
	emit_signal("player_hover_end", self.username)


func _on_click():
	challenge_issued_sfx.play()
	
	if is_self_player:
		# If player clicked themselves, don't do anything else
		return
		
	dot.texture = CHALLENGE_ISSUED
	
	emit_signal("player_clicked", self.username)
