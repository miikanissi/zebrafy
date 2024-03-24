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
import operator
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
    :param invert: Invert the black and white in resulting image, defaults to ``False``
    :param dither: Dither the pixels instead of hard limit on black and white, \
    defaults to ``False``
    :param threshold: Black pixel threshold for undithered image (``0-255``), defaults \
    to ``128``
    :param width: Width of the image in the resulting ZPL. If ``0``, use default image \
    width, defaults to ``0``
    :param height: Height of the image in the resulting ZPL. If ``0``, use default \
    image height, defaults to ``0``
    :param pos_x: X position of the image on the resulting ZPL, defaults to ``0``
    :param pos_y: Y position of the image on the resulting ZPL, defaults to ``0``
    :param complete_zpl: Return a complete ZPL with header and footer included. \
    Otherwise return only the graphic field, defaults to ``True``

    .. deprecated:: 1.1.0
        The `compression_type` parameter is deprecated in favor of `format` and will \
        be removed in version 2.0.0.
    """

    def __init__(
        self,
        image: Union[bytes, Image.Image],
        compression_type: str = None,
        format: str = None,
        invert: bool = None,
        dither: bool = None,
        threshold: int = None,
        width: int = None,
        height: int = None,
        pos_x: int = None,
        pos_y: int = None,
        complete_zpl: bool = None,
    ):
        self.image = image
        if format is None:
            if compression_type is None:
                format = "ASCII"
            else:
                format = self._compression_type_to_format(compression_type)
        self.format = format.upper()
        if invert is None:
            invert = False
        self.invert = invert
        if dither is None:
            dither = True
        self.dither = dither
        if threshold is None:
            threshold = 128
        self.threshold = threshold
        if width is None:
            width = 0
        self.width = width
        if height is None:
            height = 0
        self.height = height
        if pos_x is None:
            pos_x = 0
        self.pos_x = pos_x
        if pos_y is None:
            pos_y = 0
        self.pos_y = pos_y
        if complete_zpl is None:
            complete_zpl = True
        self.complete_zpl = complete_zpl

    image = property(operator.attrgetter("_image"))

    @image.setter
    def image(self, i):
        if not i:
            raise ValueError("Image cannot be empty.")
        if not isinstance(i, bytes) and not isinstance(i, Image.Image):
            raise TypeError(
                "Image must be a valid bytes object or PIL.Image.Image object."
                " {param_type} was given.".format(param_type=type(i))
            )
        self._image = i

    format = property(operator.attrgetter("_format"))

    @format.setter
    def format(self, f):
        if f is None:
            raise ValueError("Format cannot be empty.")
        if not isinstance(f, str):
            raise TypeError(
                "Format must be a valid string. {param_type} was given.".format(
                    param_type=type(f)
                )
            )
        if f not in ["ASCII", "B64", "Z64"]:
            raise ValueError(
                'Format must be "ASCII","B64", or "Z64". {param} was given.'.format(
                    param=f
                )
            )
        self._format = f

    invert = property(operator.attrgetter("_invert"))

    @invert.setter
    def invert(self, i):
        if i is None:
            raise ValueError("Invert cannot be empty.")
        if not isinstance(i, bool):
            raise TypeError(
                "Invert must be a boolean. {param_type} was given.".format(
                    param_type=type(i)
                )
            )
        self._invert = i

    dither = property(operator.attrgetter("_dither"))

    @dither.setter
    def dither(self, d):
        if d is None:
            raise ValueError("Dither cannot be empty.")
        if not isinstance(d, bool):
            raise TypeError(
                "Dither must be a boolean. {param_type} was given.".format(
                    param_type=type(d)
                )
            )
        self._dither = d

    threshold = property(operator.attrgetter("_threshold"))

    @threshold.setter
    def threshold(self, t):
        if t is None:
            raise ValueError("Threshold cannot be empty.")
        if not isinstance(t, int):
            raise TypeError(
                "Threshold must be an integer. {param_type} was given.".format(
                    param_type=type(t)
                )
            )
        if t < 0 or t > 255:
            raise ValueError(
                "Threshold must be within 0 to 255. {param} was given.".format(param=t)
            )
        self._threshold = t

    width = property(operator.attrgetter("_width"))

    @width.setter
    def width(self, w):
        if w is None:
            raise ValueError("Width cannot be empty.")
        if not isinstance(w, int):
            raise TypeError(
                "Width must be an integer. {param_type} was given.".format(
                    param_type=type(w)
                )
            )
        self._width = w

    height = property(operator.attrgetter("_height"))

    @height.setter
    def height(self, h):
        if h is None:
            raise ValueError("Height cannot be empty.")
        if not isinstance(h, int):
            raise TypeError(
                "Height must be an integer. {param_type} was given.".format(
                    param_type=type(h)
                )
            )
        self._height = h

    pos_x = property(operator.attrgetter("_pos_x"))

    @pos_x.setter
    def pos_x(self, x):
        if x is None:
            raise ValueError("X position cannot be empty.")
        if not isinstance(x, int):
            raise TypeError(
                "X position must be an integer. {param_type} was given.".format(
                    param_type=type(x)
                )
            )
        self._pos_x = x

    pos_y = property(operator.attrgetter("_pos_y"))

    @pos_y.setter
    def pos_y(self, y):
        if y is None:
            raise ValueError("Y position cannot be empty.")
        if not isinstance(y, int):
            raise TypeError(
                "Y position must be an integer. {param_type} was given.".format(
                    param_type=type(y)
                )
            )
        self._pos_y = y

    complete_zpl = property(operator.attrgetter("_complete_zpl"))

    @complete_zpl.setter
    def complete_zpl(self, c):
        if c is None:
            raise ValueError("Complete ZPL cannot be empty.")
        if not isinstance(c, bool):
            raise TypeError(
                "Complete ZPL must be a boolean. {param_type} was given.".format(
                    param_type=type(c)
                )
            )
        self._complete_zpl = c

    def _compression_type_to_format(self, compression_type: str) -> str:
        """
        Convert deprecated compression type to format.
        """
        if compression_type.upper() == "A":
            return "ASCII"
        elif compression_type.upper() == "B":
            return "B64"
        elif compression_type.upper() == "C":
            return "Z64"

    def to_zpl(self) -> str:
        """
        Converts PIL Image or image bytes to Zebra Programming Language (ZPL).

        :returns: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        if isinstance(self._image, bytes):
            pil_image = Image.open(BytesIO(self._image))
        else:
            pil_image = self._image

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

        graphic_field = GraphicField(pil_image, format=self._format)

        # Set graphic field position based on given parameters
        pos = "^FO0,0"
        if self._pos_x or self._pos_y:
            pos = "^FO{x},{y}".format(x=self._pos_x, y=self._pos_y)

        # Return complete ZPL with header and footer or only the graphic field based on
        # given parameters
        if self._complete_zpl:
            return "^XA\n" + pos + graphic_field.get_graphic_field() + "\n^XZ\n"

        return pos + graphic_field.get_graphic_field()
