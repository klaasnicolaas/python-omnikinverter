# pylint: disable=W0621
"""Asynchronous Python client for the Omnik Inverter."""

import asyncio

from omnikinverter import OmnikInverter


async def main():
    """Test."""
    async with OmnikInverter(
        host="example",
    ) as omnik:
        inverter: OmnikInverter = await omnik.inverter()
        print(f"Omnik Inverter: {inverter}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
