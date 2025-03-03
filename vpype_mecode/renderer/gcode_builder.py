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

import math
from typeguard import typechecked

from vpype_mecode.enums import *
from vpype_mecode.excepts import *
from vpype_mecode.codes import gcode_table
from vpype_mecode.enums import BaseEnum
from ..mecode import GMatrix


class GBuilder(GMatrix):
    """G-code command generator for CNC machines and similar devices.

    This class extends `GMatrix` to provide high-level methods for
    generating common G-code commands used in CNC machine control. It
    handles various aspects of machine operations including:

    - Unit and plane selection
    - Tool operations and changes
    - Coolant control
    - Bed control
    - Program execution control
    - Movement commands
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._current_tool = 0
        self._current_spin_mode = SpinMode.OFF
        self._current_coolant_mode = CoolantMode.OFF
        self._is_coolant_active = False
        self._is_tool_active = False

    @property
    def is_tool_active(self) -> bool:
        """Check if tool is currently active."""
        return self._is_tool_active

    @property
    def is_coolant_active(self) -> bool:
        """Check if coolant is currently active."""
        return self._is_coolant_active

    @property
    def current_tool(self) -> int:
        """Get the current tool number."""
        return self._current_tool

    @property
    def current_spin_mode(self) -> SpinMode:
        """Get the current spin mode."""
        return self._current_spin_mode

    @property
    def current_coolant_mode(self) -> CoolantMode:
        """Get the current coolant mode."""
        return self._current_coolant_mode

    @typechecked
    def select_units(self, length_units: LengthUnits) -> None:
        """Set the unit system for subsequent commands.

        Args:
            length_units (LengthUnits): The unit system to use
        """

        statement = self._get_gcode_from_table(length_units)
        self.write(statement)

    @typechecked
    def select_plane(self, plane: Plane) -> None:
        """Select the working plane for machine operations.

        Args:
            plane (Plane): The plane to use for subsequent operations
        """

        statement = self._get_gcode_from_table(plane)
        self.write(statement)

    @typechecked
    def set_distance_mode(self, mode: DistanceMode) -> None:
        """Set the positioning mode for subsequent commands.

        Args:
            mode (DistanceMode): The distance mode to use
        """

        self.is_relative = (mode == DistanceMode.RELATIVE)
        statement = self._get_gcode_from_table(mode)
        self.write(statement)

    @typechecked
    def set_feed_mode(self, mode: FeedMode) -> None:
        """Set the feed rate mode for subsequent commands.

        Args:
            mode (FeedMode): The feed rate mode to use
        """

        statement = self._get_gcode_from_table(mode)
        self.write(statement)

    @typechecked
    def set_tool_power(self, power: float) -> None:
        """Set the power level for the current tool.

        The power parameter represents tool-specific values that vary
        by machine type, such as:

        - Spindle rotation speed in RPM
        - Laser power output (typically 0-100%)
        - Other similar power settings

        Args:
            power (float): Power level for the tool (must be >= 0.0)

        Raises:
            ValueError: If power is less than 0.0
        """

        self._validate_tool_power(power)
        self.write(f'S{power}')

    @typechecked
    def set_fan_speed(self, speed: int) -> None:
        """Set the speed of the main fan.

        Args:
            speed (int): Fan speed (must be >= 0 and <= 255)

        Raises:
            ValueError: If speed is not in the valid range
        """

        self._validate_fan_speed(speed)
        mode = FanMode.ON if speed > 0 else FanMode.OFF
        statement = self._get_gcode_from_table(mode, f'S{speed}')
        self.write(statement)

    @typechecked
    def set_bed_temperature(self, units: TemperatureUnits, temp: int) -> None:
        """Set the temperature of the bed and return immediately.

        Args:
            units (TemperatureUnits): Temperature units
            temp (float): Target temperature
        """

        statement = self._get_gcode_from_table(units, f'S{temp}')
        self.write(statement)

    @typechecked
    def sleep(self, units: TimeUnits, seconds: float) -> None:
        """Delays program execution for the specified time.

        Args:
            units (TimeUnits): Time unit specification
            seconds (float): Sleep duration (minimum 1ms)

        Raises:
            ValueError: If seconds is less than 1ms
        """

        self._validate_sleep_time(seconds)
        params = f'P{units.scale(seconds)}'
        statement = self._get_gcode_from_table(units, params)
        self.write(statement)

    @typechecked
    def tool_on(self, mode: SpinMode, power: float) -> None:
        """Activate the tool with specified direction and power.

        The power parameter represents tool-specific values that vary
        by machine type, such as:

        - Spindle rotation speed in RPM
        - Laser power output (typically 0-100%)
        - Other similar power settings

        Args:
            mode (SpinMode): Direction of tool rotation (CW/CCW)
            power (float): Power level for the tool (must be >= 0.0)

        Raises:
            ValueError: If power is less than 0.0
            ValueError: If mode is OFF or was already active
            ToolStateError: If attempting invalid mode transition
        """

        self._prevent_mode_change(mode, SpinMode.OFF)
        self._prevent_mode_change(mode, ~self._current_spin_mode)
        self._validate_tool_power(power)
        self._current_spin_mode = mode
        self._is_tool_active = True

        speed_statement = f'S{power}'
        mode_statement = self._get_gcode_from_table(mode)
        statement = f'{speed_statement} {mode_statement}'
        self.write(statement, resp_needed=True)

    def tool_off(self) -> None:
        """Deactivate the current tool."""

        self._current_spin_mode = SpinMode.OFF
        self._is_tool_active = False

        statement = self._get_gcode_from_table(SpinMode.OFF)
        self.write(statement, resp_needed=True)

    @typechecked
    def tool_change(self, mode: RackMode, number: int) -> None:
        """Execute a tool change operation.

        Performs a tool change sequence, ensuring proper safety
        conditions are met before proceeding.

        Args:
            mode (RackMode): Tool change mode to execute
            number (int): Tool number to select (must be positive)

        Raises:
            ValueError: If tool number is invalid or mode is OFF
            ToolStateError: If tool is currently active
            CoolantStateError: If coolant is currently active
        """

        self._validate_tool_number(number)
        self._prevent_mode_change(mode, RackMode.OFF)
        self._ensure_tool_is_inactive('Tool change request with tool on.')
        self._ensure_coolant_is_inactive('Tool change request with coolant on.')
        self._current_tool = number

        digits = 2 ** math.ceil(math.log2(len(str(number))))
        change_statement = self._get_gcode_from_table(mode)
        statement = f'T{number:0{digits}} {change_statement}'
        self.write(statement, resp_needed=True)

    @typechecked
    def coolant_on(self, mode: CoolantMode) -> None:
        """Activate coolant system with the specified mode.

        Args:
            mode (CoolantMode): Coolant operation mode to activate

        Raises:
            ValueError: If mode is OFF or was already active
        """

        self._prevent_mode_change(mode, CoolantMode.OFF)
        self._prevent_mode_change(mode, ~self._current_coolant_mode)
        self._current_coolant_mode = mode
        self._is_coolant_active = True

        statement = self._get_gcode_from_table(mode)
        self.write(statement, resp_needed=True)

    def coolant_off(self) -> None:
        """Deactivate coolant system."""

        self._current_coolant_mode = CoolantMode.OFF
        self._is_coolant_active = False

        statement = self._get_gcode_from_table(CoolantMode.OFF)
        self.write(statement, resp_needed=True)

    @typechecked
    def halt_program(self, mode: HaltMode, **kwargs) -> None:
        """Pause or stop program execution.

        Args:
            mode (HaltMode): Type of halt to perform
            **kwargs: Arbitrary command parameters

        Raises:
            ToolStateError: If attempting to halt with tool active
            CoolantStateError: If attempting to halt with coolant active
        """

        self._ensure_tool_is_inactive('Halt request with tool on.')
        self._ensure_coolant_is_inactive('Halt request with coolant on.')

        params = self._get_params_string_from_dict(kwargs)
        statement = self._get_gcode_from_table(mode, params)
        self.write(statement, resp_needed=True)

    @typechecked
    def emergency_halt(self, message: str) -> None:
        """Execute a safety sequence and pause execution.

        Performs an emergency shutdown sequence:

        1. Deactivates the tool
        2. Turns off coolant
        3. Adds a comment with the emergency message
        4. Halts program execution

        Args:
            message (str): Description of the emergency condition
        """

        self.tool_off()
        self.coolant_off()
        self.comment(f'Emergency halt: {message}')
        self.halt_program(HaltMode.PAUSE)

    def rapid_absolute(self, **kwargs):
        """Rapid move to absolute coordinates without transforms."""

        kwargs['rapid'] = True
        self.move_absolute(**kwargs)

    def move_absolute(self, **kwargs):
        """Move to absolute coordinates without transforms."""

        if self.is_relative: self.absolute()
        super(GMatrix, self).move(**kwargs)
        if self.is_relative: self.relative()

    @typechecked
    def comment(self, message: str) -> None:
        """Write a comment to the G-code output.

        Args:
            message (str): Text of the comment
        """

        comment = self._as_comment(message)
        self.write(comment)

    def _ensure_tool_is_inactive(self, message: str) -> None:
        """Raise an exception if tool is active."""

        if self._is_tool_active:
            raise ToolStateError(message)

    def _ensure_coolant_is_inactive(self, message: str) -> None:
        """Raise an exception if coolant is active."""

        if self._is_coolant_active:
            raise CoolantStateError(message)

    def _prevent_mode_change(self, value: BaseEnum, mode: BaseEnum) -> None:
        """Raise an exception if `value` equals `mode`"""

        if value == mode:
            message = f'Invalid mode `{mode}` for `{type(mode)}`.'
            raise ValueError(message)

    def _validate_tool_number(self, number: int) -> None:
        """Validate tool number is within acceptable range."""

        if not isinstance(number, int) or number < 1:
            message = f'Invalid tool number `{number}`.'
            raise ValueError(message)

    def _validate_tool_power(self, power: float) -> None:
        """Validate tool power level is within acceptable range."""

        if not isinstance(power, int | float) or power < 0.0:
            message = f'Invalid tool power `{power}`.'
            raise ValueError(message)

    def _validate_fan_speed(self, speed: int) -> None:
        """Validate fan speed is within acceptable range."""

        if not isinstance(speed, int) or speed < 0 or speed > 255:
            message = f'Invalid fan speed `{speed}`.'
            raise ValueError(message)

    def _validate_sleep_time(self, seconds: float) -> None:
        """Validate tool power level is within acceptable range."""

        if not isinstance(seconds, int | float) or seconds < 0.001:
            message = f'Invalid sleep time `{seconds}`.'
            raise ValueError(message)

    def _get_params_string_from_dict(self, params: dict) -> str:
        return ' '.join(f'{k}{v}' for k, v in params.items())

    def _get_gcode_from_table(self, value: BaseEnum, params: str = None) -> str:
        """Generate a G-code statement from the codes table."""

        entry = gcode_table.get_entry(value)
        comment = self._as_comment(entry.description)
        args = f' {params}' if params else ''

        return f'{entry.instruction}{args} {comment}'

    def _as_comment(self, text: str) -> None:
        """Format text as a G-code comment."""

        return self._commentify(text)
