# pylint: disable=W0621
"""Asynchronous Python client for the Omnik Inverter."""

import asyncio

from omnikinverter import OmnikInverter


async def main():
    """Test."""
    async with OmnikInverter(
        host="example.com",
        json_input=False,
    ) as omnik:
        inverter: OmnikInverter = await omnik.inverter()
        print(f"Omnik Inverter: {inverter}")
        print()
        print(f"Serial Number: {inverter.serial_number}")
        print(f"Model: {inverter.model}")
        print(f"Firmware: {inverter.firmware}")
        print(f"Current Power: {inverter.solar_current_power}")
        print(f"Energy Production Today: {inverter.solar_energy_today}")
        print(f"Energy Production Total: {inverter.solar_energy_total}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
