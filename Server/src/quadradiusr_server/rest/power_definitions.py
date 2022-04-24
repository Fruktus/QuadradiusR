from abc import ABCMeta

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound

from quadradiusr_server.db.transactions import transactional
from quadradiusr_server.powers import power_definitions as server_power_definitions, \
    PowerDefinition
from quadradiusr_server.rest.auth import authorized_endpoint
from quadradiusr_server.rest.mappers import power_definition_to_json
from quadradiusr_server.server import routes


class PowerDefinitionViewBase(web.View, metaclass=ABCMeta):
    async def _get_power_definition(self) -> PowerDefinition:
        power_definition_id = self.request.match_info.get('power_definition_id')
        power_definition = server_power_definitions.get_by_id(power_definition_id)
        if not power_definition:
            raise HTTPNotFound(reason='Power definition not found')
        return power_definition


@routes.view('/power-definition')
class PowerDefinitionsView(web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        power_definitions = server_power_definitions.get_all()
        return web.json_response([power_definition_to_json(
            power_definition,
        ) for power_definition in power_definitions])


@routes.view('/power-definition/{power_definition_id}')
class PowerDefinitionView(PowerDefinitionViewBase, web.View):
    @transactional
    @authorized_endpoint
    async def get(self):
        power_definition = await self._get_power_definition()
        return web.json_response(power_definition_to_json(
            power_definition,
        ))
