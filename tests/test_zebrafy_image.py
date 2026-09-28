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
import io
import unittest

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import ZebrafyImage, ZebrafyPDF, ZebrafyZPL

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyImage(TestZebrafyCommonBase):
    """Test ZebrafyImage."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        cls.static_test_image = cls._read_static_file("test_image.png")

    def _assert_fixture(self, file_name, **options):
        zpl = ZebrafyImage(self.static_test_image, **options).to_zpl()
        self.assertEqual(zpl, self._read_static_file(file_name))

    # Output validation
    def test_image_to_zpl_fixtures(self):
        """Test image to ZPL against stored fixtures."""
        fixtures = {
            "test_image_ascii.zpl": {},
            "test_image_b64.zpl": {"format": "B64"},
            "test_image_z64.zpl": {"format": "Z64"},
            "test_image_invert.zpl": {"invert": True},
            "test_image_invert_no_dither.zpl": {"dither": False, "invert": True},
            "test_image_no_dither.zpl": {"dither": False},
            "test_image_low_threshold.zpl": {"dither": False, "threshold": 40},
            "test_image_high_threshold.zpl": {"dither": False, "threshold": 215},
            "test_image_width_height.zpl": {"width": 500, "height": 500},
            "test_image_pos_x_pos_y.zpl": {"pos_x": 100, "pos_y": 200},
            "test_image_rotation.zpl": {"rotation": 90},
            "test_image_string_line_break.zpl": {"string_line_break": 80},
        }
        for file_name, options in fixtures.items():
            with self.subTest(file_name=file_name):
                self._assert_fixture(file_name, **options)

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
        self.assertTrue(ZebrafyImage(jpeg_image).to_zpl().startswith("^XA\n^FO0,0^GFA"))

    def test_black_pixels_are_printed(self):
        """Test black pixels become 1 bits, which ZPL prints as dots."""
        image = Image.new("L", (16, 2), 255)
        image.putpixel((0, 0), 0)
        for dither in (True, False):
            zpl = ZebrafyImage(image, dither=dither, complete_zpl=False).to_zpl()
            self.assertEqual(zpl, "^FO0,0^GFA,4,4,2,80000000^FS")
        zpl = ZebrafyImage(image, invert=True, complete_zpl=False).to_zpl()
        self.assertEqual(zpl, "^FO0,0^GFA,4,4,2,7FFFFFFF^FS")

    def test_rotation_is_clockwise_without_cropping(self):
        """Test rotation keeps the whole image and matches PDF rotation."""
        image = Image.new("L", (80, 40), 255)
        image.paste(0, (0, 0, 8, 8))  # marker in the top left corner

        rotated = ZebrafyZPL(
            ZebrafyImage(image, rotation=90, dither=False).to_zpl()
        ).to_images()[0]
        self.assertEqual(rotated.size, (40, 80))
        # Clockwise rotation moves the top left corner to the top right
        self.assertEqual(rotated.getpixel((35, 2)), 0)
        self.assertEqual(rotated.getpixel((2, 2)), 255)

        pdf = ZebrafyZPL(ZebrafyImage(image, dither=False).to_zpl()).to_pdf()
        pdf_rotated = ZebrafyZPL(
            ZebrafyPDF(pdf, rotation=90, dither=False, dpi=72).to_zpl()
        ).to_images()[0]
        self.assertEqual(pdf_rotated.tobytes(), rotated.tobytes())

        for rotation, size in ((180, (80, 40)), (270, (40, 80))):
            zpl = ZebrafyImage(image, rotation=rotation).to_zpl()
            self.assertEqual(ZebrafyZPL(zpl).to_images()[0].size, size)

    def test_transparent_pixels_are_white(self):
        """Test transparent pixels are treated as white."""
        opaque_black = (0, 0, 0, 255)
        transparent_black = (0, 0, 0, 0)
        rgba = Image.new("RGBA", (16, 1), transparent_black)
        rgba.putpixel((0, 0), opaque_black)

        # Both palette entries are black, only entry 0 is transparent
        palette = Image.new("P", (16, 1), 0)
        palette.putpalette([0, 0, 0, 0, 0, 0])
        palette.putpixel((0, 0), 1)
        palette.info["transparency"] = 0

        grayscale_alpha = rgba.convert("LA")

        for image in (rgba, palette, grayscale_alpha):
            with self.subTest(mode=image.mode):
                zpl = ZebrafyImage(image, dither=False, complete_zpl=False).to_zpl()
                self.assertEqual(zpl, "^FO0,0^GFA,2,2,2,8000^FS")

        # Transparency survives a round trip through PNG bytes
        png = io.BytesIO()
        rgba.save(png, format="PNG")
        zpl = ZebrafyImage(png.getvalue(), dither=False, complete_zpl=False).to_zpl()
        self.assertEqual(zpl, "^FO0,0^GFA,2,2,2,8000^FS")


if __name__ == "__main__":
    unittest.main()
