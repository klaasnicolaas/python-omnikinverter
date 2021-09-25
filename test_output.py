# pylint: disable=W0621
"""Asynchronous Python client for the Omnik Inverter."""

import asyncio

from omnikinverter import OmnikInverter


async def main():
    """Test."""
    async with OmnikInverter(
        host="examples.com",
        source_type="js",
    ) as client:
        inverter: OmnikInverter = await client.inverter()
        device: OmnikInverter = await client.device()
        print(inverter)
        print()
        print("-- INVERTER --")
        print(f"Serial Number: {inverter.serial_number}")
        print(f"Model: {inverter.model}")
        print(f"Firmware Main: {inverter.firmware}")
        print(f"Firmware Slave: {inverter.firmware_slave}")
        print(f"Rated Power: {inverter.solar_rated_power}")
        print(f"Current Power: {inverter.solar_current_power}")
        print(f"Energy Production Today: {inverter.solar_energy_today}")
        print(f"Energy Production Total: {inverter.solar_energy_total}")
        print()
        print(device)
        print()
        print("-- DEVICE --")
        print(f"Signal Quality: {device.signal_quality}")
        print(f"Firmware: {device.firmware}")
        print(f"IP Address: {device.ip_address}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
