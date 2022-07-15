"""Asynchronous Python client for the Omnik Inverter."""
from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aiohttp
import async_timeout
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from . import tcp
from .exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
    OmnikInverterError,
)
from .models import Device, Inverter


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

    _socket_mock: None = None

    async def request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: Mapping[str, Any] | None = None,
    ) -> str:
        """Handle a request to a Omnik Inverter device.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP Method to use.
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (text) with the response from
            the Omnik Inverter.

        Raises:
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.
            OmnikInverterAuthError: Authentication failed with the Omnik Inverter.
            OmnikInverterError: Received an unexpected response from the Omnik Inverter.
        """
        url = URL.build(scheme="http", host=self.host, path="/").join(URL(uri))

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        # Use big try to make sure manual session is always cleaned up
        try:
            if self.source_type == "html" and (
                self.username is None or self.password is None
            ):
                raise OmnikInverterAuthError(
                    "A username and/or password is missing from the request"
                )
            auth = None
            if self.username and self.password:
                auth = aiohttp.BasicAuth(self.username, self.password)

            try:
                response = await self.session.request(
                    method,
                    url,
                    auth=auth,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
            except (ClientError, ClientResponseError) as exception:
                raise OmnikInverterConnectionError(
                    "Error occurred while communicating with Omnik Inverter device"
                ) from exception

            types = ["application/json", "application/x-javascript", "text/html"]
            content_type = response.headers.get("Content-Type", "")
            if not any(item in content_type for item in types):
                text = await response.text()
                raise OmnikInverterError(
                    "Unexpected response from the Omnik Inverter device",
                    {"Content-Type": content_type, "response": text},
                )

            raw_response = await response.read()
        finally:
            if self.session and self._close_session:
                await self.session.close()
                self.session = None
                self._close_session = False

        return raw_response.decode("ascii", "ignore")

    async def tcp_request(self) -> dict[str, Any]:
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
        if self.serial_number is None:
            raise OmnikInverterAuthError("serial_number is missing from the request")

        try:
            if self._socket_mock is not None:
                reader, writer = await asyncio.open_connection(sock=self._socket_mock)
            else:  # pragma: no cover
                reader, writer = await asyncio.open_connection(self.host, self.tcp_port)
        except OSError as exception:
            raise OmnikInverterConnectionError(
                "Failed to open a TCP connection to the Omnik Inverter device"
            ) from exception

        try:
            writer.write(tcp.create_information_request(self.serial_number))
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

        return tcp.parse_messages(self.serial_number, raw_msg)

    async def inverter(self) -> Inverter:
        """Get values from your Omnik Inverter.

        Returns:
            A Inverter data object from the Omnik Inverter.

        Raises:
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.
            OmnikInverterError: Unknown source type.
        """
        try:
            async with async_timeout.timeout(self.request_timeout):
                if self.source_type == "json":
                    data = await self.request(
                        "status.json", params={"CMD": "inv_query"}
                    )
                    return Inverter.from_json(json.loads(data))
                if self.source_type == "html":
                    data = await self.request("status.html")
                    return Inverter.from_html(data)
                if self.source_type == "javascript":
                    data = await self.request("js/status.js")
                    return Inverter.from_js(data)
                if self.source_type == "tcp":
                    fields = await self.tcp_request()
                    return Inverter.from_tcp(fields)
        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred while connecting to Omnik Inverter device"
            ) from exception

        raise OmnikInverterError(f"Unknown source type `{self.source_type}`")

    async def device(self) -> Device:
        """Get values from the device.

        Returns:
            A Device data object from the Omnik Inverter. None on the "tcp" source_type.

        Raises:
            OmnikInverterConnectionError: An error occurred while communicating
                with the Omnik Inverter.
            OmnikInverterError: Unknown source type.
        """
        try:
            async with async_timeout.timeout(self.request_timeout):
                if self.source_type == "json":
                    data = await self.request(
                        "status.json", params={"CMD": "inv_query"}
                    )
                    return Device.from_json(json.loads(data))
                if self.source_type == "html":
                    data = await self.request("status.html")
                    return Device.from_html(data)
                if self.source_type == "javascript":
                    data = await self.request("js/status.js")
                    return Device.from_js(data)
                if self.source_type == "tcp":
                    # None of the fields are available through a TCP data dump.
                    return Device()
        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred while connecting to Omnik Inverter device"
            ) from exception

        raise OmnikInverterError(f"Unknown source type `{self.source_type}`")

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

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
        await self.close()
