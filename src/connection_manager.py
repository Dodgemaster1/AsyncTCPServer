from __future__ import annotations
from .client import Client, Modem, Program
from .exceptions import ModemNotFound


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class ConnectionsManager:
    def __init__(self):
        self.connections: dict[Modem: list[Program]] = {}

    async def register(self, client: Client):
        if isinstance(client, Modem):
            await self._register_modem(client)
        elif isinstance(client, Program):
            await self._register_program(client)

    async def disconnect(self, client: Client):
        await client.close_connection()
        if client.modem is None:
            return
        await self._clean_resources(client)

    async def _register_modem(self, modem: Modem):
        for registered_modem in list(self.connections.keys()):
            if modem.modem_number == registered_modem.modem_number:
                await self.disconnect(modem)
                break
        self.connections[modem] = []

    async def _register_program(self, program: Program):
        for modem in self.connections.keys():
            if modem.modem_number == program.modem_number:
                self.connections[modem].append(program)
                program.modem = modem
                break
        else:
            raise ModemNotFound(modem_number=program.modem_number)

    async def _clean_resources(self, client):
        if isinstance(client, Modem):
            await self._clean_modem_resources(client)
        elif isinstance(client, Program):
            await self._clean_program_resources(client)

    async def _clean_modem_resources(self, modem):
        if modem in self.connections:
            for program in self.connections[modem].copy():
                await self.disconnect(program)
            del self.connections[modem]

    async def _clean_program_resources(self, program):
        if program in self.connections.get(program.modem, []):
            self.connections[program.modem].remove(program)
