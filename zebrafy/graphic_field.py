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
import dataclasses
import zlib
from typing import Any

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy._validation import Validated, validated_field
from zebrafy.crc import CRC

FORMATS = ("ASCII", "B64", "Z64")


def format_field() -> Any:
    """Return a validated ``format`` dataclass field."""
    return validated_field("ASCII", "Format", str, choices=FORMATS, normalize=str.upper)


def string_line_break_field() -> Any:
    """Return a validated ``string_line_break`` dataclass field."""
    return validated_field(None, "String line break", int, optional=True, minimum=1)


def invert_monochrome(pil_image: Image.Image) -> Image.Image:
    """
    Invert a black and white (mode ``"1"``) image.

    Any nonzero pixel counts as white, the same as in ``Image.tobytes()``.

    :param pil_image: A mode ``"1"`` image.
    :returns: The inverted image.
    """
    return pil_image.point(lambda v: 0 if v else 255)


@dataclasses.dataclass
class GraphicField(Validated):
    """
    Converts a PIL image to Zebra Programming Language (ZPL) graphic field data.

    Black pixels are printed. Images that are not black and white (mode ``"1"``) \
    are dithered to black and white first.

    :param PIL.Image.Image pil_image: An instance of a PIL Image.
    :param format: ZPL format parameter that accepts the following values, \
    defaults to ``"ASCII"``:

        - ``"ASCII"``: ASCII hexadecimal - most compatible (default)
        - ``"B64"``: Base64 binary
        - ``"Z64"``: LZ77 / Zlib compressed base64 binary - best compression
    :param string_line_break: Number of characters in graphic field content after \
    which a new line is added, defaults to ``None``.
    """

    pil_image: Image.Image = validated_field(
        dataclasses.MISSING,
        "Image",
        Image.Image,
        type_name="a valid PIL.Image.Image object",
        kw_only=False,
        repr=False,
    )
    format: str = format_field()
    string_line_break: int | None = string_line_break_field()

    def _get_image_bytes(self) -> bytes:
        """
        Get the image as packed rows of bits where ``1`` is a printed dot.

        :returns: Image bytes.
        """
        pil_image = self.pil_image
        if pil_image.mode != "1":
            pil_image = pil_image.convert("1")
        # PIL stores black as 0, ZPL prints 1. Inverting the image instead of the
        # bytes keeps the padding at the end of each row white.
        return invert_monochrome(pil_image).tobytes()

    def _get_binary_byte_count(self) -> int:
        """
        Get binary byte count.

        This is the total number of bytes to be transmitted for the total image or
        the total number of bytes that follow parameter bytes_per_row. For ASCII \
        download, the parameter should match parameter graphic_field_count. \
        Out-of-range values are set to the nearest limit.

        :returns: Binary byte count
        """
        if self.format == "ASCII":
            return self._get_graphic_field_count()
        return len(self._get_encoded_data_string())

    def _get_bytes_per_row(self) -> int:
        """
        Get bytes per row.

        This is the number of bytes in the image data that comprise one row of the \
        image.

        :returns: Bytes per row
        """
        return (self.pil_image.size[0] + 7) // 8

    def _get_graphic_field_count(self) -> int:
        """
        Get graphic field count.

        This is the total number of bytes comprising the image data (width x height).

        :returns: Graphic field count.
        """
        return self._get_bytes_per_row() * self.pil_image.size[1]

    def _get_encoded_data_string(self) -> str:
        """
        Get graphic field data string depending on format, without line breaks.

        :returns: Graphic field data string depending on format.
        """
        image_bytes = self._get_image_bytes()

        if self.format == "ASCII":
            return image_bytes.hex().upper()

        # Format B64 and Z64: Convert (LZ77 / Zlib compressed) bytes to base64 and
        # add header + CRC
        if self.format == "Z64":
            image_bytes = zlib.compress(image_bytes)
        encoded = base64.b64encode(image_bytes)
        return ":{format}:{encoded_data}:{crc}".format(
            format=self.format,
            encoded_data=encoded.decode("ascii"),
            crc=CRC(encoded).get_crc_hex_string(),
        )

    def _get_data_string(self) -> str:
        """
        Get graphic field data string depending on format.

        :returns: Graphic field data string depending on format, split into lines \
        if ``string_line_break`` is set.
        """
        data_string = self._get_encoded_data_string()
        if self.string_line_break:
            data_string = "\n".join(
                data_string[i : i + self.string_line_break]
                for i in range(0, len(data_string), self.string_line_break)
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
