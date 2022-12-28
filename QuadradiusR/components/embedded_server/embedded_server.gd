extends Node

const MODULE = 'embedded-server'
const SERVER_PORT_FILE = '.server_port'

var executable_path: String
var available: bool
var pid: int = -1
var wait_left: float = 0
var server_port: int = -1
var on_server_ready_callbacks: Array = []



func _init():
	if "Win" in OS.get_name():
		executable_path = './quadradiusr_server.exe'
	else:
		executable_path = './quadradiusr_server'

	self.available = File.new().file_exists(executable_path)


func _ready():
	if self.available:
		Logger.info('Server executable is available', MODULE)
	else:
		Logger.info('Server executable is not available', MODULE)

	self.run_server()


func _process(delta):
	if self.wait_left > 0:
		self.wait_left -= delta
		if self.wait_left <= 0:
			self._check_server_for_startup()


func run_server():
	if not self.available:
		push_error('Server executable is not available')
		return

	var file = File.new()

	if file.file_exists(SERVER_PORT_FILE):
		Directory.new().remove(SERVER_PORT_FILE)

	var args = ['--embedded-mode', '--host', '0.0.0.0', '--port', '0']
	Logger.info('Running server with arguments {args}'.format({'args': args}), MODULE)
	self.pid = OS.execute(executable_path, args, false, [])
	self.wait_left = 0.05


func _check_server_for_startup():
	var file = File.new()

	if not file.file_exists(SERVER_PORT_FILE):
		self.wait_left = 0.1
		return
	
	file.open(SERVER_PORT_FILE, File.READ)
	var content = file.get_as_text()
	file.close()

	self.server_port = int(content)
	Logger.info('Server started on port {port}'.format({'port': self.server_port}), MODULE)

	self.wait_left = 0
	for cb in self.on_server_ready_callbacks:
		cb.call_func()


func stop_server():
	if self.pid > 0:
		OS.kill(self.pid)
		self.pid = -1


func is_available():
	return self.available


func get_pid():
	return self.pid


func get_port():
	return self.server_port


func on_server_ready(cb: FuncRef):
	if self.server_port > 0:
		cb.call_func()
	self.on_server_ready_callbacks.append(cb)
