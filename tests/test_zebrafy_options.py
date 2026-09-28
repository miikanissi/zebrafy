########################################################################################
#
#    Author: Miika Nissi
#    Copyright 2026 Miika Nissi (https://miikanissi.com)
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
from zebrafy import ZebrafyImage, ZebrafyPDF, ZebrafyZPL

from .test_zebrafy_common import TestZebrafyCommonBase

# Option name, default, valid values, values raising TypeError, values raising
# ValueError
SHARED_OPTIONS = [
    ("format", "ASCII", ["B64", "Z64"], [123], [None, "D", ""]),
    ("invert", False, [True], ["123", 1], [None]),
    ("dither", True, [False], ["123", 0], [None]),
    ("threshold", 128, [0, 255], ["123", 1.0, True], [None, -1, 256]),
    ("width", 0, [500], ["123", True], [None, -1]),
    ("height", 0, [500], ["123", True], [None, -1]),
    ("pos_x", 0, [100], ["123"], [None, -1]),
    ("pos_y", 0, [100], ["123"], [None, -1]),
    ("rotation", 0, [90, 180, 270], ["123", 90.0], [None, 45]),
    ("string_line_break", None, [80, None], ["123"], [0, -20]),
    ("complete_zpl", True, [False], ["123"], [None]),
]
PDF_OPTIONS = [
    ("dpi", 72, [36, 720], ["123", 72.0], [None, 0, 721]),
    ("split_pages", True, [False], ["123"], [None]),
]


class TestZebrafyOptions(TestZebrafyCommonBase):
    """Test option validation shared by the converters."""

    def _check_options(self, obj, options):
        for name, default, valid, type_errors, value_errors in options:
            with self.subTest(cls=type(obj).__name__, option=name):
                self.assertEqual(getattr(obj, name), default)
                for value in valid:
                    setattr(obj, name, value)
                    self.assertEqual(getattr(obj, name), value)
                for value in type_errors:
                    with self.assertRaises(TypeError):
                        setattr(obj, name, value)
                for value in value_errors:
                    with self.assertRaises(ValueError):
                        setattr(obj, name, value)
                    # Also rejected when passed to the constructor
                    with self.assertRaises(ValueError):
                        type(obj)(
                            obj.image if hasattr(obj, "image") else obj.pdf_bytes,
                            **{name: value},
                        )

    def test_image_options(self):
        """Test ZebrafyImage option defaults and validation."""
        self._check_options(ZebrafyImage(self.test_image), SHARED_OPTIONS)

    def test_pdf_options(self):
        """Test ZebrafyPDF option defaults and validation."""
        self._check_options(ZebrafyPDF(self.test_pdf), SHARED_OPTIONS + PDF_OPTIONS)

    def test_required_input(self):
        """Test the converted input is required and type checked."""
        for cls in (ZebrafyImage, ZebrafyPDF, ZebrafyZPL):
            with self.subTest(cls=cls.__name__):
                with self.assertRaises(ValueError):
                    cls(None)
                with self.assertRaises(TypeError):
                    cls(123)
        with self.assertRaises(ValueError):
            ZebrafyPDF(b"")

    def test_format_is_case_insensitive(self):
        """Test format is normalized to uppercase."""
        self.assertEqual(ZebrafyImage(self.test_image, format="z64").format, "Z64")

    def test_options_are_keyword_only(self):
        """Test options cannot be passed positionally."""
        with self.assertRaises(TypeError):
            ZebrafyImage(self.test_image, "ASCII")

    def test_compression_type_removed(self):
        """Test the compression_type parameter removed in 2.0.0."""
        with self.assertRaises(TypeError):
            ZebrafyImage(self.test_image, compression_type="A")

    def test_repr_leaves_out_input(self):
        """Test repr shows the options but not the converted data."""
        text = repr(ZebrafyPDF(self.test_pdf, dpi=144))
        self.assertIn("dpi=144", text)
        self.assertNotIn("PDF-1.4", text)


if __name__ == "__main__":
    unittest.main()
