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
from io import BytesIO
from itertools import chain

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .graphic_field import GraphicField

GF_MATCHER = re.compile(
    r"\^GF([ABC]*),([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),(.*?(?=\^FS))\^FS"
)
A_COMPRESSION_PARAMS = ["A", "ASCII"]
B_COMPRESSION_PARAMS = ["B", "BINARY", "B64", "BASE64"]
C_COMPRESSION_PARAMS = ["C", "COMPRESSED-BINARY", "Z64", "LZ77"]


class Zebrafy:
    """
    Provides methods for converting Zebra Programming Language (ZPL) to and from PDF, \
    and images.

    :param int zid: A Zebrafy object identifier
    :param zpl: The output data of file conversion
    """

    def __init__(self, data, zid=None):
        self.data = data
        if zid is None:
            zid = 1
        self.zid = zid

    @staticmethod
    def _match_dimensions(match):
        total = int(match.group(3))
        width = int(match.group(4))

        return int(width * 8), int(total / width)

    @staticmethod
    def _validate_params(image, compression_type):
        if not isinstance(image, bytes):
            raise ValueError("Image must be a valid bytes object.")

        if not isinstance(compression_type, str):
            raise ValueError("Compression type must be a string.")

        if compression_type.upper() not in chain(
            A_COMPRESSION_PARAMS, B_COMPRESSION_PARAMS, C_COMPRESSION_PARAMS
        ):
            raise ValueError(
                (
                    "Invalid parameter for compression type. Valid options include:"
                    " {valids}."
                ).format(
                    valids=chain(
                        A_COMPRESSION_PARAMS, B_COMPRESSION_PARAMS, C_COMPRESSION_PARAMS
                    )
                )
            )

    @staticmethod
    def image_to_zpl(image, compression_type="A"):
        # Validate all input parameters
        Zebrafy._validate_params(image, compression_type)

        # Open and convert image to grayscale
        image = Image.open(BytesIO(image)).convert("1")

        graphic_field = GraphicField(image, compression_type=compression_type.upper())

        zpl_result = "^XA\n" + graphic_field.graphic_field + "\n^XZ\n"

        return zpl_result

    @staticmethod
    def zpl_to_image(zpl):
        match = GF_MATCHER.search(zpl)
        if not match:
            raise ValueError("Could not find an image in ZPL content.")

        width, height = Zebrafy._match_dimensions(match)
        compression_type = match.group(1)
        image_string = match.group(5)

        if compression_type.upper() in A_COMPRESSION_PARAMS:
            image_bytes = bytes.fromhex(image_string)
        elif compression_type.upper() in B_COMPRESSION_PARAMS:
            image_bytes = base64.b64decode(image_string)

        image = Image.frombytes("1", (width, height), image_bytes)

        return image
