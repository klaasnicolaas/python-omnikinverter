# pylint: disable=W0621
"""Asynchronous TCP Python client for the Omnik Inverter."""

import asyncio
import logging

from omnikinverter import Inverter, OmnikInverter

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    """Locally gather statistics over TCP."""
    async with OmnikInverter(
        host="examples.com",
        source_type="tcp",
        serial_number=123456789,
    ) as client:
        inverter: Inverter = (await client.perform_request()).inverter()
        # TCP backend (currently?) doesn't provide WiFi module statistics,
        # so we're not querying .device() here.
        print(inverter)
        print()
        print("-- INVERTER --")
        print(f"Serial Number: {inverter.serial_number}")
        print(f"Model: {inverter.model}")
        print(f"Firmware Main: {inverter.firmware}")
        print(f"Firmware Slave: {inverter.firmware_slave}")
        print(f"Current Power: {inverter.solar_current_power}W")
        print(f"Energy Production Today: {inverter.solar_energy_today}kWh")
        print(f"Energy Production Total: {inverter.solar_energy_total}kWh")

        optional_fields = [
            ("solar_rated_power", "Rated Power", "W"),
            ("temperature", "Temperature", "°C"),
            ("solar_hours_total", "Solar Hours Total", "h"),
            ("dc_input_voltage", "DC Input Voltage", "V"),
            ("dc_input_current", "DC Input Current", "A"),
            ("ac_output_voltage", "AC Output Voltage", "V"),
            ("ac_output_current", "AC Output Current", "A"),
            ("ac_output_frequency", "AC Output Frequency", "Hz"),
            ("ac_output_power", "AC Output Power", "W"),
            ("inverter_active", "Inverter Active", ""),
        ]

        for field, name, unit in optional_fields:
            if (val := getattr(inverter, field)) is not None:
                if isinstance(val, list):
                    values = ", ".join(
                        f"{v2:.1f}{unit}" for v2 in val if v2 is not None
                    )
                    print(f"{name}: {values}")
                elif isinstance(val, float):
                    print(f"{name}: {val:.1f}{unit}")
                else:
                    print(f"{name}: {val}{unit}")


if __name__ == "__main__":
    asyncio.run(main())
