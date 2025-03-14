# -*- coding: utf-8 -*-

"""
Defines machine modes and options.

This module contains enumeration classes that define different machine
states, options, and configurations for G-code generation. Each enum
value is linked to a specific G-Code instruction and a description, which
are stored in the `vpype_mecode.enums.codes_table`. The `GBuilder` class
uses this table to create the appropriate G-code statements.
"""

from .base_enum import BaseEnum
from .modes import BedMode
from .modes import CoolantMode
from .modes import DirectWriteMode
from .modes import FanMode
from .modes import HeadMode
from .modes import RackMode
from .modes import ToolMode
from .types import BedTemperature
from .types import DistanceMode
from .types import ExtrusionMode
from .types import FeedMode
from .types import HaltMode
from .types import HotendTemperature
from .types import Plane
from .types import PowerMode
from .types import SpinMode
from .units import LengthUnits
from .units import TemperatureUnits
from .units import TimeUnits

__all__ = [
    "BaseEnum",
    "BedMode",
    "BedTemperature",
    "CoolantMode",
    "DirectWriteMode",
    "DistanceMode",
    "ExtrusionMode",
    "FanMode",
    "FeedMode",
    "HaltMode",
    "HeadMode",
    "HotendTemperature",
    "LengthUnits",
    "Plane",
    "PowerMode",
    "RackMode",
    "SpinMode",
    "TemperatureUnits",
    "TimeUnits",
    "ToolMode",
]
