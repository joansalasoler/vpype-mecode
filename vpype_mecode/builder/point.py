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

from typing import NamedTuple
import numpy as np

from .move_params import MoveParams


class Point(NamedTuple):
    """A point in a 3D space."""

    x: float | None = None
    y: float | None = None
    z: float | None = None

    @classmethod
    def unknown(cls) -> 'Point':
        """Create a point with unknown coordinates"""
        return cls(None, None, None)

    @classmethod
    def zero(cls) -> 'Point':
        """Create a point at origin (0, 0, 0)"""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> 'Point':
        """Create a Point from a 4D vector"""
        return cls.create(*vector[:3])

    def to_vector(self) -> np.ndarray:
        """Convert point to a 4D vector"""
        return np.array([self.x or 0, self.y or 0, self.z or 0, 1.0])

    @classmethod
    def from_params(cls, params: MoveParams) -> 'Point':
        """Create a point from a dictionary of move parameters."""

        x = params.get('X', None)
        y = params.get('Y', None)
        z = params.get('Z', None)

        return cls(x, y, z)

    @classmethod
    def create(cls,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None) -> 'Point':
        """Create a point converting `None` values to zero.

        Args:
            x: X coordinate, defaults to 0 if `None`
            y: Y coordinate, defaults to 0 if `None`
            z: Z coordinate, defaults to 0 if `None`
        """

        return cls(x or 0, y or 0, z or 0)

    def replace(self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None) -> 'Point':
        """Create a new point replacing only the specified coordinates.

        Args:
            x: New X position or `None` to keep the current
            y: New Y position or `None` to keep the current
            z: New Z position or `None` to keep the current

        Returns:
            A new point with the specified coordinates.
        """

        return Point(
            self.x if x is None else x,
            self.y if y is None else y,
            self.z if z is None else z
        )

    def resolve(self) -> 'Point':
        """Create a new point replacing None values with zeros."""

        return Point(
            0 if self.x is None else self.x,
            0 if self.y is None else self.y,
            0 if self.z is None else self.z
        )

    def combine(self, o: 'Point', t: 'Point', m: 'Point') -> 'Point':
        """Update coordinates based on position changes.

        Updates coordinates by comparing the current, reference, and
        target points. Individual coordinates are updated to the values
        from point 'm' following these rules:

        - If the current coordinate is not `None`.
        - If current is `None` but reference and target differ.

        Args:
            o: The reference position
            t: The target point to update towards
            m: Values to use when updating

        Returns:
            A new point with the coordinates combined
        """

        x = m.x if self.x is not None or o.x != t.x else None
        y = m.y if self.y is not None or o.y != t.y else None
        z = m.z if self.z is not None or o.z != t.z else None

        return Point(x, y, z)

    def __add__(self, other: 'Point') -> 'Point':
        """Add two points.

        Args:
            other: Point to add to this point

        Returns:
            A new point with the coordinates added
        """

        return Point(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other: 'Point') -> 'Point':
        """Subtract two points.

        Args:
            other: Point to subtract from this point

        Returns:
            A new point with the coordinates substracted
        """

        return Point(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )
