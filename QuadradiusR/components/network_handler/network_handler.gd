extends Node

signal lobby_player_joined(data)  # TODO when new player joins lobby
signal lobby_player_left(data)  # TODO when player leaves lobby
signal lobby_message_posted(data)  # TODO when someone posts message
signal lobby_challenge_received(data)  # TODO when player was challenged
signal lobby_communique_updated(data)  # TODO possibly ignore that and just store this data in this node, make lobby retrieve it every time

onready var rest_api: RestApi = $RESTApi
onready var ws_api: WSApi = $WSApi

var url = "http://127.0.0.1:8888"
var token: String

func _ready():
	if OS.has_feature('JavaScript'):
		url = JavaScript.eval('window.location.href')
		if not url.ends_with('/'):
			url = url.rsplit('/', true, 1)[0]
	rest_api.url = url
	if EmbeddedServer.is_available():
		EmbeddedServer.on_server_ready(funcref(self, '_embedded_server_ready'))
	# use_threads=true does not work for HTML5
	rest_api.use_threads = false
	rest_api.max_redirects = 0


func _embedded_server_ready():
	rest_api.url = 'http://127.0.0.1:{port}'.format({'port': EmbeddedServer.get_port()})


func set_url(url: String):
	rest_api.url = url


# # # # # # # #
# CREATE USER #
# # # # # # # #
func create_user(username: String, password: String, cb: FuncRef, args: Dictionary):
	Logger.info('Creating user {username}'.format({'username': username}))
	rest_api.create_user(username, password, funcref(self, "_create_user_1"), {'cb': cb})

func _create_user_1(message: Message, args: Dictionary):
	Logger.info('User created')


# # # # # # # # # #
# AUTHORIZE USER  #
# # # # # # # # # #
func authorize_user(username: String, password: String, cb: FuncRef, args: Dictionary):
	rest_api.authorize(username, password, funcref(self, "_authorize_user_1"), {'cb': cb, 'user_data': args})

func _authorize_user_1(message: Message, args: Dictionary):
	# After authorize
	var is_authorized = message.result == 200

	if is_authorized:
		token = message.body['token']
		rest_api.get_user_me(self.token, funcref(self, "_authorize_user_2"), args)
	else:
		args['cb'].call_func(is_authorized, args['user_data'], message)

func _authorize_user_2(message: Message, args: Dictionary):
	# After get_user_me
	Context.username = message.body['username']
	Context.user_id = message.body['id']
	args['cb'].call_func(true, args['user_data'], message)


# # # # # # # #
# JOIN LOBBY  #
# # # # # # # #
func join_lobby(cb: FuncRef):
	Logger.info('Obtaining lobby')
	rest_api.get_lobby(token, funcref(self, "_join_lobby_1"), {'cb': cb})

func _join_lobby_1(message: Message, args: Dictionary):
	# After get_lobby
	if message.result == 200:
		Logger.info('Lobby obtained successfully, joining')
		Context.lobby_data = message.body
		ws_api.connect_to(message.body["ws_url"], token)
	else:
		Logger.info('Failed to obtain lobby')
		var test = "ws://127.0.0.1:8888/lobby/@main/connect"
		ws_api.connect_to(test, token)

	rest_api.get_lobby(token, funcref(self, "_join_lobby_2"), args)

func _join_lobby_2(message: Message, args: Dictionary):
	if message.result == 200:
		Logger.info('Lobby joined successfully')
		Context.lobby_data = message.body
	else:
		Logger.error('Failed to join lobby')

	args['cb'].call_func()


# # # # # # # # #
# INVITE PLAYER #
# # # # # # # # #
func invite_player(opponent_uuid: String):
	rest_api.invite_player(token, opponent_uuid)


# # # # # # # # # # # # #
# ACCEPT AND JOIN GAME  #
# # # # # # # # # # # # #
func accept_and_join_game(game_invite_id: String, cb: FuncRef):
	rest_api.accept_game_invite(self.token, game_invite_id, funcref(self, "_accept_and_join_game_1"), {"game_invite_id": game_invite_id, 'cb': cb})

func _accept_and_join_game_1(message: Message, args: Dictionary):
	if message.result != 200:
		push_error("Status code {code} on game join".format({"code": message.result}))
	join_game(message.body['id'], args['cb'])


# # # # # # #
# JOIN GAME #
# # # # # # #
func join_game(game_id: String, cb: FuncRef):
	Logger.info('Obtaining game {id}'.format({'id': game_id}))
	rest_api.get_game(self.token, game_id, funcref(self, "_join_game_1"), {'cb': cb})

func _join_game_1(message: Message, args: Dictionary):
	# After get_game
	if message.result == 200:
		Logger.info('Leaving lobby and joining the game')

		Context.game_data = message.body
		ws_api.close("Moving from lobby to game")
		ws_api.connect_to(message.body["ws_url"], self.token)

		Logger.info('Getting game state')
		rest_api.get_game_state(self.token, message.body['id'], funcref(self, "_join_game_2"), args)
	else:
		Logger.error('Failed to obtain the game')
	
func _join_game_2(message: Message, args: Dictionary):
	# After get_game_state
	var etag = ""
	for header in message.headers:
		if "etag" in header:
			etag = header.substr(7, 18)  # FIXME what?!
	Context.game_state = GameState.new().init(message.body, etag)
	rest_api.get_power_definitions(self.token, funcref(self, "_join_game_3"), args)

func _join_game_3(message: Message, args: Dictionary):
	# After get_power_definitions
	if message.result == 200:
		var powerups_dict = {}  # Transform powerup definitions array into dict
		for powerup in message.body:
			powerups_dict[powerup['id']] = powerup
		
		Context.powerups_data = powerups_dict
		args['cb'].call_func()
	else:
		print('join_game_3: ERROR GETTING POWER DEFINITIONS')

