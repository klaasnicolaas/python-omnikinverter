<!-- Banner -->
![alt Banner of the Omnik Inverter package](https://raw.githubusercontent.com/klaasnicolaas/python-omnikinverter/main/assets/header_omnik_inverter-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Code Coverage][codecov-shield]][codecov-url]

Asynchronous Python client for the Omnik Inverter.

## About

A python package with which you can read the data from your Omnik Inverter. Keep in mind that this repository uses webscraping, this is **not** a neat way of data processing but due to the lack of a local API this is the only option.

**NOTE**: In mid-2021, manufacturer Omnik was declared bankrupt. You can find more information about what your alternatives are [here][energiewacht].

## Supported models

| Brand    | Model            | Datasource |
|----------|------------------|------------|
| Omnik    | Omniksol 1000TL  | JS         |
| Omnik    | Omniksol 1500TL  | JS         |
| Omnik    | Omniksol 2000TL  | JS         |
| Omnik    | Omniksol 2000TL2 | JSON       |
| Omnik    | Omniksol 2500TL  | HTML       |
| Omnik    | Omniksol 3000TL  | TCP        |
| Omnik    | Omniksol 4000TL2 | JS         |
| Ginlong  | Solis-DLS-WiFi   | JSON/HTML  |
| Hosola   | 1500TL           | JS         |
| Hosala   | Bright 2500MTL-S | JS         |
| Bosswerk | BW-MI300         | HTML       |
| Bosswerk | BW-MI600         | HTML       |
| Sofar    | 3600TLM          | HTML       |
| Sofar    | 2200TL           | JS         |
| Huayu    | HY-600-Pro       | HTML       |

## Installation

```bash
pip install omnikinverter
```

## Usage

```python
import asyncio

from omnikinverter import OmnikInverter


async def main():
    """Show example on getting Omnik Inverter data."""
    async with OmnikInverter(
        host="example_host",
        source_type="javascript",
        username="omnik",
        password="inverter",
    ) as client:
        inverter = await client.inverter()
        device = await client.device()
        print(inverter)
        print(device)


if __name__ == "__main__":
    asyncio.run(main())
```

For the **source type** you can choose between: `javascript` (default), `json`, `html` and `tcp`.

## Data

You can read the following data with this package:

### Inverter

- Serial Number
- Inverter Model
- Firmware Version - Main
- Firmware Version - Slave
- Alarm Code
- Rated Power (W)
- Current Power Production (W)
- Day Energy Production (kWh)
- Total Energy Production (kWh)

On the `tcp` source type you can also find:

- Inverter temperature;
- Voltage and current for the DC input strings (up to 3)
- Voltage, current, frequency and power for all AC outputs (also up to 3)
- Total number of runtime hours.

### Device

- Signal Quality (only with JS)
- Firmware Version
- IP Address

## Use cases

This python package is used in the following projects, among others:

- [home-assistant-omnik-inverter][omnik-inverter] by Robbin Janssen

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.12+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Pre-commit

This repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. To setup the pre-commit check, run:

```bash
poetry run pre-commit install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run pre-commit run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2021-2025 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[energiewacht]: https://www.energiewacht.com/hoofdsite/home/nieuws/omnik-failliet/
[omnik-inverter]: https://github.com/robbinjanssen/home-assistant-omnik-inverter

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-omnikinverter/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-omnikinverter/actions/workflows/tests.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-omnikinverter.svg
[commits-url]: https://github.com/klaasnicolaas/python-omnikinverter/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-omnikinverter/branch/main/graph/badge.svg?token=VQTR24YFQ9
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-omnikinverter
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-omnikinverter
[downloads-shield]: https://img.shields.io/pypi/dm/omnikinverter
[downloads-url]: https://pypistats.org/packages/omnikinverter
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-omnikinverter.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-omnikinverter.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/omnikinverter/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/omnikinverter
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-omnikinverter.svg
[releases]: https://github.com/klaasnicolaas/python-omnikinverter/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
