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


GFA_MATCHER = re.compile(
    r"\^GFA,([1-9][0-9]*),([1-9][0-9]*),([1-9][0-9]*),([^\^]+)\^FS"
)


class Zebrafy(object):
    """
    Provides methods for converting Zebra Programming Language (ZPL) to and from PDF,
    HTML, and images.

    :param data: The output data of file conversion
    """

    def __init__(self, data):
        self.data = data

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

        # Get image size and calculate new width
        width, height = image.size
        width = int((width + 7) / 8)
        total = int(width * height)

        # Convert image to hex
        image_hex = image_bw.tobytes().hex()
        zpl_body = image_hex

        zpl_header = "^GFA,{byte_count},{graphic_count},{width},".format(
            byte_count=len(zpl_body), graphic_count=total, width=width
        )
        zpl_footer = "^FS"

        zpl_result = (
            "^XA\n" + zpl_header + "\n" + zpl_body + "\n" + zpl_footer + "\n^XZ\n"
        )

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
