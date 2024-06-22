"""
zebrafy: A Python library for converting PDF and images to Zebra Programming Language.

This package provides tools to facilitate the conversion of PDF documents and images \
into and from Zebra Programming Language, which is used by Zebra label printers.
"""

try:
    from ._version import __version__, version
    from ._version import __version_tuple__, version_tuple
except ImportError:
    __version__ = version = "unknown version"
    __version_tuple__ = version_tuple = (0, 0, 0)

from .crc import CRC
from .graphic_field import GraphicField
from .zebrafy_image import ZebrafyImage
from .zebrafy_pdf import ZebrafyPDF
from .zebrafy_zpl import ZebrafyZPL
