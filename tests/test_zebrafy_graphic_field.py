########################################################################################
#
#    Author: Miika Nissi
#    Copyright 2023-2023 Miika Nissi (https://miikanissi.com)
#
#    This file is part of zebrafy
#    (see https://github.com/miikanissi/zebrafy).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################################

# 1. Standard library imports:
import unittest

# 2. Known third party imports:
# 3. Local imports in the relative form:
from zebrafy import GraphicField

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyGraphicField(TestZebrafyCommonBase):
    """Test ZebrafyGraphicField."""

    def test_graphic_field_image(self):
        """Test GraphicField image input."""
        with self.assertRaises(ValueError):
            GraphicField(None)
        with self.assertRaises(TypeError):
            GraphicField(123)

    def test_graphic_field_format(self):
        """Test GraphicField format input."""
        gf = GraphicField(self.test_image)
        self.assertEqual(gf.format, "ASCII")
        with self.assertRaises(ValueError):
            gf.format = None
        with self.assertRaises(TypeError):
            gf.format = 123
        with self.assertRaises(ValueError):
            gf.format = "D"

    def test_graphic_field_string_line_break(self):
        """Test GraphicField string_line_break input."""
        gf = GraphicField(self.test_image)
        self.assertIsNone(gf.string_line_break)
        with self.assertRaises(TypeError):
            gf.string_line_break = "123"
        with self.assertRaises(ValueError):
            gf.string_line_break = -20

    def test_graphic_field_deprecated_compression_type(self):
        """Test deprecated GraphicField compression_type input."""
        gfa = GraphicField(self.test_image, compression_type="A")
        self.assertEqual(gfa.format, "ASCII")
        gfb = GraphicField(self.test_image, compression_type="B")
        self.assertEqual(gfb.format, "B64")
        gfc = GraphicField(self.test_image, compression_type="C")
        self.assertEqual(gfc.format, "Z64")


if __name__ == "__main__":
    unittest.main()
