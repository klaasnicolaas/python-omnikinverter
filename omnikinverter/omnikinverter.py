"""Asynchronous Python client for the Omnik Inverter."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from aiohttp.client import ClientSession

from .requests.http import OmnikHttpRequest
from .requests.tcp import OmnikTcpRequest

from .exceptions import OmnikInverterError
from .models import Device, Inverter


@dataclass
class OmnikInverter:
    """Main class for handling connections with the Omnik Inverter."""

    source_type: str
    http: OmnikHttpRequest | None = None
    tcp: OmnikTcpRequest | None = None
    
    _close_session: bool = False

    socket: None = None

    def __init__(
        self,
        host: str,
        source_type: str = "javascript",
        username: str | None = None,
        password: str | None = None,
        serial_number: int | None = None,
        tcp_port: int = 8899,
        request_timeout: float = 10.0,
        session: ClientSession | None = None,
    ) -> None:
        """
        Create a new Omnik instance.

        Args:
            host: The IP address of the inverter.
            source_type: The source type to get data from.
            username: The username for basic auth calls.
            password: The password for basic auth calls.
            serial_number: The serial number of the device.
            tcp_port: The TCP port to connect to.
            request_timeout: The maximum amount of seconds a request can take.
            session: The session to use, or a new session will be created.
        """
        self.source_type = source_type

        if self.source_type == 'tcp':
            self.tcp = OmnikTcpRequest(
                host=host,
                serial_number=serial_number,
                tcp_port=tcp_port,
                request_timeout=request_timeout
            )
        else:
            self.http = OmnikHttpRequest(
                host=host,
                source_type=source_type,
                username=username,
                password=password,
                request_timeout=request_timeout,
                session=session,
            )

    async def inverter(self) -> Inverter:
        """Get values from your Omnik Inverter.

        Returns:
            A Inverter data object from the Omnik Inverter.

        Raises:
            OmnikInverterError: Unknown source type.
        """
        if self.source_type == "json":
            data = await self.http.request("status.json", params={"CMD": "inv_query"})
            return Inverter.from_json(json.loads(data))
        if self.source_type == "html":
            data = await self.http.request("status.html")
            return Inverter.from_html(data)
        if self.source_type == "javascript":
            data = await self.http.request("js/status.js")
            return Inverter.from_js(data)
        if self.source_type == "tcp":
            fields = await self.tcp.request()
            return Inverter.from_tcp(fields)

        raise OmnikInverterError(f"Unknown source type `{self.source_type}`")

    async def device(self) -> Device:
        """Get values from the device.

        Returns:
            A Device data object from the Omnik Inverter. None on the "tcp" source_type.

        Raises:
            OmnikInverterError: Unknown source type.
        """
        if self.source_type == "json":
            data = await self.http.request("status.json", params={"CMD": "inv_query"})
            return Device.from_json(json.loads(data))
        if self.source_type == "html":
            data = await self.http.request("status.html")
            return Device.from_html(data)
        if self.source_type == "javascript":
            data = await self.http.request("js/status.js")
            return Device.from_js(data)
        if self.source_type == "tcp":
            # None of the fields are available through a TCP data dump.
            return Device()

        raise OmnikInverterError(f"Unknown source type `{self.source_type}`")

    async def __aenter__(self) -> OmnikInverter:
        """Async enter.

        Returns:
            The Omnik Inverter object.
        """
        return self

    async def __aexit__(self, *_exc_info: str) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        if self.http is not None:
            await self.http.close()
