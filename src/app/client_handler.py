from __future__ import annotations
import asyncio
import logging
import re
from .connection_manager import ConnectionsManager
from .client import Client
from .exceptions import ConnectionMessageError, InvalidModemNumberError, InitializeConnectionError
from .message_router import create_message_router

log = logging.getLogger(__name__)

CONN_MESSAGE_TIMEOUT = 5.0

class ClientHandler:
    def __init__(self, client: Client):
        self.client = client
        self.connections_manager = ConnectionsManager()

    async def handle_client(self):
        try:
            self.client.addr = self.client.writer.get_extra_info('peername')
            self.client.modem_number = await self._get_modem_nuber()
            await self.connections_manager.register(self.client)
            await self.client.send_ok()
            log.info(f'Client connected: {self.client}')

            await self._handle_communication_loop()

        except InitializeConnectionError as e:
            log.info(e)
        except ConnectionResetError:
            log.debug("%s reset connection", self.client)
        except Exception as e:
            log.error("Unexpected error in handle_client: %s", e, exc_info=True)
        finally:
            try:
                log.info("Connection closed: %s", self.client)
                await self.connections_manager.disconnect(self.client)
            except Exception as e:
                log.debug("Unexpected error while disconnecting %s: %s", self.client, e, exc_info=True)
            finally:
                log.debug("Current connections: %s", self.connections_manager.connections)

    async def _get_modem_nuber(self) -> int:
        conn_message = await self._get_conn_message()
        modem_number = self._parse_modem_number(conn_message)
        return modem_number

    async def _get_conn_message(self) -> str:
        try:
            data = await asyncio.wait_for(
                self.client.receive(),
                timeout=CONN_MESSAGE_TIMEOUT
            )
            return data.decode()
        except (asyncio.TimeoutError, UnicodeDecodeError) as e:
            raise ConnectionMessageError(e)

    @staticmethod
    def _parse_modem_number(conn_message: str) -> int:
        match = re.search(r"Modem=(\d+)", conn_message)  # get all digits after "Modem="
        if match:
            return int(match.group(1))
        else:
            raise InvalidModemNumberError(conn_message)

    async def _handle_communication_loop(self):
        router = create_message_router(client=self.client, connections=self.connections_manager.connections)
        while True:
            data = await self.client.receive()
            if not data:
                break
            await router.route_message(data)
