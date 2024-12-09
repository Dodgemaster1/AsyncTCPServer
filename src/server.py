from __future__ import annotations
import asyncio
import logging
from .client import create_client, Kind
from .client_handler import ClientHandler
from .config_manager import ConfigManager
from .exceptions import PortInUseError


log = logging.getLogger(__name__)

class Server:
    def __init__(self, host: str, port: int, kind: Kind):
        self.kind: Kind = kind
        self.host: str = host
        self.port: int = port

    async def run(self):
        try:
            server = await asyncio.start_server(self.handle_client, host=self.host, port=self.port)
        except OSError:
            raise PortInUseError(port=self.port)
        async with server:
            log.info(f"{self.kind.value} server listening on: {self.port}")
            await server.serve_forever()


    async def handle_client(self, reader, writer):
        client = create_client(reader=reader, writer=writer, kind=self.kind)
        client_handler = ClientHandler(client)
        await client_handler.handle_client()


async def run_servers():
    while True:
        try:
            host = '0.0.0.0'
            config = ConfigManager()
            modem_port, program_port = config.get_ports()
            modem_server = Server(host=host, port=modem_port, kind=Kind.MODEM)
            program_server = Server(host=host, port=program_port, kind=Kind.PROGRAM)

            await asyncio.gather(
                modem_server.run(),
                program_server.run()
            )

        except Exception as e:
            log.error(f"Critical error: {e}", exc_info=False)
            log.info("Reload servers in 30 seconds...")
            await asyncio.sleep(30)
