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
from io import BytesIO

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .graphic_field import GraphicField


class ZebrafyImage:
    """
    Provides a method for converting image bytes to Zebra Programming Language (ZPL).

    :param bytes image_bytes: Image as a bytes object.
    :param str compression_type: ZPL compression type parameter that accepts the \
    following values:
        - "A": ASCII hexadecimal - most compatible
        - "B": Base64 binary
        - "C": LZ77 / Zlib compressed base64 binary - best compression
    (Default: ``"A"``)
    """

    def __init__(self, image_bytes, compression_type=None):
        self.image_bytes = image_bytes
        if compression_type is None:
            compression_type = "a"
        self.compression_type = compression_type.upper()

    def to_zpl(self):
        """
        Converts image bytes to Zebra Programming Language (ZPL).

        :returns str: A complete ZPL file string which can be sent to a ZPL compatible \
        printer.
        """
        # Open and convert image to grayscale
        image = Image.open(BytesIO(self.image_bytes)).convert("1")

        graphic_field = GraphicField(image, compression_type=self.compression_type)
        zpl_result = "^XA\n" + graphic_field.get_graphic_field() + "\n^XZ\n"

        return zpl_result
