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
from zebrafy.crc import CRC


class GraphicField:
    """
    Converts a PIL image to Zebra Programming Language (ZPL) graphic field data.

    :param PIL.Image.Image image: An instance of a PIL Image.
    :param compression_type (deprecated): ZPL compression type parameter that accepts \
    the following values, defaults to ``"A"``:

        - ``"A"``: ASCII hexadecimal - most compatible (default)
        - ``"B"``: Base64 binary
        - ``"C"``: LZ77 / Zlib compressed base64 binary - best compression
    :param format: ZPL format parameter that accepts the following values, \
    defaults to ``"ASCII"``:

        - ``"ASCII"``: ASCII hexadecimal - most compatible (default)
        - ``"B64"``: Base64 binary
        - ``"Z64"``: LZ77 / Zlib compressed base64 binary - best compression
    :param string_line_break: Number of characters in graphic field content after \
    which a new line is added, defaults to `None`.

    .. deprecated:: 1.1.0
        The `compression_type` parameter is deprecated in favor of `format` and will \
        be removed in version 2.0.0.
    """

    def __init__(
        self,
        pil_image: Image,
        compression_type: str = None,
        format: str = None,
        string_line_break: int = None,
    ):
        self.pil_image = pil_image
        if format is None:
            if compression_type is None:
                format = "ASCII"
            else:
                format = self._compression_type_to_format(compression_type)
        self.format = format.upper()
        self.string_line_break = string_line_break

    pil_image = property(operator.attrgetter("_pil_image"))

    @pil_image.setter
    def pil_image(self, i):
        if not i:
            raise ValueError("Image cannot be empty.")
        if not isinstance(i, Image):
            raise TypeError(
                f"Image must be a valid PIL.Image.Image object. {type(i)} was given."
            )
        self._pil_image = i

    format = property(operator.attrgetter("_format"))

    @format.setter
    def format(self, f):
        if f is None:
            raise ValueError("Format cannot be empty.")
        if not isinstance(f, str):
            raise TypeError(f"Format must be a valid string. {type(f)} was given.")
        if f not in ["ASCII", "B64", "Z64"]:
            raise ValueError(
                f'Format type must be "ASCII","B64", or "Z64". {f} was given.'
            )
        self._format = f

    string_line_break = property(operator.attrgetter("_string_line_break"))

    @string_line_break.setter
    def string_line_break(self, s):
        if s and not isinstance(s, int):
            raise TypeError(
                f"String line break must be a valid integer. {type(s)} was given."
            )
        if s and s < 1:
            raise ValueError("String line break must be greater than 0.")
        self._string_line_break = s

    def _compression_type_to_format(self, compression_type: str) -> str:
        """Convert deprecated compression type to format."""
        if compression_type.upper() == "A":
            return "ASCII"
        elif compression_type.upper() == "B":
            return "B64"
        elif compression_type.upper() == "C":
            return "Z64"

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
        Get graphic field data string depending on format.

        :returns: Graphic field data string depending on format.
        """
        image_bytes = self._pil_image.tobytes()
        data_string = ""

        # Format ASCII: Convert bytes to ASCII hexadecimal
        if self._format == "ASCII":
            data_string = image_bytes.hex()

        # Format B64: Convert bytes to base64 and add header + CRC
        elif self._format == "B64":
            b64_bytes = base64.b64encode(image_bytes)
            data_string = ":B64:{encoded_data}:{crc}".format(
                encoded_data=b64_bytes.decode("ascii"),
                crc=CRC(b64_bytes).get_crc_hex_string(),
            )

        # Format Z64: Convert LZ77/ Zlib compressed bytes to base64 and add
        # header + CRC
        elif self._format == "Z64":
            z64_bytes = base64.b64encode(zlib.compress(image_bytes))
            data_string = ":Z64:{encoded_data}:{crc}".format(
                encoded_data=z64_bytes.decode("ascii"),
                crc=CRC(z64_bytes).get_crc_hex_string(),
            )

        if self._string_line_break:
            data_string = "\n".join(
                data_string[i : i + self._string_line_break]
                for i in range(0, len(data_string), self._string_line_break)
            )
        return data_string

    def get_graphic_field(self) -> str:
        """
        Get a complete graphic field string for ZPL.

        :returns: Complete graphic field string for ZPL.
        """
        return (
            f"^GFA,{self._get_binary_byte_count()},{self._get_graphic_field_count()},"
            f"{self._get_bytes_per_row()},{self._get_data_string()}^FS"
        )
