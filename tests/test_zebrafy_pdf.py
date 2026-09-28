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
import re
import unittest
from unittest.mock import patch

# 2. Known third party imports:
import pypdfium2
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import PrinterDPI, ZebrafyImage, ZebrafyPDF, ZebrafyZPL

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyPDF(TestZebrafyCommonBase):
    """Test ZebrafyPDF."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        cls.static_test_pdf = cls._read_static_file("test_pdf.pdf")

    def _two_page_pdf(self):
        """Get a PDF with a 16x2 and a 24x3 dot page at 72 DPI, all black."""
        zpl = (
            ZebrafyImage(Image.new("1", (16, 2), 0), complete_zpl=False).to_zpl()
            + ZebrafyImage(Image.new("1", (24, 3), 0), complete_zpl=False).to_zpl()
        )
        return ZebrafyZPL(zpl, dpi=72).to_pdf()

    # Output validation
    def test_pdf_to_zpl_fixtures(self):
        """Test PDF to ZPL against stored fixtures rendered at 72 DPI."""
        fixtures = {
            "test_pdf_ascii.zpl": {},
            "test_pdf_b64.zpl": {"format": "B64"},
            "test_pdf_z64.zpl": {"format": "Z64"},
            "test_pdf_no_dither.zpl": {"dither": False},
            "test_pdf_low_threshold.zpl": {"dither": False, "threshold": 40},
            "test_pdf_high_threshold.zpl": {"dither": False, "threshold": 215},
            "test_pdf_low_dpi.zpl": {"dpi": 36},
            "test_pdf_high_dpi.zpl": {"dpi": 144},
            "test_pdf_width_height.zpl": {"width": 720, "height": 1280},
            "test_pdf_rotation.zpl": {"rotation": 90},
            "test_pdf_string_line_break.zpl": {"string_line_break": 80},
            "test_pdf_single_label.zpl": {"split_pages": False},
        }
        for file_name, options in fixtures.items():
            with self.subTest(file_name=file_name):
                zpl = ZebrafyPDF(
                    self.static_test_pdf, **{"dpi": 72, **options}
                ).to_zpl()
                self.assertEqual(zpl, self._read_static_file(file_name))

    def test_pdf_default_dpi(self):
        """Test a US Letter PDF renders at 203 DPI by default, one label per page."""
        zpl = ZebrafyPDF(self.static_test_pdf, format="Z64").to_zpl()
        # 8.5 x 11 inches at 203 DPI is 1726 x 2233 dots, 216 bytes per row
        self.assertEqual(
            re.findall(r"\^GFA,\d+,(\d+),(\d+),", zpl),
            [(str(216 * 2233), "216")] * 2,
        )
        self.assertEqual(zpl.count("^XA"), 2)

        zpl = ZebrafyPDF(
            self.static_test_pdf, dpi=PrinterDPI.DPI_300, format="Z64"
        ).to_zpl()
        self.assertIn(",319,", zpl)  # 2550 dots wide at 300 DPI

    def test_split_pages(self):
        """Test each page is a label of its own."""
        zpl = ZebrafyPDF(
            self._two_page_pdf(), dpi=72, pos_x=2, pos_y=5, set_label_size=True
        ).to_zpl()
        self.assertEqual(
            zpl,
            "^XA\n^PW18\n^LL7\n^FO2,5^GFA,4,4,2,FFFFFFFF^FS\n^XZ\n"
            "^XA\n^PW26\n^LL8\n^FO2,5^GFA,9,9,3,FFFFFFFFFFFFFFFFFF^FS\n^XZ\n",
        )

    def test_single_label_stacks_pages(self):
        """Test pages on a single label are stacked instead of overlapping."""
        pdf = ZebrafyPDF(
            self._two_page_pdf(),
            dpi=72,
            pos_x=2,
            pos_y=5,
            split_pages=False,
            set_label_size=True,
        )
        self.assertEqual(
            pdf.to_zpl(),
            "^XA\n^PW26\n^LL10\n"
            "^FO2,5^GFA,4,4,2,FFFFFFFF^FS\n"
            "^FO2,7^GFA,9,9,3,FFFFFFFFFFFFFFFFFF^FS\n"
            "^XZ\n",
        )
        pdf.complete_zpl = False
        self.assertEqual(
            pdf.to_zpl(),
            "^FO2,5^GFA,4,4,2,FFFFFFFF^FS\n^FO2,7^GFA,9,9,3,FFFFFFFFFFFFFFFFFF^FS\n",
        )

    def test_pdf_without_pages(self):
        """Test a PDF without pages is rejected."""
        # PDFium refuses to load a PDF without pages, so fake the rendering
        with (
            patch.object(ZebrafyPDF, "_render_pages", return_value=[]),
            self.assertRaises(ValueError),
        ):
            ZebrafyPDF(self.test_pdf).to_zpl()

    def test_pdf_is_closed(self):
        """Test the PDF document and its pages are closed after conversion."""
        closed = []
        for cls in (pypdfium2.PdfDocument, pypdfium2.PdfPage):
            original = cls.close

            def close(self, original=original, cls=cls):
                closed.append(cls.__name__)
                return original(self)

            patcher = patch.object(cls, "close", close)
            patcher.start()
            self.addCleanup(patcher.stop)

        ZebrafyPDF(self.static_test_pdf, dpi=36).to_zpl()
        self.assertEqual(closed.count("PdfPage"), 2)
        self.assertIn("PdfDocument", closed)


if __name__ == "__main__":
    unittest.main()
