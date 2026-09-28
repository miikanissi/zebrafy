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
import pypdfium2
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import ZebrafyImage, ZebrafyPDF, ZebrafyZPL
from zebrafy.graphic_field import invert_monochrome

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyZPL(TestZebrafyCommonBase):
    """Test ZebrafyZPL."""

    def test_zebrafy_zpl_zpl_data(self):
        """Test ZebrafyZPL zpl_data input."""
        with self.assertRaises(ValueError):
            ZebrafyZPL(None)
        with self.assertRaises(TypeError):
            ZebrafyZPL(123)

    def test_ascii_zpl_to_image(self):
        """Test ZPL GFA ASCII to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_ascii.zpl")).to_images()[
            0
        ]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_ascii.png")
        )

    def test_b64_zpl_to_image(self):
        """Test ZPL GFA B64 to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_b64.zpl")).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_b64.png")
        )

    def test_z64_zpl_to_image(self):
        """Test ZPL GFA Z64 to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_z64.zpl")).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_z64.png")
        )

    def test_string_line_break_zpl_to_image(self):
        """Test ZPL GFA with line breaks in graphic field data to image."""
        image = ZebrafyZPL(
            self._read_static_file("test_image_string_line_break.zpl")
        ).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_ascii.png")
        )

        test_image = Image.new("1", (16, 4))
        test_image.putpixel((3, 1), 1)
        for format in ["ASCII", "B64", "Z64"]:
            zpl = ZebrafyImage(test_image, format=format, string_line_break=3).to_zpl()
            self.assertIn("\n", zpl.split("^GF", 1)[1])
            image = ZebrafyZPL(zpl).to_images()[0]
            self.assertEqual(image.tobytes(), test_image.tobytes())

    def test_compressed_ascii_zpl_to_image(self):
        """Test ZPL GFA compressed ASCII to image."""
        image = ZebrafyZPL(
            self._read_static_file("test_zpl_ascii_compressed.zpl")
        ).to_images()[0]
        self.assertEqual(image.size, (88, 131))

    def test_decompress_ascii(self):
        """Test ZPL ASCII compression characters."""

        def to_bytes(bytes_total, bytes_per_row, data):
            zpl = f"^XA^GFA,{bytes_total},{bytes_total},{bytes_per_row},{data}^FS^XZ"
            # Images show printed 1 bits as black 0 pixels, so invert them back
            return invert_monochrome(ZebrafyZPL(zpl).to_images()[0]).tobytes()

        # Repeat counts, zero fill, one fill and previous row repeat
        self.assertEqual(
            to_bytes(8, 2, "HF0,!:G8I0"), bytes.fromhex("FF00FFFFFFFF8000")
        )
        # Combined repeat counts: h (40) + G (1) = 41
        self.assertEqual(to_bytes(25, 25, "hGFI0,"), bytes.fromhex("F" * 41 + "0" * 9))
        # Largest repeat count z (400)
        self.assertEqual(to_bytes(200, 200, "zF"), bytes.fromhex("F" * 400))
        # Repeat count spanning multiple rows
        self.assertEqual(to_bytes(2, 1, "JA"), bytes.fromhex("AAAA"))
        # Unterminated last row is filled with zeros
        self.assertEqual(to_bytes(2, 1, "F,F"), bytes.fromhex("F0F0"))
        # Lowercase hexadecimal is not a repeat count
        self.assertEqual(to_bytes(2, 2, "ab,"), bytes.fromhex("AB00"))
        # Whitespace is ignored
        self.assertEqual(to_bytes(2, 2, "F F,"), bytes.fromhex("FF00"))

        with self.assertRaises(ValueError):
            to_bytes(2, 1, ":FF")
        with self.assertRaises(ValueError):
            to_bytes(2, 1, "F:F")
        with self.assertRaises(ValueError):
            to_bytes(2, 1, "FFZ,")

    def test_broken_zpl_gf_to_image(self):
        """Test broken ZPL to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_broken.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

    def test_broken_zpl_z64_crc_to_image(self):
        """Test broken ZPL GFA Z64 to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_z64_broken_crc.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

    def test_broken_zpl_z64_compression_to_image(self):
        """Test broken ZPL GFA Z64 to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_z64_broken_compression.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

    def test_zebrafy_zpl_dpi(self):
        """Test ZebrafyZPL dpi input."""
        self.assertEqual(ZebrafyZPL(self.test_zpl).dpi, 203)
        with self.assertRaises(ValueError):
            ZebrafyZPL(self.test_zpl, dpi=0)

    def test_printed_dots_are_black(self):
        """Test 1 bits, which ZPL prints, become black pixels."""
        image = ZebrafyZPL("^XA^GFA,2,2,1,80,^FS^XZ").to_images()[0]
        self.assertEqual(image.getpixel((0, 0)), 0)
        self.assertEqual(image.getpixel((1, 0)), 255)
        self.assertEqual(image.getpixel((0, 1)), 255)

    def test_to_pdf_is_lossless(self):
        """Test the PDF from ZPL holds the exact image at its physical size."""
        # Decoded images are a whole number of bytes wide, so use 408 dots
        image = Image.new("1", (408, 203), 255)
        for x in range(0, 408, 3):
            image.putpixel((x, x % 203), 0)
        zpl = ZebrafyImage(image, dither=False).to_zpl()

        pdf = pypdfium2.PdfDocument(ZebrafyZPL(zpl).to_pdf())
        try:
            page = pdf[0]
            # 408 x 203 dots at 203 DPI is 144.7 x 72 points
            width, height = page.get_size()
            self.assertAlmostEqual(width, 408 * 72 / 203, places=3)
            self.assertEqual(height, 72)
            (image_object,) = page.get_objects(
                filter=[pypdfium2.raw.FPDF_PAGEOBJ_IMAGE]
            )
            stored = image_object.get_bitmap().to_pil().convert("1")
            page.close()
        finally:
            pdf.close()
        self.assertEqual(stored.tobytes(), image.tobytes())

        # Page size follows the given printer resolution
        pdf = pypdfium2.PdfDocument(ZebrafyZPL(zpl, dpi=72).to_pdf())
        try:
            self.assertEqual(pdf[0].get_size(), (408, 203))
        finally:
            pdf.close()

    def test_ascii_zpl_to_pdf(self):
        """Test ZPL GFA ASCII to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_ascii.zpl")).to_pdf()
        ascii_zpl = ZebrafyPDF(pdf_bytes, format="ASCII").to_zpl()
        self.assertEqual(ascii_zpl, self._read_static_file("test_pdf_ascii.zpl"))

    def test_b64_zpl_to_pdf(self):
        """Test ZPL GFA B64 to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_b64.zpl")).to_pdf()
        b64_zpl = ZebrafyPDF(pdf_bytes, format="B64").to_zpl()
        self.assertEqual(b64_zpl, self._read_static_file("test_pdf_b64.zpl"))

    def test_z64_zpl_to_pdf(self):
        """Test ZPL GFA Z64 to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_z64.zpl")).to_pdf()
        z64_zpl = ZebrafyPDF(pdf_bytes, format="Z64").to_zpl()
        self.assertEqual(z64_zpl, self._read_static_file("test_pdf_z64.zpl"))


if __name__ == "__main__":
    unittest.main()
