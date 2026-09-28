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
    Utility class to calculate CRC-16/XMODEM algorithm across the received data bytes.

    Zebra printers validate B64 and Z64 graphic field data with CRC-16/XMODEM \
    (polynomial ``0x1021``, initial value ``0x0000``, no reflection, no final XOR).

    CRC-16 polynomial representation: x^{16} + x^{12} + x^5 + 1

    :param data_bytes: Bytes object for which to calculate CRC
    :param poly: Polynomial representation for CRC-16/XMODEM calculation, \
    defaults to ``0x1021``
    """

    def __init__(self, data_bytes: bytes, poly: int = None):
        self.data_bytes = data_bytes
        if poly is None:
            poly = 0x1021
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

    def _get_crc16_xmodem(self) -> int:
        """
        Calculate CRC-16/XMODEM Algorithm.

        :returns: CRC-16/XMODEM
        """
        crc = 0x0000
        for b in self._data_bytes:
            crc ^= b << 8
            for _ in range(0, 8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ self._poly
                else:
                    crc <<= 1
                crc &= 0xFFFF

        return crc

    def get_crc_hex_string(self) -> str:
        """
        Get CRC-16/XMODEM as four digit zero padding hexadecimal string.

        :returns: CRC-16/XMODEM as four digit zero padding hexadecimal string
        """
        return f"{self._get_crc16_xmodem():04X}"
