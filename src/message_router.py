from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .client import Client, Modem, Program


@dataclass
class MessageRouter(ABC):
    connections: dict

    @abstractmethod
    async def route_message(self, data: bytes):
        """
        Route message between clients depending on their type and modem number
        """
        pass


@dataclass
class ModemMessageRouter(MessageRouter):
    modem: Modem

    async def route_message(self, data: bytes):
        if data == b'CheckServer':
            await self.modem.send_ok()
        if self.modem in self.connections.keys():
            for program in self.connections[self.modem]:
                await program.send(data)


@dataclass
class ProgramMessageRouter(MessageRouter):
    program: Program

    async def route_message(self, data: bytes):
        if self.program.modem in self.connections.keys():
            await self.program.modem.send(data)



def create_message_router(client: Client, connections: dict) -> MessageRouter:
    if isinstance(client, Modem):
        return ModemMessageRouter(modem=client, connections=connections)
    elif isinstance(client, Program):
        return ProgramMessageRouter(program=client, connections=connections)
