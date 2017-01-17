"""
Init for rubber.
"""
from .version import __version__  # noqa

from rubber.apps import get_rubber_config  # noqa

default_app_config = 'rubber.apps.RubberConfig'
