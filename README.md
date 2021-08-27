## Python - Omnik Inverter Client

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Contributors][contributors-shield]][contributors-url]

[![Code Quality][code-quality-shield]][code-quality]
[![Maintainability][maintainability-shield]][maintainability-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]

Asynchronous Python client for the Omnik Inverter.

## About

A python package with which you can read the data from your Omnik Inverter. Keep in mind that this repository uses webscraping, this is **not** a neat way of data processing but due to the lack of a local API this is the only option.

**NOTE**: In mid-2021, manufacturer Omnik was declared bankrupt. You can find more information about what your alternatives are [here][energiewacht].

## Supported models

- Omnik2000TL2

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
    async with OmnikInverter(host="example_host") as client:
        inverter = await client.inverter()
        print(inverter)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

# Data

You can read the following data with this package:

- Serial Number
- Inverter Model
- Firmware Version
- Current Power Production (W)
- Day Energy Production (kWh)
- Total Energy Production (kWh)

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency
manager. But also relies on the use of NodeJS for certain checks during
development.

You need at least:

- Python 3.8+
- [Poetry][poetry-install]

Create a virtualenv and enter it:

```bash
python3 -m venv venv
source venv/bin/activate
```

To install all packages, including all development requirements:

```bash
poetry install
pre-commit install
```

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2021 Klaas Schoute

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

<!-- MARKDOWN LINKS & IMAGES -->
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-omnikinverter.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-omnikinverter/context:python
[contributors-shield]: https://img.shields.io/github/contributors/klaasnicolaas/python-omnikinverter.svg
[contributors-url]: https://github.com/klaasnicolaas/python-omnikinverter/graphs/contributors
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-omnikinverter.svg
[commits-url]: https://github.com/klaasnicolaas/python-omnikinverter/commits/master
[forks-shield]: https://img.shields.io/github/forks/klaasnicolaas/python-omnikinverter.svg
[forks-url]: https://github.com/klaasnicolaas/python-omnikinverter/network/members
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-omnikinverter.svg
[issues-url]: https://github.com/klaasnicolaas/python-omnikinverter/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-omnikinverter.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-omnikinverter.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2021.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/443c476612a574d82467/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-omnikinverter/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/omnikinverter/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/omnikinverter
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-omnikinverter.svg
[releases]: https://github.com/klaasnicolaas/python-omnikinverter/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-omnikinverter.svg
[stars-url]: https://github.com/klaasnicolaas/python-omnikinverter/stargazers

[energiewacht]: https://www.energiewacht.com/hoofdsite/home/nieuws/omnik-failliet/
[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
