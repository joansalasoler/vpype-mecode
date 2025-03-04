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

from abc import ABC, abstractmethod
from vpype_mecode.renderer.gcode_context import GContext


class BaseTool(ABC):
    """Base class for tool implementations.

    This abstract base class defines the interface for controlling
    various machine tools like lasers, spindles, or other end effectors.
    It handles tool initialization, power control, and shutdown.

    Different tools may have different activation patterns:

    - A spindle tool may start rotating during activation, but power
      on/off won't affect its state
    - A laser tool may initialize at zero power during activation, and
      power on/off will control the beam intensity
    - A pen tool might not need activation or power on/off
    """

    @abstractmethod
    def activate(self, ctx: GContext):
        """Prepare the tool for operation.

        Generates G-code commands to initialize and prepare the tool
        before its use. This might include setting up tool-specific
        parameters (spindle speed, initial power, etc) and waiting for
        the tool to warm up.

        Args:
            ctx (GContext): The G-code generation context
        """

    @abstractmethod
    def power_on(self, ctx: GContext):
        """Set the tool to its active working state.

        Generates G-code commands to set the tool to its working
        configuration. This might include setting the beam intensity,
        lowering the pen, etc.

        Args:
            ctx (GContext): The G-code generation context
        """

    @abstractmethod
    def power_off(self, ctx: GContext):
        """Set the tool to its inactive state.

        Generates G-code commands to set the tool to its non-working
        state while keeping the system active. The behavior varies by
        tool type.

        Args:
            ctx (GContext): The G-code generation context
        """

    @abstractmethod
    def deactivate(self, ctx: GContext):
        """Perform tool shutdown operations.

        Generates G-code commands to completely shut down the tool
        system. For exemple, this might include stopping a spindle or
        turning off a laser.

        Args:
            ctx (GContext): The G-code generation context
        """
