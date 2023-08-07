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

# 3. Local imports in the relative form:


class GraphicField:
    """
    Converts an image to Zebra Programming Language (ZPL) graphic field data.

    :param Image image: An instance of a PIL Image.
    :param str compression_type: ZPL compression type parameter that accepts the \
    following values:
        - "A": ASCII hexadecimal
        - "B": Binary
        - "C": Compressed binary
    (Default: ``"A"``)
    """

    def __init__(self, image, compression_type=None):
        self._image = image
        if compression_type is None:
            compression_type = "a"
        self._compression_type = compression_type.upper()

    @property
    def binary_byte_count(self):
        """
        Get binary byte count.

        This is the total number of bytes to be transmitted for the total image or
        the total number of bytes that follow parameter bytes_per_row. For ASCII \
        download, the parameter should match parameter graphic_field_count. \
        Out-of-range values are set to the nearest limit.

        :returns int: Binary byte count."
        """
        return len(self.data)

    @property
    def bytes_per_row(self):
        """
        Get bytes per row.

        This is the number of bytes in the image data that comprise one row of the \
        image.

        :returns int: Bytes per row."
        """
        return int((self._image.size[0] + 7) / 8)

    @property
    def graphic_field_count(self):
        """
        Get graphic field count.

        This is the total number of bytes comprising the image data (width x height).

        :returns int: Graphic field count."
        """
        return int(self.bytes_per_row * self._image.size[1])

    @property
    def compression_type(self):
        """
        Get compression type.

        Following options:
            - "A": ASCII hexadecimal
            - "B": Binary
            - "C": Compressed binary

        :returns str: Compression type.
        """
        return self._compression_type

    @property
    def data(self):
        """
        Get graphic field data depending on compression type.

        Options:
            - ASCII hexadecimal data: 00 to FF
            - Binary data: Strictly binary data is sent from the host. All control prefixes are
        ignored until the total number of bytes needed for the graphic format is sent.

        :returns: Graphic field data depending on compression type.
        """
        image_bytes = self._image.tobytes()
        if self.compression_type == "A":
            return image_bytes.hex()
        return image_bytes

    @property
    def graphic_field(self):
        """
        Get a complete graphic field string in ZPL.

        :returns str: Complete graphic field string in ZPL.
        """
        return "^GF{comp_type},{bb_count},{gf_count},{bpr},{data}^FS".format(
            comp_type=self.compression_type,
            bb_count=self.binary_byte_count,
            gf_count=self.graphic_field_count,
            bpr=self.bytes_per_row,
            data=self.data,
        )
