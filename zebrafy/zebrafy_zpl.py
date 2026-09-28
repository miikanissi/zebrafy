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
import io
import operator
import re
import sys
import zlib

# 2. Known third party imports:
from PIL import Image
from pypdfium2 import PdfDocument, PdfImage, PdfMatrix

# 3. Local imports in the relative form:
from zebrafy.crc import CRC

GF_MATCHER = re.compile(
    r"\^GF([ABC]*),([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),(.*?(?=\^FS))\^FS",
    re.DOTALL,
)
HEX_MATCHER = re.compile(r"[0-9A-Fa-f]*")

if sys.version_info >= (3, 9):
    DimensionsType = tuple[int, int]
    ToImagesType = list[Image.Image]
else:
    from typing import List, Tuple

    DimensionsType = Tuple[int, int]
    ToImagesType = List[Image.Image]


class ZebrafyZPL:
    """
    Convert Zebra Programming Language (ZPL) graphic fields to PDF and images.

    :param zpl_data: A valid ZPL string.
    """

    def __init__(self, zpl_data: str):
        self.zpl_data = zpl_data

    zpl_data = property(operator.attrgetter("_zpl_data"))

    @zpl_data.setter
    def zpl_data(self, d):
        if d is None:
            raise ValueError("ZPL data cannot be empty.")
        if not isinstance(d, str):
            raise TypeError(
                f"ZPL data must be a valid ZPL string. {type(d)} was given."
            )
        self._zpl_data = d

    def _match_dimensions(self, total: int, width: int) -> DimensionsType:
        """
        Get image dimensions from ZPL graphic field.

        :param total: Total number of bytes comprising the graphic format.
        :param width: Total number of bytes comprising one row of the data.
        :returns: A tuple of integers containing the width and height of the \
        graphic field image.
        """
        return int(width * 8), int(total / width)

    def _decompress_ascii(self, data: str, bytes_per_row: int) -> bytes:
        """
        Decompress ZPL ASCII hexadecimal graphic field data.

        ZPL compresses ASCII hexadecimal data with the following characters:

            - ``G`` to ``Y``: Repeat the following hexadecimal character 1 to 19 \
            times
            - ``g`` to ``z``: Repeat the following hexadecimal character 20 to 400 \
            times, in steps of 20. Counts can be combined, e.g. ``hG`` is 41.
            - ``,``: Fill the rest of the row with zeros
            - ``!``: Fill the rest of the row with ones
            - ``:``: Repeat the previous row

        :param data: ZPL ASCII hexadecimal graphic field data, compressed or not.
        :param bytes_per_row: Total number of bytes comprising one row of the data.
        :returns: Decompressed graphic field data bytes.
        """
        if HEX_MATCHER.fullmatch(data):
            return bytes.fromhex(data)

        row_length = bytes_per_row * 2
        rows = []
        row = ""
        repeat = 0
        for char in data:
            if "G" <= char <= "Y":
                repeat += ord(char) - ord("F")
            elif "g" <= char <= "z":
                repeat += (ord(char) - ord("f")) * 20
            elif char in ",!":
                rows.append(row.ljust(row_length, "0" if char == "," else "F"))
                row = ""
            elif char == ":":
                if row or not rows:
                    raise ValueError(
                        "Invalid row repeat in ZPL graphic field (^GF) data."
                    )
                rows.append(rows[-1])
            elif char in "0123456789ABCDEFabcdef":
                row += char * max(repeat, 1)
                repeat = 0
                while len(row) >= row_length:
                    rows.append(row[:row_length])
                    row = row[row_length:]
            else:
                raise ValueError(
                    f"Invalid character {char!r} in ZPL graphic field (^GF) data."
                )
        if row:
            rows.append(row.ljust(row_length, "0"))

        return bytes.fromhex("".join(rows))

    def to_images(self) -> ToImagesType:
        """
        Convert Zebra Programming Language (ZPL) graphic fields to PIL Image objects.

        :returns: A list containing PIL Images converted from ZPL graphic fields.
        """
        matches = GF_MATCHER.findall(self._zpl_data)
        if not matches:
            raise ValueError("Could not find a graphic field (^GF) in ZPL content.")

        pil_images = []
        for match in matches:
            bytes_per_row = int(match[3])
            width, height = self._match_dimensions(int(match[2]), bytes_per_row)
            compression_type = match[0].upper()
            # Remove line breaks, e.g. from string_line_break
            data_bytes = "".join(match[4].split())

            if compression_type != "A":
                raise ValueError(
                    "No valid compression type found in ZPL graphic field (^GF). Only"
                    " ASCII is supported (^GFA)."
                )

            if data_bytes.startswith(":Z64") or data_bytes.startswith(":B64"):
                zlib_compressed = True if data_bytes.startswith(":Z64") else False
                crc = data_bytes[-4:]
                data_bytes = data_bytes[5:-5]

                # Validate CRC to ensure data bytes are valid and unchanged
                if crc != CRC(data_bytes.encode("ascii")).get_crc_hex_string():
                    raise ValueError("CRC mismatch.")

                data_bytes = base64.b64decode(data_bytes)

                # Decompress LZ77 / Zlib compression
                if zlib_compressed:
                    data_bytes = zlib.decompress(data_bytes)

            else:
                data_bytes = self._decompress_ascii(data_bytes, bytes_per_row)

            pil_image = Image.frombytes("1", (width, height), data_bytes)
            pil_images.append(pil_image)

        return pil_images

    def to_pdf(self) -> bytes:
        """
        Convert Zebra Programming Language (ZPL) graphic fields to PDF.

        :returns: PDF bytes from ZPL graphic fields.
        """
        pil_images = self.to_images()
        pdf = PdfDocument.new()

        for pil_image in pil_images:
            # Save PIL Image as JPEG bytes for pypdfium2 to convert into PDF.
            image_bytes = io.BytesIO()
            pil_image.save(image_bytes, format="JPEG")

            # Load image bytes into PDF Image using pypdfium2 and get size
            image = PdfImage.new(pdf)
            image.load_jpeg(image_bytes)
            width, height = image.get_px_size()
            matrix = PdfMatrix().scale(width, height)
            image.set_matrix(matrix)

            # Save PDF Image on a new page on the PDF.
            page = pdf.new_page(width, height)
            page.insert_obj(image)
            page.gen_content()

        pdf_bytes = io.BytesIO()
        # pypdfium2.PdfDocument save method not to be confused with PIL.Image save
        pdf.save(pdf_bytes)

        return pdf_bytes.getvalue()
