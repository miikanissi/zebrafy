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
import base64
import re
import zlib

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .crc import CRC

GF_MATCHER = re.compile(
    r"\^GF([ABC]*),([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),(.*?(?=\^FS))\^FS"
)


class ZebrafyZPL:
    """
    Provides a method for converting Zebra Programming Language (ZPL) graphic fields \
    to images.

    :param str zpl_data: A valid ZPL string.
    """

    def __init__(self, zpl_data, zid=None):
        self.zpl_data = zpl_data

    def _match_dimensions(self, match):
        """
        Get image dimensions from ZPL graphic field.

        :param Match match: A RegEx Match object
        :returns tuple: A tuple of integers containing the width and height of the \
        graphic field image.
        """
        total = int(match.group(3))
        width = int(match.group(4))

        return int(width * 8), int(total / width)

    def to_image(self):
        """
        Converts Zebra Programming Language (ZPL) graphic fields to PIL Image objects.

        :returns Image: A PIL Image from ZPL graphic fields.
        """
        match = GF_MATCHER.search(self.zpl_data)
        if not match:
            raise ValueError("Could not find an image in ZPL content.")

        width, height = self._match_dimensions(match)
        compression_type = match.group(1).upper()
        data_bytes = match.group(5)

        if (compression_type == "C" and data_bytes.startswith(":Z64")) or (
            compression_type == "B" and data_bytes.startswith(":B64")
        ):
            crc = data_bytes[-4:]
            data_bytes = data_bytes[5:-5]
            if crc != CRC(data_bytes.encode("ascii")).get_crc_hex_string():
                raise ValueError("CRC mismatch.")
            data_bytes = base64.b64decode(data_bytes)
            if compression_type == "C":
                data_bytes = zlib.decompress(data_bytes)

        elif compression_type == "A":
            data_bytes = bytes.fromhex(data_bytes)

        else:
            raise ValueError("Error")

        image = Image.frombytes("1", (width, height), data_bytes)

        return image
