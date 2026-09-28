########################################################################################
#
#    Author: Miika Nissi
#    Copyright 2026 Miika Nissi (https://miikanissi.com)
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

"""Validated conversion options shared by the Zebrafy converters."""

# 1. Standard library imports:
import dataclasses

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy._validation import Validated, validated_field
from zebrafy.graphic_field import (
    GraphicField,
    format_field,
    invert_monochrome,
    string_line_break_field,
)

ROTATIONS = (0, 90, 180, 270)

# Image.rotate() turns counter-clockwise and crops non-square images, so rotate
# clockwise with lossless transposes instead, matching PDFium page rotation.
_CLOCKWISE_TRANSPOSE = {
    90: Image.Transpose.ROTATE_270,
    180: Image.Transpose.ROTATE_180,
    270: Image.Transpose.ROTATE_90,
}


@dataclasses.dataclass(kw_only=True)
class GraphicOptions(Validated):
    """
    Options for converting an image into a ZPL graphic field.

    :param format: ZPL graphic field format, defaults to ``"ASCII"``:

        - ``"ASCII"``: ASCII hexadecimal - most compatible (default)
        - ``"B64"``: Base64 binary
        - ``"Z64"``: LZ77 / Zlib compressed base64 binary - best compression
    :param invert: Invert the black and white in the resulting image, defaults to \
    ``False``
    :param dither: Dither the pixels instead of a hard limit on black and white, \
    defaults to ``True``
    :param threshold: Black pixel threshold for an undithered image (``0-255``), \
    defaults to ``128``
    :param width: Width of the image in the resulting ZPL. If ``0``, use the \
    original width, defaults to ``0``
    :param height: Height of the image in the resulting ZPL. If ``0``, use the \
    original height, defaults to ``0``
    :param pos_x: X position of the image on the resulting ZPL, defaults to ``0``
    :param pos_y: Y position of the image on the resulting ZPL, defaults to ``0``
    :param rotation: Clockwise rotation in degrees ``0``, ``90``, ``180``, or \
    ``270``, defaults to ``0``
    :param string_line_break: Number of characters in graphic field content after \
    which a new line is added, defaults to ``None``
    :param complete_zpl: Return a complete ZPL label with ``^XA`` and ``^XZ``. \
    Otherwise return only the graphic field, defaults to ``True``
    """

    format: str = format_field()
    invert: bool = validated_field(False, "Invert", bool)
    dither: bool = validated_field(True, "Dither", bool)
    threshold: int = validated_field(128, "Threshold", int, minimum=0, maximum=255)
    width: int = validated_field(0, "Width", int, minimum=0)
    height: int = validated_field(0, "Height", int, minimum=0)
    pos_x: int = validated_field(0, "X position", int, minimum=0)
    pos_y: int = validated_field(0, "Y position", int, minimum=0)
    rotation: int = validated_field(0, "Rotation", int, choices=ROTATIONS)
    string_line_break: int | None = string_line_break_field()
    complete_zpl: bool = validated_field(True, "Complete ZPL", bool)

    def _to_monochrome(
        self, pil_image: Image.Image, rotate: bool = True
    ) -> Image.Image:
        """
        Convert an image into a black and white image ready for a graphic field.

        :param pil_image: Image to convert.
        :param rotate: Apply the ``rotation`` option, defaults to ``True``.
        :returns: A mode ``"1"`` image.
        """
        # Transparent pixels would otherwise take the colour stored under them,
        # which is usually black, so place the image on a white background first.
        if pil_image.has_transparency_data:
            rgba = pil_image.convert("RGBA")
            background = Image.new("RGBA", rgba.size, "white")
            pil_image = Image.alpha_composite(background, rgba)

        if rotate and self.rotation:
            pil_image = pil_image.transpose(_CLOCKWISE_TRANSPOSE[self.rotation])

        if self.width or self.height:
            pil_image = pil_image.resize(
                (self.width or pil_image.width, self.height or pil_image.height)
            )

        if self.dither:
            pil_image = pil_image.convert("1")
        else:
            threshold = self.threshold
            pil_image = pil_image.convert("L").point(
                lambda x: 255 if x > threshold else 0, mode="1"
            )

        if self.invert:
            pil_image = invert_monochrome(pil_image)

        return pil_image

    def _get_field(self, pil_image: Image.Image, pos_x: int, pos_y: int) -> str:
        """
        Get a positioned graphic field for a black and white image.

        :param pil_image: A mode ``"1"`` image.
        :param pos_x: X position of the graphic field.
        :param pos_y: Y position of the graphic field.
        :returns: ZPL field origin followed by the graphic field.
        """
        graphic_field = GraphicField(
            pil_image, format=self.format, string_line_break=self.string_line_break
        )
        return f"^FO{pos_x},{pos_y}" + graphic_field.get_graphic_field()

    def _get_label(self, body: str) -> str:
        """
        Wrap ZPL commands into a complete label.

        :param body: ZPL commands, each line ending in a line break.
        :returns: A complete ZPL label.
        """
        return "^XA\n" + body + "^XZ\n"
