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

from typing import Tuple, Type
from typeguard import typechecked
from vpype_mecode.enums import BaseEnum

from .gcode_entry import GCodeEntry


class GCodeTable:
    """Mapping table for G-Code instructions.

    This class maintains a collection of GCodeEntry objects, providing
    a way to store and retrieve G-Code instructions and their descriptions
    based on our internal enum representations. Each entry is uniquely
    identified by a combination of its enum type and value.
    """

    @typechecked
    def __init__(self, values: Tuple[GCodeEntry, ...]):
        """Initialize a new `GCodeTable` with the given entries.

        Args:
            values: A tuple of `GCodeEntry` objects
        """

        self._entries = {}
        self._init_entries(values)

    @typechecked
    def get_entry(self, enum: BaseEnum) -> GCodeEntry:
        """Retrieve the entry for the given enum.

        Args:
            enum: The BaseEnum value to look up.

        Returns:
            GCodeEntry: The corresponding entry from the table.

        Raises:
            KeyError: If no entry exists for the given enum.
        """

        key = self._key_for(enum)
        return self._entries[key]

    @typechecked
    def add_entry(self, entry: GCodeEntry) -> None:
        """Add a new entry to the table.

        Args:
            entry: The GCodeEntry to add to the table.

        Raises:
            KeyError: If an entry for the given enum already
                      exists in the table.
        """

        key = self._key_for(entry.enum)

        if key in self._entries:
            raise KeyError(f'Key {entry.enum} already in the table.')

        self._entries[key] = entry

    def _key_for(self, enum: BaseEnum) -> Tuple[Type, BaseEnum]:
        """Generate a unique key for table lookup based on the enum."""

        return (type(enum), enum)

    def _init_entries(self, values: Tuple[GCodeEntry, ...]) -> None:
        """Initialize the entries dictionary with the provided values."""

        for entry in values:
            self.add_entry(entry)

    def _to_rst(self) -> str:
        """Returns the entries as an RST-formatted table."""

        table = [
            '.. list-table::',
            '   :header-rows: 1',
            '   :widths: auto',
            '',
            '   * - Enum',
            '     - Value',
            '     - Code',
            '     - Description'
        ]

        for entry in self._entries.values():
            modules = entry.enum.__module__.split('.')
            module = '.'.join(modules[:-1])

            table.append(f'   * - :obj:`{module}.{entry.enum}`')
            table.append(f'     - {entry.enum.value}')
            table.append(f'     - {entry.instruction}')
            table.append(f'     - {entry.description}')

        return '\n'.join(table)
