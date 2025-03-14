#! /usr/bin/env python

import os.path
import unittest
from tempfile import TemporaryFile
import sys
from os.path import abspath, dirname


HERE = dirname(abspath(__file__))

try:
    from mecode import G, is_str, decode2To3
except:
    sys.path.append(abspath(os.path.join(HERE, "..", "..")))
    from mecode import G, is_str, decode2To3


class TestGFixture(unittest.TestCase):
    def getGClass(self):
        return G

    def setUp(self):
        self.outfile = TemporaryFile("w+")
        self.g = self.getGClass()(
            output=self.outfile, print_lines=False, aerotech_include=False
        )
        self.expected = ""
        if self.g.is_relative:
            self.expect_cmd("G91 ; relative")
        else:
            self.expect_cmd("G90 ; absolute")

    def tearDown(self):
        self.g.teardown()
        self.outfile.close()
        del self.outfile
        del self.g

    # helper functions  #######################################################

    def expect_cmd(self, cmd):
        self.expected = self.expected + cmd + "\n"

    def assert_output(self):
        string_rep = ""
        if is_str(self.expected):
            string_rep = self.expected
            self.expected = self.expected.split("\n")
        self.expected = [x.strip() for x in self.expected if x.strip()]
        self.outfile.seek(0)
        lines = self.outfile.readlines()
        if "b" in self.outfile.mode:
            lines = [decode2To3(x) for x in lines]
        lines = [x.strip() for x in lines if x.strip()]
        self.assertListEqual(lines, self.expected)
        self.expected = string_rep

    def assert_almost_position(self, expected_pos):
        for k, v in expected_pos.items():
            self.assertAlmostEqual(self.g.current_position[k], v)

    def assert_position(self, expected_pos):
        self.assertEqual(self.g.current_position, expected_pos)


class TestG(TestGFixture):
    def test_init(self):
        self.assertEqual(self.g.is_relative, True)

    def test_set_axis_position(self):
        g = self.g
        g.set_axis_position()
        self.expect_cmd("G92 ; Set axis position")
        self.assert_output()
        g.set_axis_position(x=10, y=20, A=5)
        self.expect_cmd("G92 X10 Y20 A5 ; Set axis position")
        self.assert_output()
        self.assert_position({"A": 5.0, "x": 10.0, "y": 20.0, "z": 0})
        g.set_axis_position(y=0)
        self.assert_position({"A": 5.0, "x": 10.0, "y": 0.0, "z": 0})

    def test_relative(self):
        self.assertEqual(self.g.is_relative, True)
        self.g._absolute()
        self.expect_cmd("G90 ; absolute")
        self.g._relative()
        self.assertEqual(self.g.is_relative, True)
        self.expect_cmd("G91 ; relative")
        self.assert_output()
        self.g._relative()
        self.assertEqual(self.g.is_relative, True)
        self.assert_output()

    def test_absolute(self):
        self.g._absolute()
        self.assertEqual(self.g.is_relative, False)
        self.expect_cmd("G90 ; absolute")
        self.assert_output()
        self.g._absolute()
        self.assertEqual(self.g.is_relative, False)
        self.assert_output()

    def test_feed(self):
        self.g._feed(10)
        self.expect_cmd("G1 F10")
        self.assert_output()

    def test_dwell(self):
        self.g._dwell(10)
        self.expect_cmd("G4 P10")
        self.assert_output()

    def test_setup(self):
        self.outfile.close()
        self.outfile = TemporaryFile()
        self.g = G(output=self.outfile, print_lines=False, aerotech_include=True)
        self.expected = ""
        with open(os.path.join(HERE, "../header.txt")) as f:
            lines = f.read()
        self.expect_cmd(lines)
        self.expect_cmd("G91 ; relative")
        self.assert_output()

    def test_move(self):
        self.g.move(10, 10)
        self.assert_position({"x": 10.0, "y": 10.0, "z": 0})
        self.g.move(10, 10, A=50)
        self.assert_position({"x": 20.0, "y": 20.0, "A": 50, "z": 0})
        self.g.move(10, 10, 10)
        self.assert_position({"x": 30.0, "y": 30.0, "A": 50, "z": 10})
        self.expect_cmd("""
        G1 X10 Y10
        G1 X10 Y10 A50
        G1 X10 Y10 Z10
        """)
        self.assert_output()

        self.g._abs_move(20, 20, 0)
        self.expect_cmd("""
        G90 ; absolute
        G1 X20 Y20 Z0
        G91 ; relative
        """)
        self.assert_output()

        # test extrusion in absolute movement
        self.g.extrude = True
        self.g.layer_height = 0.22
        self.g.extrusion_width = 0.4
        self.g.filament_diameter = 1.75
        self.g.extrusion_multiplier = 1
        self.g._abs_move(x=30, y=30)
        self.assert_position(
            {"x": 30.0, "y": 30.0, "z": 0.0, "A": 50.0, "E": 0.45635101227893116}
        )
        self.expect_cmd("""
        G90 ; absolute
        G1 X30 Y30 E0.45635
        G91 ; relative
        """)

        self.assert_output()

        self.g.move(x=10)
        self.assert_position(
            {"x": 40.0, "y": 30.0, "A": 50, "z": 0, "E": 0.7790399076627088}
        )
        self.expect_cmd("""
        G1 X10 E0.32269
        """)
        self.assert_output()

        self.g.extrusion_multiplier = 2
        self.g.move(y=10)
        self.assert_position(
            {"x": 40.0, "y": 40.0, "A": 50, "z": 0, "E": 1.4244176984302641}
        )
        self.expect_cmd("""
        G1 Y10 E0.64538
        """)
        self.assert_output()

        self.g.move(Z=10)
        self.assert_position(
            {"x": 40.0, "y": 40.0, "A": 50, "Z": 10, "z": 0.0, "E": 1.4244176984302641}
        )
        self.expect_cmd("""
        G1 E0 Z10
        """)
        self.assert_output()

        self.g._abs_move(Z=20)
        self.assert_position(
            {"x": 40.0, "y": 40.0, "Z": 20, "A": 50, "z": 0.0, "E": 1.4244176984302641}
        )
        self.expect_cmd("""
        G90 ; absolute
        G1 E1.42442 Z20
        G91 ; relative
        """)
        self.assert_output()

    def test_abs_move(self):
        self.g._relative()
        self.g._abs_move(10, 10)
        self.expect_cmd("""
        G90 ; absolute
        G1 X10 Y10
        G91 ; relative
        """)
        self.assert_output()
        self.assert_position({"x": 10, "y": 10, "z": 0})

        self.g._abs_move(5, 5, 5)
        self.expect_cmd("""
        G90 ; absolute
        G1 X5 Y5 Z5
        G91 ; relative
        """)
        self.assert_output()
        self.assert_position({"x": 5, "y": 5, "z": 5})

        self.g._abs_move(15, 0, D=5)
        self.expect_cmd("""
        G90 ; absolute
        G1 X15 Y0 D5
        G91 ; relative
        """)
        self.assert_output()
        self.assert_position({"x": 15, "y": 0, "D": 5, "z": 5})

        self.g._absolute()
        self.g._abs_move(19, 18, D=6)
        self.expect_cmd("""
        G90 ; absolute
        G1 X19 Y18 D6
        """)
        self.assert_output()
        self.assert_position({"x": 19, "y": 18, "D": 6, "z": 5})
        self.g._relative()

    def test_rapid(self):
        self.g.rapid(10, 10)
        self.assert_position({"x": 10.0, "y": 10.0, "z": 0})
        self.g.rapid(10, 10, A=50)
        self.assert_position({"x": 20.0, "y": 20.0, "A": 50, "z": 0})
        self.g.rapid(10, 10, 10)
        self.assert_position({"x": 30.0, "y": 30.0, "A": 50, "z": 10})
        self.expect_cmd("""
        G0 X10 Y10
        G0 X10 Y10 A50
        G0 X10 Y10 Z10
        """)
        self.assert_output()

    def test_arc(self):
        with self.assertRaises(RuntimeError):
            self.g.arc()

        self.g.arc(x=10, y=0, linearize=False)
        self.expect_cmd("""
        G17 ; XY plane
        G2 X10 Y0 R5
        """)
        self.assert_output()
        self.assert_position({"x": 10, "y": 0, "z": 0})

        self.g.arc(x=5, A=0, direction="CCW", radius=5, linearize=False)
        self.expect_cmd("""
        G16 X Y A ; coordinate axis assignment
        G18 ; XZ plane
        G3 X5 A0 R5
        """)
        self.assert_output()
        self.assert_position({"x": 15, "y": 0, "A": 0, "z": 0})

        self.g.arc(x=0, y=10, helix_dim="D", helix_len=10, linearize=False)
        self.expect_cmd("""
        G16 X Y D ; coordinate axis assignment
        G17 ; XY plane
        G2 X0 Y10 R5 G1 D10
        """)
        self.assert_output()
        self.assert_position({"x": 15, "y": 10, "A": 0, "D": 10, "z": 0})

        self.g.arc(0, 10, helix_dim="D", helix_len=10, linearize=False)
        self.expect_cmd("""
        G16 X Y D ; coordinate axis assignment
        G17 ; XY plane
        G2 X0 Y10 R5 G1 D10
        """)
        self.assert_output()
        self.assert_position({"x": 15, "y": 20, "A": 0, "D": 20, "z": 0})

        with self.assertRaises(RuntimeError):
            self.g.arc(x=10, y=10, radius=1, linearize=False)

    def test_rect(self):
        self.g.rect(10, 5)
        self.expect_cmd("""
        G1 Y5
        G1 X10
        G1 Y-5
        G1 X-10
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="UL")
        self.expect_cmd("""
        G1 X10
        G1 Y-5
        G1 X-10
        G1 Y5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="UR")
        self.expect_cmd("""
        G1 Y-5
        G1 X-10
        G1 Y5
        G1 X10
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="LR")
        self.expect_cmd("""
        G1 X-10
        G1 Y5
        G1 X10
        G1 Y-5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="LL", direction="CCW")
        self.expect_cmd("""
        G1 X10
        G1 Y5
        G1 X-10
        G1 Y-5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="UL", direction="CCW")
        self.expect_cmd("""
        G1 Y-5
        G1 X10
        G1 Y5
        G1 X-10
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="UR", direction="CCW")
        self.expect_cmd("""
        G1 X-10
        G1 Y-5
        G1 X10
        G1 Y5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

        self.g.rect(10, 5, start="LR", direction="CCW")
        self.expect_cmd("""
        G1 Y5
        G1 X-10
        G1 Y-5
        G1 X10
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 0})

    def test_meander(self):
        self.g.meander(2, 2, 1)
        self.expect_cmd("""
        G1 X2
        G1 Y1
        G1 X-2
        G1 Y1
        G1 X2
        """)
        self.assert_output()
        self.assert_position({"x": 2, "y": 2, "z": 0})

        self.g.meander(2, 2, 1.1)
        self.expect_cmd("""
        ; WARNING! meander spacing updated from 1.1 to 1.0
        G1 X2
        G1 Y1
        G1 X-2
        G1 Y1
        G1 X2
        """)
        self.assert_output()
        self.assert_position({"x": 4, "y": 4, "z": 0})

        self.g.meander(2, 2, 1, start="UL")
        self.expect_cmd("""
        G1 X2
        G1 Y-1
        G1 X-2
        G1 Y-1
        G1 X2
        """)
        self.assert_output()
        self.assert_position({"x": 6, "y": 2, "z": 0})

        self.g.meander(2, 2, 1, start="UR")
        self.expect_cmd("""
        G1 X-2
        G1 Y-1
        G1 X2
        G1 Y-1
        G1 X-2
        """)
        self.assert_output()
        self.assert_position({"x": 4, "y": 0, "z": 0})

        self.g.meander(2, 2, 1, start="LR")
        self.expect_cmd("""
        G1 X-2
        G1 Y1
        G1 X2
        G1 Y1
        G1 X-2
        """)
        self.assert_output()
        self.assert_position({"x": 2, "y": 2, "z": 0})

        self.g.meander(2, 2, 1, start="LR", orientation="y")
        self.expect_cmd("""
        G1 Y2
        G1 X-1
        G1 Y-2
        G1 X-1
        G1 Y2
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 4, "z": 0})

        # test we return to absolute
        self.g._absolute()
        self.g.meander(3, 2, 1, start="LR", orientation="y")
        self.expect_cmd("""
        G90 ; absolute
        G91 ; relative
        G1 Y2
        G1 X-1
        G1 Y-2
        G1 X-1
        G1 Y2
        G1 X-1
        G1 Y-2
        G90 ; absolute
        """)
        self.assert_output()
        self.assert_position({"x": -3, "y": 4, "z": 0})

    def test_clip(self):
        self.g.clip()
        self.expect_cmd("""
        G16 X Y Z ; coordinate axis assignment
        G18 ; XZ plane
        G3 X0 Z4 R2
        """)
        self.assert_output()
        self.assert_position({"y": 0, "x": 0, "z": 4})

        self.g.clip(axis="A", direction="-y", height=10)
        self.expect_cmd("""
        G16 X Y A ; coordinate axis assignment
        G19 ; YZ plane
        G2 Y0 A10 R5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 4, "A": 10})

        self.g.clip(axis="A", direction="-y", height=-10)
        self.expect_cmd("""
        G16 X Y A ; coordinate axis assignment
        G19 ; YZ plane
        G3 Y0 A-10 R5
        """)
        self.assert_output()
        self.assert_position({"x": 0, "y": 0, "z": 4, "A": 0})

    def test_toggle_pressure(self):
        self.g.toggle_pressure(0)
        self.expect_cmd("Call togglePress P0")
        self.assert_output()

    def test_set_pressure(self):
        self.g.set_pressure(0, 10)
        self.expect_cmd("Call setPress P0 Q10")
        self.assert_output()

    def test_set_valve(self):
        self.g.set_valve(0, 1)
        self.expect_cmd("$DO0.0=1")
        self.assert_output()

    def test_rename_axis(self):
        self.g.rename_axis(z="A")
        self.g.move(10, 10, 10)
        self.assert_position({"x": 10.0, "y": 10.0, "A": 10, "z": 10})
        self.expect_cmd("""
        G1 X10 Y10 A10
        """)
        self.assert_output()

        self.g.rename_axis(z="B")
        self.g.move(10, 10, 10)
        self.assert_position({"x": 20.0, "y": 20.0, "z": 20, "A": 10, "B": 10})
        self.expect_cmd("""
        G1 X10 Y10 B10
        """)
        self.assert_output()

        self.g.rename_axis(x="W")
        self.g.move(10, 10, 10)
        self.assert_position({"x": 30.0, "y": 30.0, "z": 30, "A": 10, "B": 20, "W": 10})
        self.expect_cmd("""
        G1 W10 Y10 B10
        """)
        self.assert_output()

        self.g.rename_axis(x="X")
        self.g.arc(x=10, z=10, linearize=False)
        self.assert_position({"x": 40.0, "y": 30.0, "z": 40, "A": 10, "B": 30, "W": 10})
        self.expect_cmd("""
        G16 X Y B ; coordinate axis assignment
        G18 ; XZ plane
        G2 X10 B10 R7.07107
        """)
        self.assert_output()

        self.g.meander(10, 10, 10)
        self.expect_cmd("""
        G1 X10
        G1 Y10
        G1 X-10
        """)
        self.assert_output()

    def test_meander_helpers(self):
        self.assertEqual(self.g._meander_spacing(12, 1.5), 1.5)
        self.assertEqual(self.g._meander_spacing(10, 2.2), 2)
        self.assertEqual(self.g._meander_passes(11, 1.5), 8)
        self.assertEqual(self.g._meander_spacing(1, 0.11), 0.1)

    def test_triangular_wave(self):
        self.g.triangular_wave(2, 2, 1)
        self.expect_cmd("""
        G1 X2 Y2
        G1 X2 Y-2
        """)
        self.assert_output()
        self.assert_position({"x": 4, "y": 0, "z": 0})

        self.g.triangular_wave(1, 2, 2.5, orientation="y")
        self.expect_cmd("""
        G1 X1 Y2
        G1 X-1 Y2
        G1 X1 Y2
        G1 X-1 Y2
        G1 X1 Y2
        """)
        self.assert_output()
        self.assert_position({"x": 5, "y": 10, "z": 0})

        self.g.triangular_wave(2, 2, 1.5, start="UL")
        self.expect_cmd("""
        G1 X-2 Y2
        G1 X-2 Y-2
        G1 X-2 Y2
        """)
        self.assert_output()
        self.assert_position({"x": -1, "y": 12, "z": 0})

        self.g.triangular_wave(2, 2, 1, start="LR")
        self.expect_cmd("""
        G1 X2 Y-2
        G1 X2 Y2
        """)
        self.assert_output()
        self.assert_position({"x": 3, "y": 12, "z": 0})

        self.g.triangular_wave(2, 2, 1, start="LR", orientation="y")
        self.expect_cmd("""
        G1 X2 Y-2
        G1 X-2 Y-2
        """)
        self.assert_output()
        self.assert_position({"x": 3, "y": 8, "z": 0})

        # test we return to absolute
        self.g._absolute()
        self.g.triangular_wave(3, 2, 1, start="LR", orientation="y")
        self.expect_cmd("""
        G90 ; absolute
        G91 ; relative
        G1 X3 Y-2
        G1 X-3 Y-2
        G90 ; absolute
        """)
        self.assert_output()
        self.assert_position({"x": 3, "y": 4, "z": 0})

    def test_output_digits(self):
        self.g.output_digits = 1
        self.g.move(10)
        self.expect_cmd("""
        G1 X10
        """)
        self.assert_output()
        self.g.output_digits = 6
        self.g.move(10)
        self.expect_cmd("""
        G1 X10
        """)
        self.assert_output()

    def test_open_in_binary(self):
        outfile = TemporaryFile("wb+")
        g = self.getGClass()(output=outfile, print_lines=False)
        g.move(10, 10)
        outfile.seek(0)
        lines = outfile.readlines()
        assert type(lines[0]) == bytes
        outfile.close()


if __name__ == "__main__":
    unittest.main()
