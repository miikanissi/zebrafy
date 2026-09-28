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
import random
import unittest

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import GraphicField, ZebrafyZPL
from zebrafy.graphic_field import compress_ascii

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
        gf.format = "ascii_compressed"
        self.assertEqual(gf.format, "ASCII_COMPRESSED")
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

    def test_get_binary_byte_count(self):
        """Test _get_binary_byte_count method."""
        image = Image.new("1", (16, 4))

        # ASCII binary byte count must match graphic field count
        for format in ["ASCII", "ASCII_COMPRESSED"]:
            gf = GraphicField(image, format=format)
            self.assertEqual(gf._get_binary_byte_count(), gf._get_graphic_field_count())
            self.assertEqual(gf._get_binary_byte_count(), 8)

        # Line breaks are not counted
        gf = GraphicField(image, format="ASCII", string_line_break=3)
        self.assertEqual(gf._get_binary_byte_count(), 8)
        for format in ["B64", "Z64"]:
            gf = GraphicField(image, format=format)
            count = len(gf._get_data_string())
            self.assertEqual(gf._get_binary_byte_count(), count)
            gf.string_line_break = 3
            self.assertIn("\n", gf._get_data_string())
            self.assertEqual(gf._get_binary_byte_count(), count)

    def test_edge_cases(self):
        """Test edge cases with different image sizes and color modes."""
        small_image = Image.new("1", (1, 1))
        gf = GraphicField(small_image)
        self.assertEqual(gf._get_graphic_field_count(), 1)

        large_image = Image.new("1", (1000, 1000))
        gf = GraphicField(large_image)
        self.assertEqual(gf._get_graphic_field_count(), 125000)

    def test_non_monochrome_image(self):
        """Test images that are not black and white are converted first."""
        color_image = Image.new("RGB", (10, 10), "black")
        gf = GraphicField(color_image)
        self.assertEqual(gf._get_graphic_field_count(), 20)
        # 10 black dots and 6 white padding bits per row
        self.assertEqual(gf._get_data_string(), "FFC0" * 10)

    def test_compress_ascii(self):
        """Test ZPL ASCII compression of known rows."""
        cases = [
            # Row of zeros, repeated rows
            ("0000" * 3, 2, ",::"),
            # Row of ones
            ("FFFF", 2, "!"),
            # Trailing zeros and ones are filled
            ("8000", 2, "8,"),
            ("0FFF", 2, "0!"),
            # Runs of 3 or more use repeat counts, shorter runs do not
            ("AAAB", 2, "IAB"),
            ("AABB", 2, "AABB"),
            # 41 = h (40) + G (1)
            ("F" * 41 + "0" * 9, 25, "hGF,"),
            # Longest single run is z (400) + Y (19) = 419, longer runs are split
            ("A" * 420, 210, "zYAA"),
            ("A" * 800, 400, "zYAyGA"),
        ]
        for data, bytes_per_row, expected in cases:
            with self.subTest(data=data[:12], bytes_per_row=bytes_per_row):
                self.assertEqual(compress_ascii(data, bytes_per_row), expected)

    def test_compress_ascii_round_trip(self):
        """Test compressed ASCII graphic fields decode to the original image."""
        rng = random.Random(1)
        for width, height in [(1, 1), (8, 3), (13, 7), (64, 40), (203, 50)]:
            image = Image.new("1", (width, height), 255)
            # Mix of runs, noise, repeated rows, and empty rows
            for y in range(height):
                if y % 5 == 1:
                    continue
                for x in range(width):
                    if (x // 7 + y // 3) % 3 == 0 or rng.random() < 0.05:
                        image.putpixel((x, y), 0)
            with self.subTest(size=(width, height)):
                gf = GraphicField(image, format="ASCII_COMPRESSED")
                decoded = ZebrafyZPL(gf.get_graphic_field()).to_images()[0]
                self.assertEqual(
                    decoded.crop((0, 0, width, height)).tobytes(), image.tobytes()
                )


if __name__ == "__main__":
    unittest.main()
