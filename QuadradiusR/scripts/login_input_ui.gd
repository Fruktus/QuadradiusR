extends Node2D

onready var guestinput = $GuestInput
onready var usernameinput = $UsernameInput
onready var passwordinput = $PasswordInput
onready var pwbutton = $PWButton

signal login(is_guest, remember_pw, username, password)



func _on_guest_click():
	usernameinput.text = ""
	passwordinput.text = ""


func _on_member_click():
	guestinput.text = ""	


func _on_start_click():
	if guestinput.text != "":
		emit_signal("login", true, false, guestinput.text, "")
	elif usernameinput.text != "" and passwordinput.text != "":
		emit_signal("login", false, pwbutton.pressed(), usernameinput.text, passwordinput.text)
