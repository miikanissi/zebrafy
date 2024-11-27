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
from PIL import Image

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

    def test_get_graphic_field(self):
        """Test get_graphic_field method."""
        gf = GraphicField(self.test_image)
        zpl_string = gf.get_graphic_field()
        self.assertTrue(zpl_string.startswith("^GFA"))

    def test_get_data_string(self):
        """Test _get_data_string method."""
        gf = GraphicField(self.test_image, format="ASCII")
        data_string = gf._get_data_string()
        self.assertIsInstance(data_string, str)

        gf = GraphicField(self.test_image, format="B64")
        data_string = gf._get_data_string()
        self.assertTrue(data_string.startswith(":B64:"))

        gf = GraphicField(self.test_image, format="Z64")
        data_string = gf._get_data_string()
        self.assertTrue(data_string.startswith(":Z64:"))

    def test_edge_cases(self):
        """Test edge cases with different image sizes and color modes."""
        small_image = Image.new("1", (1, 1))
        gf = GraphicField(small_image)
        self.assertEqual(gf._get_graphic_field_count(), 1)

        large_image = Image.new("1", (1000, 1000))
        gf = GraphicField(large_image)
        self.assertEqual(gf._get_graphic_field_count(), 125000)

        color_image = Image.new("RGB", (10, 10))
        gf = GraphicField(color_image)
        self.assertEqual(gf._get_graphic_field_count(), 20)


if __name__ == "__main__":
    unittest.main()
