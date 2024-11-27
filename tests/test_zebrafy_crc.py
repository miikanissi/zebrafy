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
from zebrafy import CRC

from .test_zebrafy_common import TestZebrafyCommonBase


class TestZebrafyCRC(TestZebrafyCommonBase):
    """Test ZebrafyCRC."""

    def setUp(self):
        """Set up."""
        super().setUp()
        self.crc = CRC(b"Python is fun")

    def test_crc_data_bytes(self):
        """Test CRC data bytes input."""
        with self.assertRaises(ValueError):
            CRC(None)
        with self.assertRaises(TypeError):
            CRC(123)

    def test_crc_poly(self):
        """Test CRC polynomial input."""
        self.assertEqual(self.crc.poly, 0x8408)
        with self.assertRaises(ValueError):
            self.crc.poly = None
        with self.assertRaises(TypeError):
            self.crc.poly = "Test"


if __name__ == "__main__":
    unittest.main()
