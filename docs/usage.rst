Usage
=====

.. _installation:

Installation
------------

To use Zebrafy, first install it using pip:

.. code-block:: console

  (.venv) $ pip install zebrafy


ZebrafyPDF and ZebrafyImage Parameters
--------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Parameter
     - Description
   * - ``format``
     - ZPL graphic field format (default ``"ASCII"``)

       - ``"ASCII"``: ASCII hexadecimal, the most compatible
       - ``"ASCII_COMPRESSED"``: ASCII hexadecimal with ZPL run-length compression.
         Works on the same printers as ``"ASCII"``. A PDF page with text comes out
         5 to 50 times smaller, a photo about half the size
       - ``"B64"``: Base64 binary
       - ``"Z64"``: zlib compressed Base64 binary, usually the smallest
   * - ``invert``
     - Invert black and white (``True`` or ``False``, default ``False``)
   * - ``dither``
     - Dither the image instead of a hard black and white threshold (``True`` or
       ``False``, default ``True``)
   * - ``threshold``
     - Black pixel threshold when not dithering (``0-255``, default ``128``)
   * - ``width``
     - Width of the image in the resulting ZPL, ``0`` to keep the original width
       (default ``0``)
   * - ``height``
     - Height of the image in the resulting ZPL, ``0`` to keep the original height
       (default ``0``)
   * - ``pos_x``
     - X position of the graphic field in dots (default ``0``)
   * - ``pos_y``
     - Y position of the graphic field in dots (default ``0``)
   * - ``rotation``
     - Clockwise rotation in degrees (``0``, ``90``, ``180`` or ``270``, default ``0``)
   * - ``string_line_break``
     - Insert a line break into the graphic field data every this many characters
       (default ``None``)
   * - ``complete_zpl``
     - Wrap the output in ``^XA`` and ``^XZ`` to make a complete label, or output only
       the graphic field (``True`` or ``False``, default ``True``)
   * - ``set_label_size``
     - Add ``^PW`` (print width) and ``^LL`` (label length) commands sized to the
       image, so the printer doesn't crop it to its configured width (``True`` or
       ``False``, default ``False``)

**ZebrafyPDF** also takes these parameters:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Parameter
     - Description
   * - ``dpi``
     - Resolution to render the PDF at, in dots per inch (default ``203``). Set it to
       the resolution of your printer and the PDF prints at its real size. The
       ``PrinterDPI`` presets cover the common Zebra print heads: ``DPI_152``,
       ``DPI_203``, ``DPI_300`` and ``DPI_600``
   * - ``split_pages``
     - Print each page on a label of its own (default ``True``). With ``False``, the
       pages are stacked top to bottom on one label

All parameters except the input are keyword-only. Transparent pixels in images are
treated as white.



Conversions
-----------

Image to ZPL Graphic Field with ZebrafyImage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert image bytes into a complete ZPL string and save to file:

.. code-block:: python

  from zebrafy import ZebrafyImage

  with open("source.png", "rb") as image:
      zpl_string = ZebrafyImage(image.read()).to_zpl()

  with open("output.zpl", "w") as zpl:
      zpl.write(zpl_string)

Example usage with optional parameters:

.. code-block:: python

  from zebrafy import ZebrafyImage

  with open("source.png", "rb") as image:
      zpl_string = ZebrafyImage(
          image.read(),
          format="Z64",
          invert=True,
          dither=False,
          threshold=128,
          width=720,
          height=1280,
          pos_x=100,
          pos_y=100,
          rotation=90,
          string_line_break=80,
          complete_zpl=True,
      ).to_zpl()

  with open("output.zpl", "w") as zpl:
      zpl.write(zpl_string)

Alternatively, **ZebrafyImage** also accepts PIL Image as the image parameter instead of
image bytes:

.. code-block:: python

  from PIL import Image
  from zebrafy import ZebrafyImage

  pil_image = Image.new(mode="RGB", size=(100, 100))
  zpl_string = ZebrafyImage(pil_image).to_zpl()

  with open("output.zpl", "w") as zpl:
      zpl.write(zpl_string)


PDF to ZPL Graphic Field with ZebrafyPDF
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert PDF bytes into a complete ZPL string and save to file:

.. code-block:: python

  from zebrafy import ZebrafyPDF

  with open("source.pdf", "rb") as pdf:
      zpl_string = ZebrafyPDF(pdf.read()).to_zpl()

  with open("output.zpl", "w") as zpl:
      zpl.write(zpl_string)

**ZebrafyPDF** conversion supports the same optional parameters as **ZebrafyImage**
conversion, with the addition of the ``split_pages`` parameter to split the PDF pages:

.. code-block:: python

  from zebrafy import ZebrafyPDF

  with open("source.pdf", "rb") as pdf:
      zpl_string = ZebrafyPDF(
          pdf.read(),
          format="Z64",
          invert=True,
          dither=False,
          threshold=128,
          dpi=203,
          width=720,
          height=1280,
          pos_x=100,
          pos_y=100,
          rotation=90,
          string_line_break=80,
          complete_zpl=True,
          split_pages=True,
      ).to_zpl()

  with open("output.zpl", "w") as zpl:
      zpl.write(zpl_string)

ZPL to PDF or Images with ZebrafyZPL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert all graphic fields from a valid ZPL file to PIL Images and save to image files:

.. code-block:: python

  from zebrafy import ZebrafyZPL

  with open("source.zpl", "r") as zpl:
      pil_images = ZebrafyZPL(zpl.read()).to_images()
      for count, pil_image in enumerate(pil_images):
          pil_image.save(f"output_{count}.png", "PNG")

Convert all graphic fields from a valid ZPL file to PDF bytes and save to PDF file:

.. code-block:: python

  from zebrafy import ZebrafyZPL

  with open("source.zpl", "r") as zpl:
      pdf_bytes = ZebrafyZPL(zpl.read()).to_pdf()

  with open("output.pdf", "wb") as pdf:
      pdf.write(pdf_bytes)


Command Line
------------

Installing zebrafy also installs a ``zebrafy`` command (``python -m zebrafy`` works
too). It converts a PDF or an image to ZPL, or a ZPL file to a PDF or images:

.. code-block:: console

  $ zebrafy label.pdf -o label.zpl
  $ zebrafy logo.png --format ascii_compressed --no-dither --pos-x 50 > logo.zpl
  $ zebrafy label.zpl -o label.pdf
  $ zebrafy label.zpl -o label.png

The options match the library parameters: ``--format``, ``--invert``,
``--no-dither``, ``--threshold``, ``--width``, ``--height``, ``--pos-x``, ``--pos-y``,
``--rotation``, ``--line-break``, ``--graphic-field-only``, ``--label-size``,
``--dpi`` and ``--no-split-pages``. Run ``zebrafy --help`` for details. Use ``-`` as
the input to read from stdin. When a ZPL file has more than one graphic field, each
one is saved as its own image, numbered ``label-1.png``, ``label-2.png`` and so on.


Upgrading from 1.x
------------------

Version 2.0 changes the output, so check your labels after upgrading.

- Black pixels now print black. Earlier versions wrote black pixels as blank dots and
  white pixels as printed dots, so labels came out inverted and ``invert=True`` was
  the workaround. Remove ``invert=True`` if you added it for that reason.
- ``ZebrafyPDF`` renders at 203 DPI instead of 72, so a PDF prints at its real size
  on a 203 DPI printer. Pass ``dpi=72`` to get the old size back.
- ``ZebrafyPDF`` puts each page on its own label by default. Before, all pages were
  printed on top of each other on one label. With ``split_pages=False`` the pages are
  now stacked below each other.
- ``rotation`` turns images clockwise, the same as PDF rotation, and keeps the whole
  image. Before, ``ZebrafyImage`` turned counter-clockwise and cropped non-square
  images.
- Transparent pixels are white. Before, they took the color stored under them, which
  is usually black.
- ``ZebrafyZPL.to_pdf()`` stores the images losslessly and sizes each page for
  203 DPI. Pass ``dpi`` to ``ZebrafyZPL`` for other printers.
- The ``compression_type`` parameter is gone. Use ``format`` instead: ``"A"`` is
  ``"ASCII"``, ``"B"`` is ``"B64"`` and ``"C"`` is ``"Z64"``.
- Parameters after the input are keyword-only, and ``None`` is no longer accepted in
  place of a default.
- ASCII graphic fields use uppercase hexadecimal.
- Python 3.10 or newer is required.
