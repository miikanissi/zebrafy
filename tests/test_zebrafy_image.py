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
from zebrafy import ZebrafyImage

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyImage(TestZebrafyCommonBase):
    """Test ZebrafyImage."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        cls.static_test_image = cls._read_static_file("test_image.png")

    def test_zebrafy_image_image(self):
        """Test ZebrafyImage image input."""
        with self.assertRaises(ValueError):
            ZebrafyImage(None)
        with self.assertRaises(TypeError):
            ZebrafyImage(123)

    def test_zebrafy_image_format(self):
        """Test ZebrafyImage format input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.format, "ASCII")
        with self.assertRaises(ValueError):
            zebrafy_image.format = None
        with self.assertRaises(TypeError):
            zebrafy_image.format = 123
        with self.assertRaises(ValueError):
            zebrafy_image.format = "D"

    def test_zebrafy_image_deprecated_compression_type(self):
        """Test deprecated ZebrafyImage compression_type input."""
        gfa = ZebrafyImage(self.test_image, compression_type="A")
        self.assertEqual(gfa.format, "ASCII")
        gfb = ZebrafyImage(self.test_image, compression_type="B")
        self.assertEqual(gfb.format, "B64")
        gfc = ZebrafyImage(self.test_image, compression_type="C")
        self.assertEqual(gfc.format, "Z64")

    def test_zebrafy_image_invert(self):
        """Test ZebrafyImage invert input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertFalse(zebrafy_image.invert)
        with self.assertRaises(ValueError):
            zebrafy_image.invert = None
        with self.assertRaises(TypeError):
            zebrafy_image.invert = "123"

    def test_zebrafy_image_dither(self):
        """Test ZebrafyImage dither input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertTrue(zebrafy_image.dither)
        with self.assertRaises(ValueError):
            zebrafy_image.dither = None
        with self.assertRaises(TypeError):
            zebrafy_image.dither = "123"

    def test_zebrafy_image_threshold(self):
        """Test ZebrafyImage threshold input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.threshold, 128)
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = None
        with self.assertRaises(TypeError):
            zebrafy_image.threshold = "123"
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = -1
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = 256

    def test_zebrafy_image_width(self):
        """Test ZebrafyImage width input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.width, 0)
        with self.assertRaises(ValueError):
            zebrafy_image.width = None
        with self.assertRaises(TypeError):
            zebrafy_image.width = "123"

    def test_zebrafy_image_height(self):
        """Test ZebrafyImage height input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.height, 0)
        with self.assertRaises(ValueError):
            zebrafy_image.height = None
        with self.assertRaises(TypeError):
            zebrafy_image.height = "123"

    def test_zebrafy_image_pos_x(self):
        """Test ZebrafyImage pos_x input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.pos_x, 0)
        with self.assertRaises(ValueError):
            zebrafy_image.pos_x = None
        with self.assertRaises(TypeError):
            zebrafy_image.pos_x = "123"

    def test_zebrafy_image_pos_y(self):
        """Test ZebrafyImage pos_y input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.pos_y, 0)
        with self.assertRaises(ValueError):
            zebrafy_image.pos_y = None
        with self.assertRaises(TypeError):
            zebrafy_image.pos_y = "123"

    def test_zebrafy_image_rotation(self):
        """Test ZebrafyImage rotation input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertEqual(zebrafy_image.rotation, 0)
        with self.assertRaises(ValueError):
            zebrafy_image.rotation = None
        with self.assertRaises(TypeError):
            zebrafy_image.rotation = "123"
        with self.assertRaises(TypeError):
            zebrafy_image.rotation = 90.0
        with self.assertRaises(ValueError):
            zebrafy_image.rotation = 45

    def test_zebrafy_image_complete_zpl(self):
        """Test ZebrafyImage complete_zpl input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertTrue(zebrafy_image.complete_zpl)
        with self.assertRaises(ValueError):
            zebrafy_image.complete_zpl = None
        with self.assertRaises(TypeError):
            zebrafy_image.complete_zpl = "123"

    def test_zebrafy_image_string_line_break(self):
        """Test ZebrafyImage string_line_break input."""
        zebrafy_image = ZebrafyImage(self.test_image)
        self.assertIsNone(zebrafy_image.string_line_break)
        with self.assertRaises(TypeError):
            zebrafy_image.string_line_break = "123"
        with self.assertRaises(ValueError):
            zebrafy_image.string_line_break = -20

    # Output validation
    def test_image_to_default_zpl(self):
        """Test image to ZPL with default options."""
        default_zpl = ZebrafyImage(self.static_test_image).to_zpl()
        self.assertEqual(default_zpl, self._read_static_file("test_image_ascii.zpl"))

    def test_image_to_ascii_zpl(self):
        """Test image to ZPL with A (ASCII) compression."""
        ascii_zpl = ZebrafyImage(self.static_test_image, format="ASCII").to_zpl()
        self.assertEqual(ascii_zpl, self._read_static_file("test_image_ascii.zpl"))

    def test_image_to_b64_zpl(self):
        """Test image to ZPL with B (B64 Binary) compression."""
        b64_zpl = ZebrafyImage(self.static_test_image, format="B64").to_zpl()
        self.assertEqual(b64_zpl, self._read_static_file("test_image_b64.zpl"))

    def test_image_to_z64_zpl(self):
        """Test image to ZPL with C (Z64 Binary) compression."""
        z64_zpl = ZebrafyImage(self.static_test_image, format="Z64").to_zpl()
        self.assertEqual(z64_zpl, self._read_static_file("test_image_z64.zpl"))

    def test_image_to_zpl_invert(self):
        """Test image to ZPL inverting the image."""
        gf_zpl = ZebrafyImage(self.static_test_image, invert=True).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_invert.zpl"))

    def test_image_to_zpl_invert_no_dither(self):
        """Test image to ZPL without dithering and inverting the image."""
        gf_zpl = ZebrafyImage(
            self.static_test_image, dither=False, invert=True
        ).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_image_invert_no_dither.zpl")
        )

    def test_image_to_zpl_no_dither(self):
        """Test image to ZPL without dithering the image."""
        gf_zpl = ZebrafyImage(self.static_test_image, dither=False).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_no_dither.zpl"))

    def test_image_to_zpl_threshold_low(self):
        """Test image to ZPL without dithering the image and low threshold."""
        gf_zpl = ZebrafyImage(
            self.static_test_image, dither=False, threshold=40
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_low_threshold.zpl"))

    def test_image_to_zpl_threshold_high(self):
        """Test image to ZPL without dithering the image and high threshold."""
        gf_zpl = ZebrafyImage(
            self.static_test_image, dither=False, threshold=215
        ).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_image_high_threshold.zpl")
        )

    def test_image_to_zpl_width_height(self):
        """Test image to ZPL with width and height."""
        gf_zpl = ZebrafyImage(self.static_test_image, width=500, height=500).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_width_height.zpl"))

    def test_image_to_zpl_pos_x_pos_y(self):
        """Test image to ZPL with pos_x and pos_y."""
        gf_zpl = ZebrafyImage(self.static_test_image, pos_x=100, pos_y=200).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_pos_x_pos_y.zpl"))

    def test_image_to_zpl_rotation(self):
        """Test image to ZPL with rotation."""
        gf_zpl = ZebrafyImage(self.static_test_image, rotation=90).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_rotation.zpl"))

    def test_image_to_zpl_string_line_break(self):
        """Test image to ZPL with string_line_break."""
        gf_zpl = ZebrafyImage(self.static_test_image, string_line_break=80).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_image_string_line_break.zpl")
        )

    def test_multiple_image_to_zpl(self):
        """Test multiple images to ZPL with default options."""
        gf_zpl = ZebrafyImage(
            self.static_test_image,
            complete_zpl=False,
        ).to_zpl()
        complete_zpl = "^XA\n" + gf_zpl + "\n" + gf_zpl + "\n^XZ\n"
        self.assertEqual(
            complete_zpl, self._read_static_file("test_image_multiple.zpl")
        )

    def test_zebrafy_image_jpeg(self):
        """Test ZebrafyImage with a JPEG image."""
        jpeg_image = self._read_static_file("test_image.jpg")
        zebrafy_image = ZebrafyImage(jpeg_image)
        self.assertEqual(zebrafy_image.format, "ASCII")

    def test_zebrafy_image_boundary_threshold(self):
        """Test ZebrafyImage with boundary threshold values."""
        zebrafy_image = ZebrafyImage(self.test_image)
        zebrafy_image.threshold = 0
        self.assertEqual(zebrafy_image.threshold, 0)
        zebrafy_image.threshold = 255
        self.assertEqual(zebrafy_image.threshold, 255)

    def test_zebrafy_image_combined_parameters(self):
        """Test ZebrafyImage with combined parameters."""
        zebrafy_image = ZebrafyImage(
            self.test_image, invert=True, dither=False, threshold=100
        )
        self.assertTrue(zebrafy_image.invert)
        self.assertFalse(zebrafy_image.dither)
        self.assertEqual(zebrafy_image.threshold, 100)


if __name__ == "__main__":
    unittest.main()
