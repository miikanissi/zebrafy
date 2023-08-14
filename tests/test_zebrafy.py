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
import os
import unittest

# 2. Known third party imports:
# 3. Local imports in the relative form:
from zebrafy import ZebrafyImage, ZebrafyPDF, ZebrafyZPL, __version__


class TestZebrafy(unittest.TestCase):
    def _read_static_file(self, file_name):
        """
        Helper method to read a test file from static directory.

        :param str file_name: File name of a file in tests/static directory.
        :returns Union[bytes,str]: File contents as bytes or string
        """
        open_mode = "r" if file_name.endswith(".zpl") else "rb"
        with open(
            os.path.join(os.path.join(os.path.dirname(__file__), "static"), file_name),
            open_mode,
        ) as file:
            return file.read()

    def test_version(self):
        """Test package version."""
        self.assertEqual(__version__, "0.1.0")

    ####################
    # Image to ZPL Tests
    ####################
    def test_image_to_default_zpl(self):
        """Test image to ZPL with default options."""
        default_zpl = ZebrafyImage(self._read_static_file("test_image.png")).to_zpl()
        self.assertEqual(default_zpl, self._read_static_file("test_image_gfa.zpl"))

    def test_image_to_gfa_zpl(self):
        """Test image to ZPL with A (ASCII) compression."""
        gfa_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), compression_type="A"
        ).to_zpl()
        self.assertEqual(gfa_zpl, self._read_static_file("test_image_gfa.zpl"))

    def test_image_to_gfb_zpl(self):
        """Test image to ZPL with B (B64 Binary) compression."""
        gfb_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), compression_type="B"
        ).to_zpl()
        self.assertEqual(gfb_zpl, self._read_static_file("test_image_gfb.zpl"))

    def test_image_to_gfc_zpl(self):
        """Test image to ZPL with C (Z64 Binary) compression."""
        gfc_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), compression_type="C"
        ).to_zpl()
        self.assertEqual(gfc_zpl, self._read_static_file("test_image_gfc.zpl"))

    def test_image_to_zpl_no_dither(self):
        """Test image to ZPL without dithering the image."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), dither=False
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_no_dither.zpl"))

    def test_image_to_zpl_threshold_low(self):
        """Test image to ZPL without dithering the image and low threshold."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), dither=False, threshold=40
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_low_threshold.zpl"))

    def test_image_to_zpl_threshold_high(self):
        """Test image to ZPL without dithering the image and high threshold."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), dither=False, threshold=215
        ).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_image_high_threshold.zpl")
        )

    def test_image_to_zpl_width_height(self):
        """Test image to ZPL without dithering the image and high threshold."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), width=500, height=500
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_width_height.zpl"))

    def test_multiple_image_to_zpl(self):
        """Test multiple images to ZPL with default options."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"),
            complete_zpl=False,
        ).to_zpl()
        complete_zpl = "^XA\n" + gf_zpl + "\n" + gf_zpl + "\n^XZ\n"
        self.assertEqual(
            complete_zpl, self._read_static_file("test_image_multiple.zpl")
        )

    def test_image_not_bytes_or_pil_image(self):
        zebrafy_image = ZebrafyImage("This is not an image")
        with self.assertRaises(ValueError):
            zebrafy_image.to_zpl()

    ####################
    # ZPL to Image Tests
    ####################
    def test_gfa_zpl_to_image(self):
        """Test ZPL GFA to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_gfa.zpl")).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_gfa.png")
        )

    def test_gfb_zpl_to_image(self):
        """Test ZPL GFB to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_gfb.zpl")).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_gfb.png")
        )

    def test_gfc_zpl_to_image(self):
        """Test ZPL GFC to image bytes."""
        image = ZebrafyZPL(self._read_static_file("test_image_gfc.zpl")).to_images()[0]
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("test_image_gfc.png")
        )

    def test_broken_zpl_gf_to_image(self):
        """Test broken ZPL to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_broken.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

    ##################
    # PDF to ZPL Tests
    ##################
    def test_pdf_to_default_zpl(self):
        """Test PDF to ZPL with default options."""
        default_zpl = ZebrafyPDF(self._read_static_file("test_pdf.pdf")).to_zpl()
        self.assertEqual(default_zpl, self._read_static_file("test_pdf_gfa.zpl"))

    def test_pdf_to_gfa_zpl(self):
        """Test PDF to ZPL with A (ASCII) compression."""
        gfa_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), compression_type="A"
        ).to_zpl()
        self.assertEqual(gfa_zpl, self._read_static_file("test_pdf_gfa.zpl"))

    def test_pdf_to_gfb_zpl(self):
        """Test PDF to ZPL with B (B64 Binary) compression."""
        gfb_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), compression_type="B"
        ).to_zpl()
        self.assertEqual(gfb_zpl, self._read_static_file("test_pdf_gfb.zpl"))

    def test_pdf_to_gfc_zpl(self):
        """Test PDF to ZPL with C (Z64 Binary) compression."""
        gfc_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), compression_type="C"
        ).to_zpl()
        self.assertEqual(gfc_zpl, self._read_static_file("test_pdf_gfc.zpl"))

    def test_pdf_to_zpl_no_dither(self):
        """Test PDF to ZPL without dithering the PDF."""
        gf_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), dither=False
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_no_dither.zpl"))

    def test_pdf_to_zpl_threshold_low(self):
        """Test PDF to ZPL without dithering the PDF and low threshold."""
        gf_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), dither=False, threshold=40
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_low_threshold.zpl"))

    def test_pdf_to_zpl_threshold_high(self):
        """Test PDF to ZPL without dithering the PDF and high threshold."""
        gf_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), dither=False, threshold=215
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_high_threshold.zpl"))

    def test_pdf_to_zpl_width_height(self):
        """Test PDF to ZPL without dithering the PDF and high threshold."""
        gf_zpl = ZebrafyPDF(
            self._read_static_file("test_pdf.pdf"), width=720, height=1280
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_pdf_width_height.zpl"))

    ##################
    # ZPL to PDF Tests
    ##################
    def test_gfa_zpl_to_pdf(self):
        """Test ZPL GFA to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_gfa.zpl")).to_pdf()
        gfa_zpl = ZebrafyPDF(pdf_bytes, compression_type="A").to_zpl()
        self.assertEqual(gfa_zpl, self._read_static_file("test_pdf_gfa.zpl"))

    def test_gfb_zpl_to_pdf(self):
        """Test ZPL GFB to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_gfb.zpl")).to_pdf()
        gfb_zpl = ZebrafyPDF(pdf_bytes, compression_type="B").to_zpl()
        self.assertEqual(gfb_zpl, self._read_static_file("test_pdf_gfb.zpl"))

    def test_gfc_zpl_to_pdf(self):
        """Test ZPL GFC to PDF bytes."""
        pdf_bytes = ZebrafyZPL(self._read_static_file("test_pdf_gfc.zpl")).to_pdf()
        gfc_zpl = ZebrafyPDF(pdf_bytes, compression_type="C").to_zpl()
        self.assertEqual(gfc_zpl, self._read_static_file("test_pdf_gfc.zpl"))
