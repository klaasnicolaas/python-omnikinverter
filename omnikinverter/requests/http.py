"""Create HTTP Requests for the Omnik Inverter."""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import async_timeout
from aiohttp import BasicAuth
from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from omnikinverter.exceptions import (
    OmnikInverterAuthError,
    OmnikInverterConnectionError,
    OmnikInverterError,
)

@dataclass
class OmnikHttpRequest:
    host: str
    source_type: str
    username: str | None
    password: str | None
    request_timeout: float
    session: ClientSession | None

    _close_session: bool = False

    def __init__(
        self,
        host: str,
        source_type: str,
        username: str,
        password: str,
        request_timeout: float,
        session: ClientSession | None,
    ) -> None:
        """
        Create a new HTTP Request instance.

        Args:
            host: The IP address of the inverter.
            source_type: The source type to get data from.
            username: The username for basic auth calls.
            password: The password for basic auth calls.
            request_timeout: The maximum amount of seconds a request can take.
            session: The session to use, or a new session will be created.
        """
        self.host = host
        self.source_type = source_type
        self.username = username
        self.password = password
        self.request_timeout = request_timeout
        self.session = session

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

        # Make sure the request is valid.
        self._validate_request()

        # Open a session
        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    # Get the auth method for HTML sources.
                    auth=self._get_basic_auth(),
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise OmnikInverterConnectionError(
                "Timeout occurred while connecting to Omnik Inverter device"
            ) from exception
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

        return raw_response.decode("ascii", "ignore")

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()
        
    def _validate_request(self) -> None:
        if self.source_type == "html" and (
            self.username is None or self.password is None
        ):
            raise OmnikInverterAuthError("A username and/or password is missing from the request")

    def _get_basic_auth(self) -> BasicAuth|None:
        if self.source_type == "html":
            return BasicAuth(self.username, self.password)
        
        return None
