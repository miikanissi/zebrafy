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
from typing import Union

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import CRC, GraphicField, ZebrafyImage, ZebrafyPDF, ZebrafyZPL, __version__


class TestZebrafy(unittest.TestCase):
    def _read_static_file(self, file_name: str) -> Union[bytes, str]:
        """
        Helper method to read a test file from static directory.

        :param file_name: File name of a file in tests/static directory.
        :returns: File contents as bytes or string
        """
        open_mode = "r" if file_name.endswith(".zpl") else "rb"
        with open(
            os.path.join(os.path.join(os.path.dirname(__file__), "static"), file_name),
            open_mode,
        ) as file:
            return file.read()

    def test_version(self):
        """Test package version."""
        self.assertEqual(__version__, "1.0.0")

    ###########
    # CRC Tests
    ###########
    def test_crc_data_bytes(self):
        with self.assertRaises(ValueError):
            CRC(None)
        with self.assertRaises(TypeError):
            CRC(123)

    def test_crc_poly(self):
        crc = CRC(b"Python is fun")
        with self.assertRaises(ValueError):
            crc.poly = None
        with self.assertRaises(TypeError):
            crc.poly = "Test"

    ####################
    # GraphicField Tests
    ####################
    def test_graphic_field_image(self):
        with self.assertRaises(ValueError):
            GraphicField(None)
        with self.assertRaises(TypeError):
            GraphicField(123)

    def test_graphic_field_compression_type(self):
        im = Image.new(mode="RGB", size=(200, 200))
        gf = GraphicField(im)
        with self.assertRaises(ValueError):
            gf.compression_type = None
        with self.assertRaises(TypeError):
            gf.compression_type = 123
        with self.assertRaises(ValueError):
            gf.compression_type = "D"

    ####################
    # ZebrafyImage Tests
    ####################
    # Input validation
    def test_zebrafy_image_image(self):
        """Test ZebrafyImage image input"""
        with self.assertRaises(ValueError):
            ZebrafyImage(None)
        with self.assertRaises(TypeError):
            ZebrafyImage(123)

    def test_zebrafy_image_compression_type(self):
        """Test ZebrafyImage compression_type input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.compression_type = None
        with self.assertRaises(TypeError):
            zebrafy_image.compression_type = 123
        with self.assertRaises(ValueError):
            zebrafy_image.compression_type = "D"

    def test_zebrafy_image_invert(self):
        """Test ZebrafyImage invert input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.invert = None
        with self.assertRaises(TypeError):
            zebrafy_image.invert = "123"

    def test_zebrafy_image_dither(self):
        """Test ZebrafyImage dither input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.dither = None
        with self.assertRaises(TypeError):
            zebrafy_image.dither = "123"

    def test_zebrafy_image_threshold(self):
        """Test ZebrafyImage threshold input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = None
        with self.assertRaises(TypeError):
            zebrafy_image.threshold = "123"
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = -1
        with self.assertRaises(ValueError):
            zebrafy_image.threshold = 256

    def test_zebrafy_image_width(self):
        """Test ZebrafyImage width input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.width = None
        with self.assertRaises(TypeError):
            zebrafy_image.width = "123"

    def test_zebrafy_image_height(self):
        """Test ZebrafyImage height input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.height = None
        with self.assertRaises(TypeError):
            zebrafy_image.height = "123"

    def test_zebrafy_image_pos_x(self):
        """Test ZebrafyImage pos_x input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.pos_x = None
        with self.assertRaises(TypeError):
            zebrafy_image.pos_x = "123"

    def test_zebrafy_image_pos_y(self):
        """Test ZebrafyImage pos_y input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.pos_y = None
        with self.assertRaises(TypeError):
            zebrafy_image.pos_y = "123"

    def test_zebrafy_image_complete_zpl(self):
        """Test ZebrafyImage complete_zpl input"""
        im = Image.new(mode="RGB", size=(200, 200))
        zebrafy_image = ZebrafyImage(im)
        with self.assertRaises(ValueError):
            zebrafy_image.complete_zpl = None
        with self.assertRaises(TypeError):
            zebrafy_image.complete_zpl = "123"

    # Output validation
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

    def test_image_to_zpl_invert(self):
        """Test image to ZPL inverting the image."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), invert=True
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_invert.zpl"))

    def test_image_to_zpl_invert_no_dither(self):
        """Test image to ZPL without dithering and inverting the image."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), dither=False, invert=True
        ).to_zpl()
        self.assertEqual(
            gf_zpl, self._read_static_file("test_image_invert_no_dither.zpl")
        )

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
        """Test image to ZPL with width and height."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), width=500, height=500
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_width_height.zpl"))

    def test_image_to_zpl_pos_x_pos_y(self):
        """Test image to ZPL with pos_x and pos_y."""
        gf_zpl = ZebrafyImage(
            self._read_static_file("test_image.png"), pos_x=100, pos_y=200
        ).to_zpl()
        self.assertEqual(gf_zpl, self._read_static_file("test_image_pos_x_pos_y.zpl"))

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

    ##################
    # ZebrafyPDF Tests
    ##################
    # Input validation
    def test_zebrafy_pdf_pdf_bytes(self):
        """Test ZebrafyImage pdf_bytes input"""
        with self.assertRaises(ValueError):
            ZebrafyPDF(None)
        with self.assertRaises(TypeError):
            ZebrafyPDF(123)

    def test_zebrafy_pdf_compression_type(self):
        """Test ZebrafyPDF compression_type input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.compression_type = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.compression_type = 123
        with self.assertRaises(ValueError):
            zebrafy_pdf.compression_type = "D"

    def test_zebrafy_pdf_invert(self):
        """Test ZebrafyPDF invert input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.invert = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.invert = "123"

    def test_zebrafy_pdf_dither(self):
        """Test ZebrafyPDF dither input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.dither = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.dither = "123"

    def test_zebrafy_pdf_threshold(self):
        """Test ZebrafyPDF threshold input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.threshold = "123"
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = -1
        with self.assertRaises(ValueError):
            zebrafy_pdf.threshold = 256

    def test_zebrafy_pdf_width(self):
        """Test ZebrafyPDF width input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.width = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.width = "123"

    def test_zebrafy_pdf_height(self):
        """Test ZebrafyPDF height input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.height = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.height = "123"

    def test_zebrafy_pdf_pos_x(self):
        """Test ZebrafyPDF pos_x input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.pos_x = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.pos_x = "123"

    def test_zebrafy_pdf_pos_y(self):
        """Test ZebrafyPDF pos_y input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.pos_y = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.pos_y = "123"

    def test_zebrafy_pdf_complete_zpl(self):
        """Test ZebrafyPDF complete_zpl input"""
        pdf = self._read_static_file("test_pdf.pdf")
        zebrafy_pdf = ZebrafyPDF(pdf)
        with self.assertRaises(ValueError):
            zebrafy_pdf.complete_zpl = None
        with self.assertRaises(TypeError):
            zebrafy_pdf.complete_zpl = "123"

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
    # ZebrafyZPL Tests
    ##################
    def test_zebrafy_zpl_zpl_data(self):
        with self.assertRaises(ValueError):
            ZebrafyZPL(None)
        with self.assertRaises(TypeError):
            ZebrafyZPL(123)

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

    def test_broken_zpl_gfc_crc_to_image(self):
        """Test broken ZPL gfc to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_gfc_broken_crc.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

    def test_broken_zpl_gfc_compression_to_image(self):
        """Test broken ZPL gfc to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("test_image_gfc_broken_compression.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_images()

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
