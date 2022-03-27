from aiohttp import web

from quadradiusr_server.server import routes


@routes.view('/health')
class HealthView(web.View):
    async def get(self):
        return web.json_response({
            'status': 'up',
        })
