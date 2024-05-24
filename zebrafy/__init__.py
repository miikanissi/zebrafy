"""
zebrafy: A Python library for converting PDF and images to Zebra Programming Language (ZPL).

This package provides tools to facilitate the conversion of PDF documents and images into
and from Zebra Programming Language, which is used by Zebra label printers.
"""

from .crc import CRC
from .graphic_field import GraphicField
from .zebrafy_image import ZebrafyImage
from .zebrafy_pdf import ZebrafyPDF
from .zebrafy_zpl import ZebrafyZPL

__version__ = "1.1.3"
