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
import operator

# 2. Known third party imports:

# 3. Local imports in the relative form:


class CRC:
    """
    Utility class to calculate CRC-16-CCITT algorithm across the received data bytes.

    CRC-16-CCITT polynomial representation: x^{16} + x^{12} + x^5 + 1

    :param data_bytes: Bytes object for which to calculate CRC
    :param poly: Reversed polynomial representation for CRC-16-CCITT calculation, \
    defaults to ``0x8408``
    """

    def __init__(self, data_bytes: bytes, poly: int = None):
        self.data_bytes = data_bytes
        if poly is None:
            poly = 0x8408
        self.poly = poly

    data_bytes = property(operator.attrgetter("_data_bytes"))

    @data_bytes.setter
    def data_bytes(self, d):
        if d is None:
            raise ValueError("Bytes data cannot be empty.")
        if not isinstance(d, bytes):
            raise TypeError(
                f"Bytes data must be a valid bytes object. {type(d)} was given."
            )
        self._data_bytes = d

    poly = property(operator.attrgetter("_poly"))

    @poly.setter
    def poly(self, p):
        if p is None:
            raise ValueError("Polynomial cannot be empty.")
        if not isinstance(p, int):
            raise TypeError(f"Polynomial must be a valid integer. {type(p)} was given.")
        self._poly = p

    def _get_crc16_ccitt(self) -> int:
        """
        Calculate CRC-16-CCITT Algorithm.

        :returns: CRC-16-CCITT
        """
        data = bytearray(self._data_bytes)
        crc = 0xFFFF
        for b in data:
            cur_byte = 0xFF & b
            for _ in range(0, 8):
                if (crc & 0x0001) ^ (cur_byte & 0x0001):
                    crc = (crc >> 1) ^ self._poly
                else:
                    crc >>= 1
                cur_byte >>= 1
        crc = ~crc & 0xFFFF
        crc = (crc << 8) | ((crc >> 8) & 0xFF)

        return crc & 0xFFFF

    def get_crc_hex_string(self) -> str:
        """
        Get CRC-16-CCITT as four digit zero padding hexadecimal string.

        :returns: CRC-16-CCITT as four digit zero padding hexadecimal string
        """
        return f"{self._get_crc16_ccitt():04X}"
