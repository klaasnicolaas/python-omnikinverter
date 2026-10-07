"""Asynchronous Python client for the Omnik Inverter."""

from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from . import tcp
from .exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
    OmnikInverterError,
)
from .models import Device, Inverter, OmnikInverterData

VERSION: str = metadata.version("omnikinverter")


@dataclass
class OmnikInverter:
    """Main class for handling connections with the Omnik Inverter."""

    host: str
    username: str | None = None
    password: str | None = None
    source_type: str = "javascript"
    request_timeout: float = 10.0
    session: ClientSession | None = None
    serial_number: int | None = None  # Optional, only for TCP backend
    tcp_port: int = 8899

    _close_session: bool = False

    async def request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to a Omnik Inverter device.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP Method to use.
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (text) with the response from
            the Omnik Inverter.

        Raises:
        ------
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.
            OmnikInverterAuthError: Authentication failed with the Omnik Inverter.
            OmnikInverterError: Received an unexpected response from the Omnik Inverter.

        """
        url = URL.build(scheme="http", host=self.host, path="/").join(URL(uri))

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "User-Agent": f"PythonOmnikInverter/{VERSION}",
        }

        if self.source_type == "html" and (
            self.username is None or self.password is None
        ):
            msg = "A username and/or password is missing from the request"
            raise OmnikInverterAuthError(msg)

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        if self.username and self.password:
            credentials = f"{self.username}:{self.password}".encode("latin1")
            headers["Authorization"] = f"Basic {base64.b64encode(credentials).decode()}"

        # Use big try to make sure manual session is always cleaned up
        try:
            try:
                async with asyncio.timeout(self.request_timeout):
                    response = await self.session.request(
                        method,
                        url,
                        params=params,
                        headers=headers,
                    )
                    response.raise_for_status()
                    raw_response = await response.read()
            except TimeoutError as exception:
                msg = "Timeout occurred while connecting to Omnik Inverter device"
                raise OmnikInverterConnectionError(msg) from exception
            except (ClientError, ClientResponseError) as exception:
                msg = "Error occurred while communicating with Omnik Inverter device"
                raise OmnikInverterConnectionError(msg) from exception
        finally:
            await self.close()

        types = ["application/json", "application/x-javascript", "text/html"]
        content_type = response.headers.get("Content-Type", "")
        if not any(item in content_type for item in types):
            text = await response.text()
            msg = "Unexpected response from the Omnik Inverter device"
            raise OmnikInverterError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return raw_response.decode("ascii", "ignore")

    async def tcp_request(self) -> dict[str, Any]:
        """Perform a raw TCP request to the Omnik device.

        Returns
        -------
            A Python dictionary (text) with the response from
            the Omnik Inverter.

        Raises
        ------
            OmnikInverterAuthError: Serial number is required to communicate
                with the Omnik Inverter.
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.

        """
        if self.serial_number is None:
            msg = "serial_number is missing from the request"
            raise OmnikInverterAuthError(msg)

        try:
            async with asyncio.timeout(self.request_timeout):
                reader, writer = await asyncio.open_connection(self.host, self.tcp_port)
        except TimeoutError as exception:  # pragma: no cover
            msg = "Timeout occurred while connecting to the Omnik Inverter device"
            raise OmnikInverterConnectionError(msg) from exception
        except OSError as exception:
            msg = "Failed to open a TCP connection to the Omnik Inverter device"
            raise OmnikInverterConnectionError(msg) from exception

        try:
            async with asyncio.timeout(self.request_timeout):
                writer.write(tcp.create_information_request(self.serial_number))
                await writer.drain()

                # The reply may arrive in multiple TCP segments, keep reading
                # until all announced messages are complete.
                raw_msg = bytearray()
                while not tcp.is_complete(raw_msg):
                    chunk = await reader.read(1024)
                    if not chunk:
                        break
                    raw_msg.extend(chunk)
        except TimeoutError as exception:
            msg = "Timeout occurred while communicating with the Omnik Inverter device"
            raise OmnikInverterConnectionError(msg) from exception
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError as exception:
                msg = "Failed to communicate with the Omnik Inverter device over TCP"
                raise OmnikInverterConnectionError(msg) from exception

        return tcp.parse_messages(self.serial_number, raw_msg)

    async def _fetch(self) -> str | dict[str, Any]:
        """Fetch the raw status data from the Omnik Inverter.

        Returns
        -------
            The decoded response for the web sources, or the parsed
            fields for the TCP source.

        Raises
        ------
            OmnikInverterError: Unknown source type.

        """
        if self.source_type == "json":
            return await self.request("status.json", params={"CMD": "inv_query"})
        if self.source_type == "html":
            return await self.request("status.html")
        if self.source_type == "javascript":
            return await self.request("js/status.js")
        if self.source_type == "tcp":
            return await self.tcp_request()

        msg = f"Unknown source type `{self.source_type}`"
        raise OmnikInverterError(msg)

    def _parse_inverter(self, data: str | dict[str, Any]) -> Inverter:
        """Parse raw status data into an Inverter object."""
        if isinstance(data, dict):
            return Inverter.from_tcp(data)
        if self.source_type == "json":
            return Inverter.from_json(json.loads(data))
        if self.source_type == "html":
            return Inverter.from_html(data)
        return Inverter.from_js(data)

    def _parse_device(self, data: str | dict[str, Any]) -> Device:
        """Parse raw status data into a Device object."""
        if isinstance(data, dict):
            # None of the fields are available through a TCP data dump.
            return Device()
        if self.source_type == "json":
            return Device.from_json(json.loads(data))
        if self.source_type == "html":
            return Device.from_html(data)
        return Device.from_js(data)

    async def data(self) -> OmnikInverterData:
        """Get both the Inverter and Device values with a single request.

        Returns
        -------
            An OmnikInverterData object holding the Inverter and Device
            data from the Omnik Inverter.

        """
        data = await self._fetch()
        return OmnikInverterData(
            inverter=self._parse_inverter(data),
            device=self._parse_device(data),
        )

    async def inverter(self) -> Inverter:
        """Get values from your Omnik Inverter.

        Returns
        -------
            A Inverter data object from the Omnik Inverter.

        """
        return self._parse_inverter(await self._fetch())

    async def device(self) -> Device:
        """Get values from the device.

        Returns
        -------
            A Device data object from the Omnik Inverter. Empty on the "tcp"
            source_type.

        """
        if self.source_type == "tcp":
            # None of the fields are available through a TCP data dump,
            # so there is no need to contact the inverter.
            return Device()
        return self._parse_device(await self._fetch())

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()
            self.session = None
            self._close_session = False

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Omnik Inverter object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
