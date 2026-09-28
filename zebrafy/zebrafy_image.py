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
import dataclasses
from io import BytesIO

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy._validation import validated_field
from zebrafy.options import GraphicOptions


@dataclasses.dataclass
class ZebrafyImage(GraphicOptions):
    """
    Convert a PIL Image or image bytes into Zebra Programming Language (ZPL).

    Transparent pixels are treated as white.

    :param image: Image as a PIL Image or bytes object.

    All other parameters are keyword-only and described in \
    :class:`~zebrafy.options.GraphicOptions`.
    """

    image: bytes | Image.Image = validated_field(
        dataclasses.MISSING,
        "Image",
        (bytes, Image.Image),
        type_name="a valid bytes object or PIL.Image.Image object",
        kw_only=False,
        repr=False,
    )

    def to_zpl(self) -> str:
        """
        Convert PIL Image or image bytes into Zebra Programming Language (ZPL).

        :returns: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        pil_image: Image.Image
        if isinstance(self.image, bytes):
            pil_image = Image.open(BytesIO(self.image))
        else:
            pil_image = self.image

        pil_image = self._to_monochrome(pil_image)
        graphic_field = self._get_field(pil_image, self.pos_x, self.pos_y)

        if self.complete_zpl:
            return self._get_label(graphic_field + "\n")
        return graphic_field
