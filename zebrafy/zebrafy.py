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
import re
from io import BytesIO

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .graphic_field import GraphicField

GFA_MATCHER = re.compile(
    r"\^GFA,([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),([^\^]+)\^FS"
)


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
        total = int(match.group(2))
        width = int(match.group(3))
        return int(width * 8), int(total / width)

    @staticmethod
    def image_to_zpl(image):
        # Open and convert image to grayscale
        image = Image.open(BytesIO(image))
        image_bw = image.convert("1")

        graphic_field = GraphicField(image_bw, compression_type="A")

        zpl_result = "^XA\n" + graphic_field.graphic_field + "\n^XZ\n"

        return zpl_result

    @staticmethod
    def zpl_to_image(zpl):
        match = GFA_MATCHER.search(zpl)
        if not match:
            raise ValueError("Could not find an image in ZPL content.")

        width, height = Zebrafy._match_dimensions(match)

        image_bytes = bytes.fromhex(match.group(4))
        image = Image.frombytes("1", (width, height), image_bytes)

        return image
