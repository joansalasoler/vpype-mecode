# -*- coding: utf-8 -*-

"""
Exceptions and errors.

This module defines a collection of exceptions to handle errors related
to G-code processing and generation.
"""

from .gcode_errors import GCodeError
from .gcode_errors import ToolStateError
from .gcode_errors import CoolantStateError
from .plugin_errors import ImageLoadError
from .plugin_errors import VpypeMecodeError

__all__ = [
    "GCodeError",
    "ToolStateError",
    "CoolantStateError",
    "ImageLoadError",
    "VpypeMecodeError",
]
