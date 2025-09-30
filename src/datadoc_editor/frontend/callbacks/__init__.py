"""Dash callback functions.

This package initializer collects and exposes all callback definitions from separate modules.

Callbacks are imported here from their respective modules and exposed in a single namespace
for easier access and maintainability.

Callbacks should be organized according to logical, practical, or thematic groupings.
This helps keep related functionality together and makes it easier
to extend or replace callbacks as the project evolves.

Before creating a new module, check if an appropriate callback module already exists.

All callbacks should be added in 'register_all_callbacks'.

The actual decorated callbacks should be minimal functions that
call other functions where the main logic resides. This approach supports unit testing,
as decorated functions are otherwise difficult to test.

Functions containing the main logic should be categorized into separate files.
"""

from dash import Dash

from .dataset_callbacks import register_dataset_callbacks
from .global_variables_callbacks import register_global_variables_callbacks
from .pseudonymization_callbacks import register_pseudonymization_callbacks
from .register_callbacks import register_callbacks
from .use_restrictions_callbacks import register_use_restriction_callbacks
from .variables_callbacks import register_variables_callbacks


def register_all_callbacks(app: Dash) -> None:
    """All registered callbacks in app."""
    register_callbacks(app)
    register_dataset_callbacks(app)
    register_variables_callbacks(app)
    register_pseudonymization_callbacks(app)
    register_use_restriction_callbacks(app)
    register_global_variables_callbacks(app)
