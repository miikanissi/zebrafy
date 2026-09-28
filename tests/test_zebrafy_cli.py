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

# 1. Standard library imports:
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# 2. Known third party imports:
from PIL import Image

# 3. Local imports in the relative form:
from zebrafy import ZebrafyImage, ZebrafyPDF, ZebrafyZPL
from zebrafy.cli import main

from .test_zebrafy_common import TestZebrafyCommonBase

STATIC = Path(__file__).parent / "static"


class TestZebrafyCLI(TestZebrafyCommonBase):
    """Test the zebrafy command."""

    def setUp(self):
        """Set up a temporary directory."""
        super().setUp()
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.tmp = Path(temp_dir.name)

    def _run(self, *args, stdin=b""):
        """Run the command and return its exit status, stdout, and stderr."""
        stdout, stderr = io.StringIO(), io.StringIO()
        fake_stdin = io.TextIOWrapper(io.BytesIO(stdin))
        with (
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            patch("sys.stdin", fake_stdin),
        ):
            try:
                status = main([str(arg) for arg in args])
            except SystemExit as exit:
                status = exit.code
        return status, stdout.getvalue(), stderr.getvalue()

    def test_image_to_stdout(self):
        """Test converting an image and printing the ZPL."""
        status, stdout, _ = self._run(STATIC / "test_image.png", "--no-dither")
        self.assertEqual(status, 0)
        self.assertEqual(stdout, self._read_static_file("test_image_no_dither.zpl"))

    def test_image_options(self):
        """Test image options are passed through."""
        output = self.tmp / "out.zpl"
        status, _, _ = self._run(
            STATIC / "test_image.jpg",
            "-o", output,
            "--format", "z64",
            "--invert",
            "--threshold", "100",
            "--no-dither",
            "--width", "200",
            "--height", "100",
            "--pos-x", "3",
            "--pos-y", "4",
            "--rotation", "90",
            "--line-break", "60",
            "--label-size",
        )  # fmt: skip
        self.assertEqual(status, 0)
        expected = ZebrafyImage(
            self._read_static_file("test_image.jpg"),
            format="Z64",
            invert=True,
            threshold=100,
            dither=False,
            width=200,
            height=100,
            pos_x=3,
            pos_y=4,
            rotation=90,
            string_line_break=60,
            set_label_size=True,
        ).to_zpl()
        self.assertEqual(output.read_text(), expected)

        status, stdout, _ = self._run(STATIC / "test_image.jpg", "--graphic-field-only")
        self.assertTrue(stdout.startswith("^FO0,0^GFA"))

    def test_pdf_to_file(self):
        """Test converting a PDF into a ZPL file."""
        output = self.tmp / "out.zpl"
        status, _, _ = self._run(
            STATIC / "test_pdf.pdf", "-o", output, "--dpi", "72", "--no-split-pages"
        )
        self.assertEqual(status, 0)
        self.assertEqual(
            output.read_text(), self._read_static_file("test_pdf_single_label.zpl")
        )

    def test_stdin(self):
        """Test reading the input from stdin."""
        pdf = self._read_static_file("test_pdf.pdf")
        status, stdout, _ = self._run("-", "--dpi", "72", stdin=pdf)
        self.assertEqual(status, 0)
        self.assertEqual(stdout, ZebrafyPDF(pdf, dpi=72).to_zpl())

    def test_zpl_to_pdf_and_images(self):
        """Test converting ZPL into a PDF and into images."""
        zpl_file = STATIC / "test_pdf_ascii.zpl"
        zpl = zpl_file.read_text()

        status, _, _ = self._run(zpl_file, "-o", self.tmp / "out.pdf", "--dpi", "72")
        self.assertEqual(status, 0)
        self.assertEqual((self.tmp / "out.pdf").read_bytes()[:5], b"%PDF-")

        # One image per graphic field, numbered when there is more than one
        status, _, _ = self._run(zpl_file, "-o", self.tmp / "page.png")
        self.assertEqual(status, 0)
        images = ZebrafyZPL(zpl).to_images()
        for number, image in enumerate(images, start=1):
            with Image.open(self.tmp / f"page-{number}.png") as saved:
                self.assertEqual(saved.convert("1").tobytes(), image.tobytes())

        # ZPL is recognized by its content too
        zpl_without_extension = self.tmp / "label"
        zpl_without_extension.write_text(self._read_static_file("test_image_ascii.zpl"))
        status, _, _ = self._run(zpl_without_extension, "-o", self.tmp / "single.png")
        self.assertEqual(status, 0)
        self.assertTrue((self.tmp / "single.png").exists())

    def test_errors(self):
        """Test errors exit with status 1 and a message."""
        not_an_image = self.tmp / "notes.txt"
        not_an_image.write_text("hello")
        broken_pdf = self.tmp / "broken.pdf"
        broken_pdf.write_bytes(b"%PDF-1.4 broken")
        cases = [
            ((self.tmp / "missing.png",), "No such file"),
            ((not_an_image,), "is not a PDF, image, or ZPL"),
            ((broken_pdf,), "error:"),
            ((STATIC / "test_image_ascii.zpl",), "needs an output file"),
            ((STATIC / "test_image.png", "--threshold", "300"), "Threshold"),
        ]
        for args, message in cases:
            with self.subTest(args=args):
                status, stdout, stderr = self._run(*args)
                self.assertEqual(status, 1)
                self.assertEqual(stdout, "")
                self.assertIn(message, stderr)

    def test_broken_pipe(self):
        """Test a closed stdout exits quietly."""
        with (
            patch("sys.stdout.write", side_effect=BrokenPipeError),
            patch("zebrafy.cli.os.dup2") as dup2,
            patch("zebrafy.cli.os.open", return_value=99),
            patch("sys.stdout.fileno", return_value=1),
        ):
            status = main([str(STATIC / "test_image.jpg")])
        self.assertEqual(status, 1)
        dup2.assert_called_once_with(99, 1)

    def test_python_m(self):
        """Test ``python -m zebrafy`` runs the command."""
        result = subprocess.run(
            [sys.executable, "-m", "zebrafy", "--version"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent)},
        )
        self.assertTrue(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
