from __future__ import annotations
from asyncio import StreamWriter, StreamReader
from abc import ABC
from enum import Enum


class Kind(Enum):
    MODEM = "modem"
    PROGRAM = "program"


class Client(ABC):
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.writer = writer
        self.reader = reader
        self.modem_number: int | None = None
        self.addr: str | None = None
        self.is_connected = True
        self.modem: Modem | None = None
        self.repr: str | None = None

    async def send(self, message: bytes):
        """
        Send message to client
        """
        if self.writer.is_closing():
            return False
        self.writer.write(message)
        await self.writer.drain()

    async def send_ok(self):
        await self.send(b"OK\r\n")

    async def receive(self) -> bytes:
        """
        Receive message from client
        :return: message
        """
        return await self.reader.read(2048)

    async def close_connection(self):
        if self.is_connected:
            if not self.writer.is_closing():
                self.writer.close()
                await self.writer.wait_closed()
            self.is_connected = False

    # For logging dict with connections
    def __repr__(self) -> str:
        if self.repr is None:
            self.repr = f"Client(modem_number={self.modem_number}, kind={self.__class__.__name__}, addr={self.addr})"
        return self.repr

    # For using object as dict key
    def __hash__(self):
        return hash(self.addr)


class Modem(Client):
    def __init__(self, reader, writer):
        super().__init__(reader, writer)
        self.modem = self


class Program(Client):
    def __init__(self, reader, writer):
        super().__init__(reader, writer)
        self.modem: Modem | None = None


def create_client(reader: StreamReader, writer: StreamWriter, kind: Kind) -> Client:
    if kind == Kind.MODEM:
        return Modem(reader, writer)
    else:
        return Program(reader, writer)
