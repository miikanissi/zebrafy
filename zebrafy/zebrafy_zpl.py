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
import re
import zlib

# 2. Known third party imports:
from PIL import Image
from pypdfium2 import PdfDocument, PdfImage, PdfMatrix

# 3. Local imports in the relative form:
from .crc import CRC

GF_MATCHER = re.compile(
    r"\^GF([ABC]*),([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),(.*?(?=\^FS))\^FS"
)


class ZebrafyZPL:
    """
    Provides a method for converting Zebra Programming Language (ZPL) graphic fields \
    to PDF and images.

    :param str zpl_data: A valid ZPL string.
    """

    def __init__(self, zpl_data, zid=None):
        self._zpl_data = zpl_data

    def _match_dimensions(self, total, width):
        """
        Get image dimensions from ZPL graphic field.

        :param int total: Total number of bytes comprising the graphic format.
        :param int width: Total number of bytes comprising one row of the data.
        :returns tuple: A tuple of integers containing the width and height of the \
        graphic field image.
        """

        return int(width * 8), int(total / width)

    def to_images(self):
        """
        Converts Zebra Programming Language (ZPL) graphic fields to PIL Image objects.

        :returns list: A list containing PIL Images converted from ZPL graphic fields.
        """
        matches = GF_MATCHER.findall(self._zpl_data)
        if not matches:
            raise ValueError("Could not find a graphic field (^GF) in ZPL content.")

        pil_images = []
        for match in matches:
            width, height = self._match_dimensions(int(match[2]), int(match[3]))
            compression_type = match[0].upper()
            data_bytes = match[4]

            # Compression types B and C have base64 encoded data
            if (compression_type == "C" and data_bytes.startswith(":Z64")) or (
                compression_type == "B" and data_bytes.startswith(":B64")
            ):
                crc = data_bytes[-4:]
                data_bytes = data_bytes[5:-5]

                # Validate CRC to ensure data bytes are valid and unchanged
                if crc != CRC(data_bytes.encode("ascii")).get_crc_hex_string():
                    raise ValueError("CRC mismatch.")

                data_bytes = base64.b64decode(data_bytes)

                # Compression type C: decompress LZ77 / Zlib compression
                if compression_type == "C":
                    data_bytes = zlib.decompress(data_bytes)

            # Compression type A contains ASCII hexadecimal data
            elif compression_type == "A":
                data_bytes = bytes.fromhex(data_bytes)

            else:
                raise ValueError(
                    "No valid compression type found in ZPL graphic field (^GF)."
                )

            pil_image = Image.frombytes("1", (width, height), data_bytes)
            pil_images.append(pil_image)

        return pil_images

    def to_pdf(self):
        """
        Converts Zebra Programming Language (ZPL) graphic fields to PDF.

        :returns bytes: PDF bytes from ZPL graphic fields.
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
            width, height = image.get_size()
            matrix = PdfMatrix().scale(width, height)
            image.set_matrix(matrix)

            # Save PDF Image on a new page on the PDF.
            page = pdf.new_page(width, height)
            page.insert_obj(image)
            page.gen_content()

        pdf_bytes = io.BytesIO()
        # pypdfium2.PdfDocument save method not to be confused with PIL.Image save method
        pdf.save(pdf_bytes)

        return pdf_bytes.getvalue()
