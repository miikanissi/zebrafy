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
from typing import Union

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from .graphic_field import GraphicField


class ZebrafyImage:
    """
    Provides a method for converting PIL Image or image bytes to Zebra Programming \
    Language (ZPL).

    :param image: Image as a PIL Image or bytes object.
    :param compression_type: ZPL compression type parameter that accepts the \
    following values, defaults to "A":

        - "A": ASCII hexadecimal - most compatible (default)
        - "B": Base64 binary
        - "C": LZ77 / Zlib compressed base64 binary - best compression
    :param invert: Invert the black and white in resulting image, defaults to False
    :param dither: Dither the pixels instead of hard limit on black and white, \
    defaults to False
    :param threshold: Black pixel threshold for undithered image (0-255), defaults \
    to 128
    :param width: Width of the image in the resulting ZPL. If 0, use default image \
    width, defaults to 0
    :param height: Height of the image in the resulting ZPL. If 0, use default \
    image height, defaults to 0
    :param pos_x: X position of the image on the resulting ZPL, defaults to 0
    :param pos_y: Y position of the image on the resulting ZPL, defaults to 0
    :param complete_zpl: Return a complete ZPL with header and footer included. \
    Otherwise return only the graphic field, defaults to True
    """

    def __init__(
        self,
        image: Union[bytes, Image.Image],
        compression_type: str = None,
        invert: bool = None,
        dither: bool = None,
        threshold: int = None,
        width: int = None,
        height: int = None,
        pos_x: int = None,
        pos_y: int = None,
        complete_zpl: bool = None,
    ):
        self._image = image
        if compression_type is None:
            compression_type = "a"
        self._compression_type = compression_type.upper()
        if invert is None:
            invert = False
        self._invert = invert
        if dither is None:
            dither = True
        self._dither = dither
        if threshold is None:
            threshold = 128
        self._threshold = threshold
        if width is None:
            width = 0
        self._width = width
        if height is None:
            height = 0
        self._height = height
        if pos_x is None:
            pos_x = 0
        self._pos_x = pos_x
        if pos_y is None:
            pos_y = 0
        self._pos_y = pos_y
        if complete_zpl is None:
            complete_zpl = True
        self._complete_zpl = complete_zpl

    def to_zpl(self) -> str:
        """
        Converts PIL Image or image bytes to Zebra Programming Language (ZPL).

        :returns: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        if isinstance(self._image, Image.Image):
            pil_image = self._image
        elif isinstance(self._image, bytes):
            pil_image = Image.open(BytesIO(self._image))
        else:
            raise ValueError(
                (
                    "Cannot load image from {source} - not a PIL Image or bytes object."
                ).format(source=self._image)
            )

        # Resize image if width or height defined in parameters
        if self._width or self._height:
            width, height = pil_image.size
            if self._width:
                width = self._width
            if self._height:
                height = self._height
            pil_image = pil_image.resize((width, height))

        # Convert image to black and white based on given parameters
        if self._dither:
            pil_image = pil_image.convert("1")
            if self._invert:
                pil_image = pil_image.point(lambda x: 255 - x)
        else:
            pil_image = pil_image.convert("L")
            pil_image = pil_image.point(
                lambda x: (
                    (0 if self._invert else 255)
                    if x > self._threshold
                    else (255 if self._invert else 0)
                ),
                mode="1",
            )

        graphic_field = GraphicField(pil_image, compression_type=self._compression_type)

        # Set graphic field position based on given parameters
        pos = "^FO0,0"
        if self._pos_x or self._pos_y:
            pos = "^FO{x},{y}".format(x=self._pos_x, y=self._pos_y)

        # Return complete ZPL with header and footer or only the graphic field based on
        # given parameters
        if self._complete_zpl:
            return "^XA\n" + pos + graphic_field.get_graphic_field() + "\n^XZ\n"

        return pos + graphic_field.get_graphic_field()
