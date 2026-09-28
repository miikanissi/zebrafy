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

# 2. Known third party imports:
from PIL import Image
from pypdfium2 import PdfDocument

# 3. Local imports in the relative form:
from zebrafy._validation import validated_field
from zebrafy.options import GraphicOptions


@dataclasses.dataclass
class ZebrafyPDF(GraphicOptions):
    """
    Provides a method for converting PDFs to Zebra Programming Language (ZPL).

    :param pdf_bytes: PDF as a bytes object.
    :param dpi: Pixels per PDF canvas unit. This defines the resolution scaling of \
    the image (<72: compress, >72: stretch), defaults to ``72``
    :param split_pages: Put each PDF page on a label of its own. Otherwise the pages \
    are stacked vertically on a single label, defaults to ``True``

    All other parameters are keyword-only and described in \
    :class:`~zebrafy.options.GraphicOptions`.
    """

    pdf_bytes: bytes = validated_field(
        dataclasses.MISSING,
        "PDF",
        bytes,
        type_name="a valid bytes object",
        kw_only=False,
        repr=False,
    )
    dpi: int = validated_field(72, "DPI", int, minimum=1, maximum=720)
    split_pages: bool = validated_field(True, "Split pages", bool)

    def _render_pages(self) -> list[Image.Image]:
        """
        Render each PDF page into a black and white image.

        :returns: A list of mode ``"1"`` images, one per page.
        """
        images = []
        for page in PdfDocument(self.pdf_bytes):
            bitmap = page.render(scale=self.dpi / 72, rotation=self.rotation)
            # Rotation is already handled in the PDF rendering
            images.append(self._to_monochrome(bitmap.to_pil(), rotate=False))
        return images

    def to_zpl(self) -> str:
        """
        Convert PDF bytes to Zebra Programming Language (ZPL).

        :returns: A complete ZPL file string which can be sent to a ZPL compatible \
        printer or a ZPL graphic field if complete_zpl is not set.
        """
        images = self._render_pages()
        if not images:
            raise ValueError("PDF has no pages.")

        graphic_fields = []
        offset = 0
        for pil_image in images:
            pos_y = self.pos_y if self.split_pages else self.pos_y + offset
            graphic_fields.append(self._get_field(pil_image, self.pos_x, pos_y) + "\n")
            offset += pil_image.height

        if not self.complete_zpl:
            return "".join(graphic_fields)

        if self.split_pages:
            return "".join(self._get_label(field) for field in graphic_fields)
        return self._get_label("".join(graphic_fields))
