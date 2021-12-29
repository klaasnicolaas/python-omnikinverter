"""Asynchronous Python client for the Omnik Inverter."""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aiohttp
import async_timeout
from aiohttp.client import ClientError, ClientResponseError
from aiohttp.hdrs import METH_GET
from yarl import URL

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
    request_timeout: int = 10

    async def request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
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
            with async_timeout.timeout(self.request_timeout):
                async with aiohttp.request(
                    method,
                    url,
                    auth=auth,
                    params=params,
                    headers=headers,
                ) as response:
                    response.raise_for_status()

                    types = [
                        "application/json",
                        "application/x-javascript",
                        "text/html",
                    ]
                    content_type = response.headers.get("Content-Type", "")
                    if not any(item in content_type for item in types):
                        text = await response.text()
                        raise OmnikInverterError(
                            "Unexpected response from the Omnik Inverter device",
                            {"Content-Type": content_type, "response": text},
                        )

                    return await response.text()

        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred while connecting to Omnik Inverter device"
            ) from exception
        except (ClientError, ClientResponseError) as exception:
            raise OmnikInverterConnectionError(
                "Error occurred while communicating with Omnik Inverter device"
            ) from exception

    async def inverter(self) -> Inverter:
        """Get values from your Omnik Inverter.

        Returns:
            A Inverter data object from the Omnik Inverter.
        """
        if self.source_type == "json":
            data = await self.request("status.json", params={"CMD": "inv_query"})
            return Inverter.from_json(data)
        if self.source_type == "html":
            data = await self.request("status.html")
            return Inverter.from_html(data)
        data = await self.request("js/status.js")
        return Inverter.from_js(data)

    async def device(self) -> Device:
        """Get values from the device.

        Returns:
            A Device data object from the Omnik Inverter.
        """
        if self.source_type == "json":
            data = await self.request("status.json", params={"CMD": "inv_query"})
            return Device.from_json(data)
        if self.source_type == "html":
            data = await self.request("status.html")
            return Device.from_html(data)
        data = await self.request("js/status.js")
        return Device.from_js(data)

    async def __aenter__(self) -> OmnikInverter:
        """Async enter.

        Returns:
            The Omnik Inverter object.
        """
        return self

    async def __aexit__(self, *_exc_info) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
