# -*- coding: utf-8 -*-

# G-Code generator for Vpype.
# Copyright (C) 2025 Joan Sala <contact@joansala.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import dataclasses
from typing import Optional

import vpype as vp
from pydantic import BaseModel, Field

from vpype_mecode.enums import DirectWriteMode
from .base_config import BaseConfig


@dataclasses.dataclass
class MecodeConfig(BaseModel, BaseConfig):
    """
    Configuration settings for the `mecode` library.

    This class stores various options that are passed directly to the
    `mecode` library, which is responsible for generating the G-Code.
    See the :doc:`command line reference </cli>` for detailed information
    about the properties of this class.

    Example:
        >>> params = { 'output': 'output.gcode' }
        >>> mecode_config = MecodeConfig.model_validate(params)
        >>> print(mecode_config.output)
    """

    # Predefined settings (do not change)
    setup: bool = Field(False)
    absolute: bool = Field(True)
    print_lines: bool | str = Field("auto")
    extrude: bool = Field(False)

    # Output settings
    output: Optional[str] = Field(None)
    header: Optional[str] = Field(None)
    footer: Optional[str] = Field(None)
    aerotech_include: bool = Field(False)
    decimal_places: int = Field(5, ge=0)
    comment_symbols: str = Field("(")
    line_endings: str = Field("os")

    # Direct write settings
    direct_write_mode: DirectWriteMode = Field(DirectWriteMode.OFF)
    host: str = Field("localhost")
    port: int = Field(8000, ge=0)
    baudrate: int = Field(250000, ge=0)
    wait_for_response: bool = Field(False)

    # Axis naming settings
    x_axis: str = Field("X")
    y_axis: str = Field("Y")
    z_axis: str = Field("Z")
    i_axis: str = Field("I")
    j_axis: str = Field("J")
    k_axis: str = Field("K")

    # Extrusion parameters (currently unused)
    filament_diameter: float = Field(vp.convert_length("1.75mm"))
    layer_height: Optional[float] = Field(vp.convert_length("0.2mm"))
    extrusion_width: Optional[float] = Field(vp.convert_length("0.35mm"))
    extrusion_multiplier: float = Field(1.0)

    # Vpype's default unit of measure is pixels, so we may need to
    # convert some values to work units (millimeters or inches).

    _fields_with_px_units = {
        "extrusion_width": "px",
        "filament_diameter": "px",
        "layer_height": "px",
    }
