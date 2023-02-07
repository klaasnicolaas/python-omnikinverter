"""Create TCP Requests for the Omnik Inverter."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from omnikinverter.exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
)
from asyncio.streams import StreamReader, StreamWriter

from omnikinverter import tcp_handler

@dataclass
class OmnikTcpRequest:
    host: str
    serial_number: int
    tcp_port: int
    request_timeout: float
    _close_session: bool = False

    _reader: StreamReader | None = None
    _writer: StreamWriter | None = None
    _raw_msg: Any | None = None

    def __init__(
        self,
        host: str,
        serial_number: int,
        tcp_port: int,
        request_timeout: float,
    ) -> None:
        """
        Create a new TCP Request instance.

        Args:
            host: The IP address of the inverter.
            serial_number: The serial number of the device.
            tcp_port: The TCP port to connect to.
            request_timeout: The maximum amount of seconds a request can take.
        """
        self.host = host
        self.serial_number = serial_number
        self.tcp_port = tcp_port
        self.request_timeout = request_timeout

    async def request(self) -> dict[str, Any]:
        """Perform a raw TCP request to the Omnik device.
        Returns:
            A Python dictionary (text) with the response from
            the Omnik Inverter.
        Raises:
            OmnikInverterAuthError: Serial number is required to communicate
                with the Omnik Inverter.
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.
        """
        # Make sure the request is valid.
        self._validate_request()

        try:
            await asyncio.wait_for(self._connect(), timeout=self.request_timeout)
            await asyncio.wait_for(self._write_message(), timeout=self.request_timeout)
            await asyncio.wait_for(self._read_message(), timeout=self.request_timeout)
            await asyncio.wait_for(self._close(), timeout=self.request_timeout)
        except OSError as exception:
            raise OmnikInverterConnectionError(
                "Failed to communicate with the Omnik Inverter device over TCP"
            ) from exception
        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred when opening a TCP connection to the Omnik Inverter device"
            ) from exception
        
        return tcp_handler.parse_messages(self.serial_number, self._raw_msg)

    async def _connect(self) -> None:
        # Await for the method with a timeout.
        reader, writer = await asyncio.open_connection(self.host, self.tcp_port)

        self._reader = reader
        self._writer = writer

    async def _write_message(self) -> None:
        self._writer.write(tcp_handler.create_information_request(self.serial_number))
        await self._writer.drain()

    async def _read_message(self) -> None:
        self._raw_msg = await self._reader.read(1024)
        
    async def _close(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()

    def _validate_request(self) -> None:
        if self.serial_number is None:
            raise OmnikInverterAuthError("serial_number is missing from the request")
