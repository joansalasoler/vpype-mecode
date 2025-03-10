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

"""
Configuration options.

This module defines all available configuration options that can be used
to customize the G-Code generation process. They are used both to parse
the command line options and the TOML configuration files.
"""

from vpype_cli import TextType, IntRangeType, FloatRangeType
from vpype_cli import IntegerType, LengthType, PathType

from vpype_mecode.config import ConfigOption
from vpype_mecode.enums import *


command_options = (


    # ------------------------------------------------------------------
    # Global Options
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='outfile',
        type=PathType(dir_okay=False, writable=True),
        help="""
        File path where the generated G-Code will be saved. If not
        specified, the G-Code will be printed to the terminal.
        """,
    ),
    ConfigOption(
        option_name='render_config',
        type=PathType(exists=True, dir_okay=False, resolve_path=True),
        default=None,
        help="""
        Path to a TOML file containing configuration settings specific
        to the document and each of its layers.
        """,
    ),

    # ------------------------------------------------------------------
    # G-Code Renderer Options
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='length_units',
        type=LengthUnits,
        help="""
        Choose the unit of measurement for the output G-Code.
        """,
    ),
    ConfigOption(
        option_name='time_units',
        type=TimeUnits,
        help="""
        Choose the unit of time for the output G-Code. Used to specify
        program execution delays.
        """,
    ),
    ConfigOption(
        option_name='head_mode',
        type=HeadMode,
        help="""
        Specifies the head type for G-code generation. The head determines
        how axis movements are generated and coordinated.
        """,
    ),
    ConfigOption(
        option_name='tool_mode',
        type=ToolMode,
        help="""
        Specifies the tool type for G-code generation. The generated
        code adapts to the selected tool type.
        """,
    ),
    ConfigOption(
        option_name='rack_mode',
        type=RackMode,
        help="""
        Specifies if tool changes are needed between layers or if the
        machine can handle multiple tools.
        """,
    ),
    ConfigOption(
        option_name='coolant_mode',
        type=CoolantMode,
        help="""
        Selects the type of coolant used during operation.
        """,
    ),
    ConfigOption(
        option_name='fan_mode',
        type=FanMode,
        help="""
        Selects the type of fan used during operation.
        """,
    ),
    ConfigOption(
        option_name='bed_mode',
        type=BedMode,
        help="""
        Selects the type of bed used for operation.
        """,
    ),
    ConfigOption(
        option_name='work_speed',
        type=LengthType(),
        help="""
        The speed at which the tool moves while performing an operation
        (cutting, drawing, etc). Measured in units per minute.
        """,
    ),
    ConfigOption(
        option_name='plunge_speed',
        type=LengthType(),
        help="""
        The speed at which the tool moves during the plunging phase,
        where it enters the material. The plunge is typically slower than
        the work speed to ensure controlled entry. Measured in units per
        minute.
        """,
    ),
    ConfigOption(
        option_name='travel_speed',
        type=LengthType(),
        help="""
        The speed at which the tool moves between operations, without
        interacting with the material or work surface, measured in units
        per minute.
        """,
    ),
    ConfigOption(
        option_name='fan_speed',
        type=IntRangeType(min=0, max=255),
        help="""
        The speed at which the fan rotates during operations. A value
        of 0 turns off the fan, while a value of 255 sets it to its
        maximum speed.
        """,
    ),
    ConfigOption(
        option_name='bed_temperature',
        type=IntegerType(),
        help="""
        The temperature at which the heated bed is set during operation,
        measured in celcius degrees.
        """,
    ),
    ConfigOption(
        option_name='power_level',
        type=IntRangeType(min=0),
        help="""
        Controls the intensity of energy-based tools such as laser
        cutters, plasma cutters, or 3D printer extruders.
        """,
    ),
    ConfigOption(
        option_name='spindle_rpm',
        type=IntRangeType(min=0),
        help="""
        Controls the rotational speed of the spindle, used for rotating
        tools such as  mills, drills, and routers. The value is measured
        in revolutions per minute (RPM).
        """,
    ),
    ConfigOption(
        option_name='spin_mode',
        type=SpinMode,
        help="""
        Sets the rotation direction of the spindle.
        """,
    ),
    ConfigOption(
        option_name='power_mode',
        type=PowerMode,
        help="""
        Sets the power mode of the tool.
        """,
    ),
    ConfigOption(
        option_name='warmup_delay',
        type=FloatRangeType(min=0.001),
        help="""
        Time to wait in seconds after tool activation or deactivation
        before starting any movement. This ensures the tool reaches its
        target state (power, speed, etc) before operating.
        """,
    ),
    ConfigOption(
        option_name='tool_number',
        type=IntRangeType(min=1),
        help="""
        Specify the tool number to be used for machining operations.
        """,
    ),
    ConfigOption(
        option_name='work_z',
        type=LengthType(),
        help="""
        The Z-axis height at which the tool will perform its active work
        (cutting, drawing, printing, etc).
        """,
    ),
    ConfigOption(
        option_name='plunge_z',
        type=LengthType(),
        help="""
        The Z-axis height at which the tool begins plunging into the
        material. This is usually just above the final work Z, allowing
        the tool to gradually enter the material.
        """,
    ),
    ConfigOption(
        option_name='safe_z',
        type=LengthType(),
        help="""
        The Z-axis height the tool moves to when traveling between
        operations, ensuring it does not collide with the material.
        """,
    ),
    ConfigOption(
        option_name='park_z',
        type=LengthType(),
        help="""
        The Z-axis parking height where the tool retracts for maintenance
        operations, such as tool changes and program completion.
        """,
    ),

    # ------------------------------------------------------------------
    # G-Code Transform Options
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='height_map_path',
        type=PathType(exists=True, dir_okay=False, resolve_path=True),
        help="""
        Path to a heightmap image file that defines surface variations
        across the work area. The image is interpreted as a grid of
        values that can be used to dynamically adjust various parameters
        during operation, such as tool height or power levels.
        """,
    ),
    ConfigOption(
        option_name='height_map_scale',
        type=FloatRangeType(min=0.0),
        help="""
        Scaling factor applied to normalized heightmap values (0.0 to 1.0)
        to convert them into actual work units. For example, a scale of 10
        means a heightmap value of 1.0 becomes 10 units.
        """,
    ),
    ConfigOption(
        option_name='height_map_tolerance',
        type=FloatRangeType(min=0.0),
        help="""
        Minimum height difference threshold used when sampling points
        from the height map. Points with height differences below this
        value will be filtered out. Measured in work units.
        """,
    ),

    # ------------------------------------------------------------------
    # G-Code Output Options (mecode)
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='header',
        type=PathType(exists=True, dir_okay=False, resolve_path=True),
        help="""
        Path to a file containing custom G-Code lines to be added at the
        beginning of the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='footer',
        type=PathType(exists=True, dir_okay=False, resolve_path=True),
        help="""
        Path to a file containing custom G-Code lines to be added at the
        end of the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='aerotech_include',
        hidden=True,
        is_flag=True,
        help="""
        Adds Aerotech-specific functions and variable definitions to the
        output G-Code, if applicable.
        """,
    ),
    ConfigOption(
        option_name='output_digits',
        type=IntRangeType(min=0),
        help="""
        Number of decimal places to include in G-Code coordinates and
        values.
        """,
    ),
    ConfigOption(
        option_name='lineend',
        type=TextType(),
        help="""
        Specifies the line-ending characters for the generated G-Code.
        Use 'os' to match the system default.
        """,
    ),
    ConfigOption(
        option_name='comment_char',
        type=TextType(),
        help="""
        Defines the character used to mark comments in the generated
        G-Code.
        """,
    ),

    # ------------------------------------------------------------------
    # Direct Writing to Printer (mecode)
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='direct_write_mode',
        type=DirectWriteMode,
        help="""
        Sends the generated G-Code directly to a connected machine via a
        socket or serial connection.
        """,
    ),
    ConfigOption(
        option_name='host',
        type=TextType(),
        help="""
        The hostname or IP address of the machine when using direct
        writing over a network.
        """,
    ),
    ConfigOption(
        option_name='port',
        type=IntRangeType(min=0),
        help="""
        The port number used for network communication with the machine
        when using direct writing.
        """,
    ),
    ConfigOption(
        option_name='baudrate',
        type=IntRangeType(min=0),
        help="""
        The communication speed (baud rate) for a serial connection to
        the machine when using direct writing.
        """,
    ),
    ConfigOption(
        option_name='two_way_comm',
        is_flag=True,
        help="""
        If enabled, the program will wait for a response from the machine
        after sending each G-Code command.
        """,
    ),

    # ------------------------------------------------------------------
    # Axis Naming (mecode)
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='x_axis',
        type=TextType(),
        help="""
        Custom label for the machine's X axis in the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='y_axis',
        type=TextType(),
        help="""
        Custom label for the machine's Y axis in the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='z_axis',
        type=TextType(),
        help="""
        Custom label for the machine's Z axis in the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='i_axis',
        type=TextType(),
        help="""
        Custom label for the machine's I axis in the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='j_axis',
        type=TextType(),
        help="""
        Custom label for the machine's J axis in the generated G-Code.
        """,
    ),
    ConfigOption(
        option_name='k_axis',
        type=TextType(),
        help="""
        Custom label for the machine's K axis in the generated G-Code.
        """,
    ),

    # ------------------------------------------------------------------
    # 3D Printing Settings (mecode)
    # ------------------------------------------------------------------

    ConfigOption(
        option_name='extrude',
        hidden=True,
        is_flag=True,
        help="""
        Enables extrusion mode, where filament flow is calculated and
        added to move commands.
        """,
    ),
    ConfigOption(
        option_name='filament_diameter',
        hidden=True,
        type=LengthType(),
        help="""
        Diameter of the filament used for 3D printing.
        """,
    ),
    ConfigOption(
        option_name='layer_height',
        hidden=True,
        type=LengthType(),
        help="""
        The thickness of each printed layer for 3D printing.
        """,
    ),
    ConfigOption(
        option_name='extrusion_width',
        hidden=True,
        type=LengthType(),
        help="""
        The width of the extruded filament, including any flattening
        effect.
        """,
    ),
    ConfigOption(
        option_name='extrusion_multiplier',
        hidden=True,
        type=FloatRangeType(min=0.0),
        help="""
        Adjusts the amount of filament extruded. A value greater than 1
        increases extrusion; a value less than 1 reduces it.
        """,
    ),

)
