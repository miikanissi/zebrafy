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
import operator
import zlib

# 2. Known third party imports:
from PIL.Image import Image

# 3. Local imports in the relative form:
from .crc import CRC


class GraphicField:
    """
    Converts a PIL image to Zebra Programming Language (ZPL) graphic field data.

    :param PIL.Image.Image image: An instance of a PIL Image.
    :param compression_type: ZPL compression type parameter that accepts the \
    following values, defaults to ``"A"``:

        - ``"A"``: ASCII hexadecimal - most compatible (default)
        - ``"B"``: Base64 binary
        - ``"C"``: LZ77 / Zlib compressed base64 binary - best compression
    """

    def __init__(self, pil_image: Image, compression_type: str = None):
        self.pil_image = pil_image
        if compression_type is None:
            compression_type = "a"
        self.compression_type = compression_type.upper()

    pil_image = property(operator.attrgetter("_pil_image"))

    @pil_image.setter
    def pil_image(self, i):
        if not i:
            raise ValueError("Image cannot be empty.")
        if not isinstance(i, Image):
            raise TypeError(
                "Image must be a valid PIL.Image.Image object. {param_type} was given."
                .format(param_type=type(i))
            )
        self._pil_image = i

    compression_type = property(operator.attrgetter("_compression_type"))

    @compression_type.setter
    def compression_type(self, c):
        if c is None:
            raise ValueError("Compression type cannot be empty.")
        if not isinstance(c, str):
            raise TypeError(
                "Compression type must be a valid string. {param_type} was given."
                .format(param_type=type(c))
            )
        if c not in ["A", "B", "C"]:
            raise ValueError(
                'Compression type must be "A","B", or "C". {param} was given.'.format(
                    param=c
                )
            )
        self._compression_type = c

    def _get_binary_byte_count(self) -> int:
        """
        Get binary byte count.

        This is the total number of bytes to be transmitted for the total image or
        the total number of bytes that follow parameter bytes_per_row. For ASCII \
        download, the parameter should match parameter graphic_field_count. \
        Out-of-range values are set to the nearest limit.

        :returns: Binary byte count
        """
        return len(self._get_data_string())

    def _get_bytes_per_row(self) -> int:
        """
        Get bytes per row.

        This is the number of bytes in the image data that comprise one row of the \
        image.

        :returns: Bytes per row
        """
        return int((self._pil_image.size[0] + 7) / 8)

    def _get_graphic_field_count(self) -> int:
        """
        Get graphic field count.

        This is the total number of bytes comprising the image data (width x height).

        :returns: Graphic field count."
        """
        return int(self._get_bytes_per_row() * self._pil_image.size[1])

    def _get_data_string(self) -> str:
        """
        Get graphic field data string depending on compression type.

        :returns: Graphic field data string depending on compression type.
        """
        image_bytes = self._pil_image.tobytes()
        data_string = ""

        # Compression type A: Convert bytes to ASCII hexadecimal
        if self._compression_type == "A":
            data_string = image_bytes.hex()

        # Compression type B: Convert bytes to base64 and add header + CRC
        elif self._compression_type == "B":
            b64_bytes = base64.b64encode(image_bytes)
            data_string = ":B64:{encoded_data}:{crc}".format(
                encoded_data=b64_bytes.decode("ascii"),
                crc=CRC(b64_bytes).get_crc_hex_string(),
            )

        # Compression type C: Convert LZ77/ Zlib compressed bytes to base64 and add
        # header + CRC
        elif self._compression_type == "C":
            z64_bytes = base64.b64encode(zlib.compress(image_bytes))
            data_string = ":Z64:{encoded_data}:{crc}".format(
                encoded_data=z64_bytes.decode("ascii"),
                crc=CRC(z64_bytes).get_crc_hex_string(),
            )

        return data_string

    def get_graphic_field(self) -> str:
        """
        Get a complete graphic field string for ZPL.

        :returns: Complete graphic field string for ZPL.
        """
        return "^GF{comp_type},{bb_count},{gf_count},{bpr},{data}^FS".format(
            comp_type=self._compression_type,
            bb_count=self._get_binary_byte_count(),
            gf_count=self._get_graphic_field_count(),
            bpr=self._get_bytes_per_row(),
            data=self._get_data_string(),
        )
