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

"""Command line interface for converting between PDF, images, and ZPL."""

# 1. Standard library imports:
import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

# 2. Known third party imports:
from PIL import UnidentifiedImageError
from pypdfium2 import PdfiumError

# 3. Local imports in the relative form:
from zebrafy import __version__
from zebrafy.graphic_field import FORMATS
from zebrafy.options import ROTATIONS
from zebrafy.zebrafy_image import ZebrafyImage
from zebrafy.zebrafy_pdf import ZebrafyPDF
from zebrafy.zebrafy_zpl import ZebrafyZPL


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zebrafy",
        description=(
            "Convert a PDF or an image to ZPL, or the graphic fields of a ZPL file "
            "to a PDF or images."
        ),
        epilog=(
            "examples:\n"
            "  zebrafy label.pdf -o label.zpl\n"
            "  zebrafy logo.png --format z64 --no-dither > logo.zpl\n"
            "  zebrafy label.zpl -o label.pdf"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input", help="PDF, image, or ZPL file to convert. Use - to read stdin."
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output file. ZPL is written to stdout if omitted. For ZPL input, the "
            "extension picks the output: .pdf for a PDF, or an image extension such "
            "as .png for one image per graphic field."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)

    zpl = parser.add_argument_group("PDF and image to ZPL")
    zpl.add_argument(
        "--format",
        type=str.upper,
        choices=FORMATS,
        default="ASCII",
        help="graphic field format (default: ASCII)",
    )
    zpl.add_argument("--invert", action="store_true", help="invert black and white")
    zpl.add_argument(
        "--dither",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="dither instead of a hard black and white threshold (default: dither)",
    )
    zpl.add_argument(
        "--threshold",
        type=int,
        default=128,
        help="black pixel threshold without dithering, 0-255 (default: 128)",
    )
    zpl.add_argument("--width", type=int, default=0, help="resize to this width")
    zpl.add_argument("--height", type=int, default=0, help="resize to this height")
    zpl.add_argument("--pos-x", type=int, default=0, help="x position (default: 0)")
    zpl.add_argument("--pos-y", type=int, default=0, help="y position (default: 0)")
    zpl.add_argument(
        "--rotation",
        type=int,
        choices=ROTATIONS,
        default=0,
        help="clockwise rotation in degrees (default: 0)",
    )
    zpl.add_argument(
        "--line-break",
        type=int,
        help="insert a line break in the graphic field data every N characters",
    )
    zpl.add_argument(
        "--graphic-field-only",
        action="store_true",
        help="output only the graphic field, without ^XA and ^XZ",
    )
    zpl.add_argument(
        "--label-size",
        action="store_true",
        help="set the print width (^PW) and label length (^LL) to fit the image",
    )

    shared = parser.add_argument_group("PDF input and output")
    shared.add_argument(
        "--dpi",
        type=int,
        default=203,
        help="printer resolution in dots per inch (default: 203)",
    )
    shared.add_argument(
        "--split-pages",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "put each PDF page on its own label, or stack them on one label "
            "(default: split)"
        ),
    )
    return parser


def _read_input(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    return Path(path).read_bytes()


def _is_zpl(path: str, data: bytes) -> bool:
    if Path(path).suffix.lower() == ".zpl":
        return True
    return data.lstrip()[:3].upper() in (b"^XA", b"~DG")


def _zpl_to_file(args: argparse.Namespace, data: bytes) -> None:
    if not args.output or args.output == "-":
        raise ValueError(
            "ZPL input needs an output file: -o out.pdf for a PDF, or -o out.png "
            "for images."
        )
    zebrafy_zpl = ZebrafyZPL(data.decode("utf-8"), dpi=args.dpi)
    output = Path(args.output)
    if output.suffix.lower() == ".pdf":
        output.write_bytes(zebrafy_zpl.to_pdf())
        return

    images = zebrafy_zpl.to_images()
    if len(images) == 1:
        images[0].save(output)
        return
    for number, image in enumerate(images, start=1):
        image.save(output.with_name(f"{output.stem}-{number}{output.suffix}"))


def _to_zpl(args: argparse.Namespace, data: bytes) -> str:
    options = {
        "format": args.format,
        "invert": args.invert,
        "dither": args.dither,
        "threshold": args.threshold,
        "width": args.width,
        "height": args.height,
        "pos_x": args.pos_x,
        "pos_y": args.pos_y,
        "rotation": args.rotation,
        "string_line_break": args.line_break,
        "complete_zpl": not args.graphic_field_only,
        "set_label_size": args.label_size,
    }
    if data.startswith(b"%PDF"):
        return ZebrafyPDF(
            data, dpi=args.dpi, split_pages=args.split_pages, **options
        ).to_zpl()
    return ZebrafyImage(data, **options).to_zpl()


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the ``zebrafy`` command.

    :param argv: Command line arguments, defaults to ``sys.argv[1:]``.
    :returns: Exit status.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        data = _read_input(args.input)
        if _is_zpl(args.input, data):
            _zpl_to_file(args, data)
            return 0

        zpl = _to_zpl(args, data)
        if args.output and args.output != "-":
            Path(args.output).write_text(zpl, encoding="ascii")
        else:
            sys.stdout.write(zpl)
    except BrokenPipeError:
        # The reader of stdout went away, e.g. `zebrafy label.pdf | head`
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 1
    except UnidentifiedImageError:
        parser.exit(1, f"zebrafy: error: {args.input} is not a PDF, image, or ZPL.\n")
    except (OSError, PdfiumError, TypeError, ValueError) as error:
        parser.exit(1, f"zebrafy: error: {error}\n")
    return 0
