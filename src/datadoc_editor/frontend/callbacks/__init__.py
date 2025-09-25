"""Dash callback functions.

The actual decorated callbacks should be very minimal functions which
call other functions where the logic lives. This is done to support unit
testing because the decorated functions are difficult to test.

The functions where the logic lives should be categorised into files.
"""

from dash import Dash

from .pseudonymization_callbacks import register_pseudonymization_callbacks
from .register_callbacks import register_callbacks
from .use_restrictions_callbacks import register_use_restriction_callbacks


def register_all_callbacks(app: Dash) -> None:
    """All register callbacks in app."""
    register_callbacks(app)
    register_pseudonymization_callbacks(app)
    register_use_restriction_callbacks(app)
