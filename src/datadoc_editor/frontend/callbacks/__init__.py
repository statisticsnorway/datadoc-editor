"""Dash callback functions.

The actual decorated callbacks should be very minimal functions which
call other functions where the logic lives. This is done to support unit
testing because the decorated functions are difficult to test.

The functions where the logic lives should be categorised into files.
"""

from .register_callbacks import register_callbacks
from .pseudonymization_callbacks import register_pseudonymization_callbacks

def register_all_callbacks(app):
    register_callbacks(app)
    register_pseudonymization_callbacks(app)