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
import sys
import unittest
from unittest.mock import patch

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import ZebrafyPDF, ZebrafyZPL

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


class TestZebrafyZPLImports(TestZebrafyCommonBase):
    """Test ZebrafyZPL imports."""

    @patch("sys.version_info", (3, 8))
    def test_imports_python_38_or_lower(self):
        """Test ZebrafyZPL imports for Python 3.8 or lower."""
        import importlib

        importlib.reload(sys.modules["zebrafy.zebrafy_zpl"])
        from typing import List, Tuple

        from zebrafy.zebrafy_zpl import DimensionsType, ToImagesType

        self.assertEqual(DimensionsType, Tuple[int, int])
        self.assertEqual(ToImagesType, List[Image.Image])


if __name__ == "__main__":
    unittest.main()
