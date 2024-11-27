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
import importlib
import os
import sys
import unittest
from importlib.metadata import version
from typing import Union
from unittest.mock import patch

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:


class TestZebrafyCommonBase(unittest.TestCase):
    """Test Zebrafy common base."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        cls.test_image = Image.new(mode="RGB", size=(200, 200))
        cls.test_zpl = (
            "^XA\n" "^FO50,50\n" "^GFA,16,16,1,,\n" "FFFFFFFFFFFFFFFF\n" "^XZ"
        )
        cls.test_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj\n"
            b"<< /Type /Catalog /Pages 2 0 R >>\n"
            b"endobj\n"
            b"2 0 obj\n"
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
            b"endobj\n"
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\n"
            b"endobj\n"
            b"4 0 obj\n"
            b"<< /Length 44 >>\n"
            b"stream\n"
            b"BT /F1 24 Tf 100 700 Td (Hello, World!) Tj ET\n"
            b"endstream\n"
            b"endobj\n"
            b"xref\n"
            b"0 5\n"
            b"0000000000 65535 f \n"
            b"0000000010 00000 n \n"
            b"0000000060 00000 n \n"
            b"0000000110 00000 n \n"
            b"0000000210 00000 n \n"
            b"trailer\n"
            b"<< /Size 5 /Root 1 0 R >>\n"
            b"startxref\n"
            b"260\n"
            b"%%EOF"
        )

    @classmethod
    def _read_static_file(cls, file_name: str) -> Union[bytes, str]:
        """
        Read a test file from static directory.

        :param file_name: File name of a file in tests/static directory.
        :returns: File contents as bytes or string
        """
        open_mode = "r" if file_name.endswith(".zpl") else "rb"
        with open(
            os.path.join(os.path.join(os.path.dirname(__file__), "static"), file_name),
            open_mode,
        ) as file:
            return file.read()


class TestZebrafyCommon(TestZebrafyCommonBase):
    """Test Zebrafy common."""

    def test_version(self):
        """Test package version."""
        from zebrafy import __version__

        self.assertEqual(__version__, version("zebrafy"))

    def test_import_error(self):
        """Test import error handling."""
        version_file = os.path.join(
            os.path.dirname(__file__), "..", "zebrafy", "_version.py"
        )
        temp_version_file = version_file + ".bak"

        # Rename the _version.py file to simulate ImportError
        os.rename(version_file, temp_version_file)

        try:
            with patch.dict("sys.modules", {"zebrafy._version": None}):
                importlib.invalidate_caches()
                try:
                    del sys.modules["zebrafy"]
                except KeyError:
                    pass

                try:
                    from zebrafy import __version__
                except ImportError:
                    __version__ = "unknown version"

                self.assertEqual(__version__, "unknown version")
        finally:
            # Restore the _version.py file
            os.rename(temp_version_file, version_file)
            importlib.invalidate_caches()
            importlib.reload(sys.modules["zebrafy"])


if __name__ == "__main__":
    unittest.main()
