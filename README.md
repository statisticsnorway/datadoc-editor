# Datadoc

[![PyPI](https://img.shields.io/pypi/v/ssb-datadoc.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ssb-datadoc.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ssb-datadoc)][pypi status]
[![License](https://img.shields.io/pypi/l/ssb-datadoc)][license]

[![Documentation](https://github.com/statisticsnorway/datadoc-editor/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/datadoc-editor/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_datadoc&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_datadoc&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)][uv]

[pypi status]: https://pypi.org/project/ssb-datadoc/
[documentation]: https://statisticsnorway.github.io/datadoc
[tests]: https://github.com/statisticsnorway/datadoc-editor/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_datadoc
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_datadoc
[pre-commit]: https://github.com/pre-commit/pre-commit
[uv]: https://docs.astral.sh/uv/

## Features

- Describe a dataset and its variables according to Statistics Norway's metadata model.
- Supports `parquet` and `sas7bdat` dataset files.
- Supports local file system and Google Cloud Storage buckets.

## Installation

You can install _Datadoc_ via [pipx] from [PyPI]:

```console
pipx install ssb-datadoc
```

## Usage

Datadoc is available on [Dapla Lab](https://lab.dapla.ssb.no/) and works best there.

Usage instructions: <https://manual.dapla.ssb.no/statistikkere/datadoc.html>

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Datadoc_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/datadoc-editor/issues
[pipx]: https://pipx.pypa.io/latest/installation/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/datadoc-editor/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/datadoc-editor/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/datadoc-editor/reference.html
