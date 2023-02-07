"""Create TCP Requests for the Omnik Inverter."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from omnikinverter.exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
)

from omnikinverter import tcp_handler

@dataclass
class OmnikTcpRequest:
    host: str
    serial_number: int
    tcp_port: int
    request_timeout: float
    _close_session: bool = False

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

        # Define the await function.
        open_connection = asyncio.open_connection(self.host, self.tcp_port)
        
        try:
            # Await for the method with a timeout.
            reader, writer = await asyncio.wait_for(open_connection, self.request_timeout)
        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred when opening a TCP connection to the Omnik Inverter device"
            ) from exception
        except OSError as exception:
            raise OmnikInverterConnectionError(
                "Failed to open a TCP connection to the Omnik Inverter device"
            ) from exception

        try:
            writer.write(tcp_handler.create_information_request(self.serial_number))
            await writer.drain()

            raw_msg = await reader.read(1024)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError as exception:
                raise OmnikInverterConnectionError(
                    "Failed to communicate with the Omnik Inverter device over TCP"
                ) from exception

        return tcp_handler.parse_messages(self.serial_number, raw_msg)

    def _validate_request(self) -> None:
        if self.serial_number is None:
            raise OmnikInverterAuthError("serial_number is missing from the request")
