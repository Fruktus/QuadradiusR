from quadradiusr_server import config
from quadradiusr_server.server import QuadradiusRServer

server = QuadradiusRServer(config.from_toml('config.toml'))
server.run()
