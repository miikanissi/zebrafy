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

# 2. Known third party imports:
from pypdfium2 import PdfDocument

# 3. Local imports in the relative form:
from .zebrafy_image import ZebrafyImage


class ZebrafyPDF:
    """
    Provides a method for converting PDFs to Zebra Programming Language (ZPL).

    :param bytes pdf_bytes: PDF as a bytes object.
    :param str compression_type: ZPL compression type parameter that accepts the \
    following values:
        - "A": ASCII hexadecimal - most compatible
        - "B": Base64 binary
        - "C": LZ77 / Zlib compressed base64 binary - best compression
    (Default: ``"A"``)
    :param bool inverse: Invert the black and white in the resulting PDF
    (Default: ``False``)
    :param bool dither: Dither the pixels instead of hard limit on black and white
    (Default: ``True``)
    :param int threshold: Black pixel threshold for undithered PDF (0-255)
    (Default: ``128``)
    :param bool complete_zpl: Return a complete ZPL with header and footer included. \
    Otherwise return only the graphic field.
    (Default: ``True``)
    """

    def __init__(
        self,
        pdf_bytes,
        compression_type=None,
        inverse=None,
        dither=None,
        threshold=None,
        complete_zpl=None,
    ):
        self._pdf_bytes = pdf_bytes
        if compression_type is None:
            compression_type = "a"
        self._compression_type = compression_type.upper()
        if inverse is None:
            inverse = False
        self._inverse = inverse
        if dither is None:
            dither = True
        self._dither = dither
        if threshold is None:
            threshold = 128
        self._threshold = threshold
        if complete_zpl is None:
            complete_zpl = True
        self._complete_zpl = complete_zpl

    def to_zpl(self):
        """
        Converts PDF bytes to Zebra Programming Language (ZPL).

        :returns str: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        # Open and convert image to grayscale
        pdf = PdfDocument(self._pdf_bytes)
        graphic_fields = ""
        for page in pdf:
            bitmap = page.render(scale=1, rotation=0)
            pil_image = bitmap.to_pil()
            zebrafy_image = ZebrafyImage(
                pil_image,
                compression_type=self._compression_type,
                inverse=self._inverse,
                dither=self._dither,
                threshold=self._threshold,
                complete_zpl=False,
            )
            graphic_fields += zebrafy_image.to_zpl() + "\n"

        if self._complete_zpl:
            return "^XA\n" + graphic_fields + "^XZ\n"

        return graphic_fields
