"""Tests for the utils module."""

import pathlib

import tomli

from datadoc_editor.utils import get_app_version
from datadoc_editor.utils import running_in_notebook


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_get_app_version():
    with (pathlib.Path(__file__).parent.parent / "pyproject.toml").open("rb") as f:
        pyproject = tomli.load(f)

    assert get_app_version() == pyproject["project"]["version"]
