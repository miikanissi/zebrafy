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
from zebrafy import ZebrafyPDF

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyPDF(TestZebrafyCommonBase):
    """Test ZebrafyPDF."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        cls.static_test_pdf = cls._read_static_file("test_pdf.pdf")

    def test_zebrafy_pdf_pdf_bytes(self):
        """Test ZebrafyImage pdf_bytes input."""
        with self.assertRaises(ValueError):
            ZebrafyPDF(None)
        with self.assertRaises(TypeError):
            ZebrafyPDF(123)

    def test_zebrafy_pdf_format(self):
        """Test ZebrafyPDF format input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.format, "ASCII")
        with self.assertRaises(ValueError):
            zebrafy_pdf.format = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.format = 123
        with self.assertRaises(ValueError):
            zebrafy_pdf.format = "D"

    def test_zebrafy_pdf_deprecated_compression_type(self):
        """Test deprecated ZebrafyPDF compression_type input."""
        gfa = ZebrafyPDF(self.test_pdf, compression_type="A")
        self.assertEqual(gfa.format, "ASCII")
        gfb = ZebrafyPDF(self.test_pdf, compression_type="B")
        self.assertEqual(gfb.format, "B64")
        gfc = ZebrafyPDF(self.test_pdf, compression_type="C")
        self.assertEqual(gfc.format, "Z64")

    def test_zebrafy_pdf_invert(self):
        """Test ZebrafyPDF invert input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertFalse(zebrafy_pdf.invert)
        with self.assertRaises(ValueError):
            zebrafy_pdf.invert = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.invert = "123"

    def test_zebrafy_pdf_dither(self):
        """Test ZebrafyPDF dither input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertTrue(zebrafy_pdf.dither)
        with self.assertRaises(ValueError):
            zebrafy_pdf.dither = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.dither = "123"

    def test_zebrafy_pdf_threshold(self):
        """Test ZebrafyPDF threshold input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.threshold, 128)
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.threshold = "123"
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = -1
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = 256

    def test_zebrafy_pdf_dpi(self):
        """Test ZebrafyPDF dpi input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.dpi, 72)
        with self.assertRaises(ValueError):
            zebrafy_pdf.dpi = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.dpi = "123"
        with self.assertRaises(ValueError):
            zebrafy_pdf.dpi = -1
        with self.assertRaises(ValueError):
            zebrafy_pdf.dpi = 0
        with self.assertRaises(ValueError):
            zebrafy_pdf.dpi = 721

    def test_zebrafy_pdf_width(self):
        """Test ZebrafyPDF width input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.width, 0)
        with self.assertRaises(ValueError):
            zebrafy_pdf.width = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.width = "123"

    def test_zebrafy_pdf_height(self):
        """Test ZebrafyPDF height input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.height, 0)
        with self.assertRaises(ValueError):
            zebrafy_pdf.height = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.height = "123"

    def test_zebrafy_pdf_pos_x(self):
        """Test ZebrafyPDF pos_x input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.pos_x, 0)
        with self.assertRaises(ValueError):
            zebrafy_pdf.pos_x = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.pos_x = "123"

    def test_zebrafy_pdf_pos_y(self):
        """Test ZebrafyPDF pos_y input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.pos_y, 0)
        with self.assertRaises(ValueError):
            zebrafy_pdf.pos_y = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.pos_y = "123"

    def test_zebrafy_pdf_rotation(self):
        """Test ZebrafyPDF rotation."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertEqual(zebrafy_pdf.rotation, 0)
        with self.assertRaises(ValueError):
            zebrafy_pdf.rotation = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.rotation = "123"
        with self.assertRaises(TypeError):
            zebrafy_pdf.rotation = 90.0
        with self.assertRaises(ValueError):
            zebrafy_pdf.rotation = 45

    def test_zebrafy_pdf_string_line_break(self):
        """Test ZebrafyPdf string_line_break input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertIsNone(zebrafy_pdf.string_line_break)
        with self.assertRaises(TypeError):
            zebrafy_pdf.string_line_break = "123"
        with self.assertRaises(ValueError):
            zebrafy_pdf.string_line_break = -20

    def test_zebrafy_pdf_complete_zpl(self):
        """Test ZebrafyPDF complete_zpl input."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertTrue(zebrafy_pdf.complete_zpl)
        with self.assertRaises(ValueError):
            zebrafy_pdf.complete_zpl = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.complete_zpl = "123"

    def test_zebrafy_pdf_split_pages(self):
        """Test ZebrafyPDF split pages."""
        zebrafy_pdf = ZebrafyPDF(self.test_pdf)
        self.assertFalse(zebrafy_pdf.split_pages)
        with self.assertRaises(ValueError):
            zebrafy_pdf.split_pages = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.split_pages = "123"

    def test_pdf_to_default_zpl(self):
        """Test PDF to ZPL with default options."""
        default_zpl = ZebrafyPDF(self.static_test_pdf).to_zpl()
        self.assertEqual(default_zpl, self._read_static_file("test_pdf_ascii.zpl"))

    def test_pdf_to_ascii_zpl(self):
        """Test PDF to ZPL with A (ASCII) compression."""
        ascii_zpl = ZebrafyPDF(self.static_test_pdf, format="ASCII").to_zpl()
        self.assertEqual(ascii_zpl, self._read_static_file("test_pdf_ascii.zpl"))

    def test_pdf_to_b64_zpl(self):
        """Test PDF to ZPL with B (B64 Binary) compression."""
        b64_zpl = ZebrafyPDF(self.static_test_pdf, format="B64").to_zpl()
        self.assertEqual(b64_zpl, self._read_static_file("test_pdf_b64.zpl"))

    def test_pdf_to_z64_zpl(self):
        """Test PDF to ZPL with C (Z64 Binary) compression."""
        z64_zpl = ZebrafyPDF(self.static_test_pdf, format="Z64").to_zpl()
        self.assertEqual(z64_zpl, self._read_static_file("test_pdf_z64.zpl"))

    def test_pdf_to_zpl_no_dither(self):
        """Test PDF to ZPL without dithering the PDF."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, dither=False).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_no_dither.zpl"))

    def test_pdf_to_zpl_threshold_low(self):
        """Test PDF to ZPL without dithering the PDF and low threshold."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, dither=False, threshold=40).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_low_threshold.zpl"))

    def test_pdf_to_zpl_threshold_high(self):
        """Test PDF to ZPL without dithering the PDF and high threshold."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, dither=False, threshold=215).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_high_threshold.zpl"))

    def test_pdf_to_zpl_dpi_low(self):
        """Test PDF to ZPL with low DPI."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, dpi=36).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_low_dpi.zpl"))

    def test_pdf_to_zpl_dpi_high(self):
        """Test PDF to ZPL with high DPI."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, dpi=144).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_high_dpi.zpl"))

    def test_pdf_to_zpl_width_height(self):
        """Test PDF to ZPL with set width and height."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, width=720, height=1280).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_width_height.zpl"))

    def test_pdf_to_zpl_rotation(self):
        """Test PDF to ZPL with rotation."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, rotation=90).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_rotation.zpl"))

    def test_pdf_to_zpl_string_line_break(self):
        """Test PDF to ZPL with string_line_break."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, string_line_break=80).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_pdf_string_line_break.zpl")
        )

    def test_pdf_to_zpl_split_pages(self):
        """Test PDF to ZPL with split pages."""
        gf_zpl = ZebrafyPDF(self.static_test_pdf, split_pages=True).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_split_pages.zpl"))


if __name__ == "__main__":
    unittest.main()
