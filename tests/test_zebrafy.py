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
from zebrafy import ZebrafyImage, ZebrafyZPL, __version__


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

    def _image_to_zpl(self, filename, compression_type=None):
        """
        Helper method to convert image to ZPL.

        :param str file_name: File name of a file in tests/static directory.
        :param str compression_type: The compression type used ("A", "B", "C")
        :returns str: ZPL contents as string
        """
        zebrafy_image = ZebrafyImage(
            self._read_static_file(filename), compression_type=compression_type
        )
        zpl = zebrafy_image.to_zpl()
        return zpl

    def _zpl_to_image(self, filename):
        """
        Helper method to convert ZPL to PIL Image.

        :param str file_name: File name of a file in tests/static directory.
        :returns Image: PIL Image from ZPL.
        """
        zebrafy_zpl = ZebrafyZPL(
            self._read_static_file(filename),
        )
        image = zebrafy_zpl.to_image()
        return image

    def test_version(self):
        """Test package version."""
        self.assertEqual(__version__, "0.1.0")

    def test_image_to_default_zpl(self):
        """Test image to ZPL with default options."""
        default_zpl = self._image_to_zpl("image.png")
        self.assertEqual(default_zpl, self._read_static_file("image_zpl_default.zpl"))

    def test_image_to_gfa_zpl(self):
        """Test image to ZPL with A (ASCII) compression."""
        gfa_zpl = self._image_to_zpl("image.png", compression_type="A")
        self.assertEqual(gfa_zpl, self._read_static_file("image_zpl_gfa.zpl"))

    def test_image_to_gfb_zpl(self):
        """Test image to ZPL with B (B64 Binary) compression."""
        gfb_zpl = self._image_to_zpl("image.png", compression_type="B")
        self.assertEqual(gfb_zpl, self._read_static_file("image_zpl_gfb.zpl"))

    def test_image_to_gfc_zpl(self):
        """Test image to ZPL with C (Z64 Binary) compression."""
        gfc_zpl = self._image_to_zpl("image.png", compression_type="C")
        self.assertEqual(gfc_zpl, self._read_static_file("image_zpl_gfc.zpl"))

    def test_gfa_zpl_to_image(self):
        """Test ZPL GFA to image bytes."""
        image = self._zpl_to_image("image_zpl_gfa.zpl")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("zpl_gfa_image.png")
        )

    def test_gfb_zpl_to_image(self):
        """Test ZPL GFB to image bytes."""
        image = self._zpl_to_image("image_zpl_gfb.zpl")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("zpl_gfb_image.png")
        )

    def test_gfc_zpl_to_image(self):
        """Test ZPL GFC to image bytes."""
        image = self._zpl_to_image("image_zpl_gfc.zpl")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        self.assertEqual(
            image_bytes.getvalue(), self._read_static_file("zpl_gfc_image.png")
        )

    def test_broken_zpl_gf_to_image(self):
        """Test broken ZPL to image bytes - resulting in ValueError."""
        zebrafy_broken_zpl = ZebrafyZPL(
            self._read_static_file("broken_zpl_gf.zpl"),
        )
        with self.assertRaises(ValueError):
            zebrafy_broken_zpl.to_image()
