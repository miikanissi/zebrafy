|zebrafy_icon_64| Zebrafy
=========================

.. |zebrafy_icon_64| image:: https://raw.githubusercontent.com/miikanissi/zebrafy/master/docs/zebrafy-64.png
   :alt: Zebrafy Logo

.. image:: https://github.com/miikanissi/zebrafy/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/miikanissi/zebrafy/actions/workflows/ci.yml
    :alt: CI

.. image:: https://readthedocs.org/projects/zebrafy/badge/?version=latest
    :target: https://zebrafy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/zebrafy
    :target: https://pypi.org/project/zebrafy
    :alt: Zebrafy PyPi Package

.. image:: https://img.shields.io/badge/license-LGPLv3-green
    :target: https://www.gnu.org/licenses/lgpl-3.0.en.html#license-text
    :alt: License

**Zebrafy** is a Python 3 library for converting PDF and images to and from
`Zebra Programming Language (ZPL) <https://en.wikipedia.org/wiki/Zebra_Programming_Language>`_
graphic fields (^GF).

**Zebrafy** consists of three conversion tools:

- **ZebrafyImage** — convert an image into valid ZPL
- **ZebrafyPDF** — convert a PDF into valid ZPL
- **ZebrafyZPL** — convert valid ZPL graphic fields into images or PDF

If you want more control over the resulting ZPL data, **ZebrafyImage** and
**ZebrafyPDF** support the following optional parameters:

+-----------------------+--------------------------------------------------------------------------------------------------------------+
| Parameter             | Description                                                                                                  |
+=======================+==============================================================================================================+
| ``format``            | ZPL graphic field format type (default ``"ASCII"``)                                                          |
|                       |                                                                                                              |
|                       | - ``"ASCII"`` — ASCII hexadecimal (most compatible)                                                          |
|                       | - ``"B64"`` — Base64 Binary                                                                                  |
|                       | - ``"Z64"`` — Z64 compressed binary (best compression)                                                       |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``invert``            | Invert the black and white in the image/PDF output. (``True`` or ``False``, default ``False``)               |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``dither``            | Dither the result instead of hard limit on black pixels. (``True`` or ``False``, default ``True``)           |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``threshold``         | Black pixel threshold for image without dithering (``0-255``, default ``128``)                               |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``width``             | Width of the image in the resulting ZPL, ``0`` to use original image/PDF width (default ``0``)               |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``height``            | Height of the image in the resulting ZPL, ``0`` to use original image/PDF height (default ``0``)             |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``pos_x``             | Pixel x position of the graphic field in resulting ZPL (default ``0``)                                       |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``pos_y``             | Pixel y position of the graphic field in resulting ZPL (default ``0``)                                       |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``rotation``          | Rotates the image by the specified degree (``0``, ``90``, ``180`` or ``270``, default ``0``)                 |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``string_line_break`` | Number of characters in graphic field content after which a line break is inserted (default ``None``)        |
+-----------------------+--------------------------------------------------------------------------------------------------------------+
| ``complete_zpl``      | Add ZPL header and footer or only get the ZPL graphic field output (``True`` or ``False``, default ``True``) |
+-----------------------+--------------------------------------------------------------------------------------------------------------+

Additionally, **ZebrafyPDF** supports the following optional parameters:

+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
| Parameter             | Description                                                                                                           |
+=======================+=======================================================================================================================+
| ``dpi``               | Pixels per PDF canvas unit, defines resolution scaling of the PDF image (<72: compress, >72: stretch, default ``72``) |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------+
| ``split_pages``       | Split the PDF into separate ZPL labels for each page (``True`` or ``False``, default ``False``)                       |
+-----------------------+-----------------------------------------------------------------------------------------------------------------------+


Getting Started
---------------

Installation
^^^^^^^^^^^^

.. code-block:: console

  pip install zebrafy


Dependencies
^^^^^^^^^^^^

Pip handles all dependencies automatically. This library is built on top of:

- `Pillow <https://pillow.readthedocs.io/>`_ — Python Imaging Library
- `pypdfium2 <https://github.com/pypdfium2-team/pypdfium2>`_ — Python 3 binding to
  `PDFium <https://pdfium.googlesource.com/pdfium/+/refs/heads/main>`_

Example Usage
^^^^^^^^^^^^^

Image to ZPL Graphic Field with **ZebrafyImage**
""""""""""""""""""""""""""""""""""""""""""""""""

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


PDF to ZPL Graphic Field with **ZebrafyPDF**
""""""""""""""""""""""""""""""""""""""""""""

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
          dpi=72,
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

ZPL to PDF or Images with **ZebrafyZPL**
""""""""""""""""""""""""""""""""""""""""

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


Contributing and Issues
-----------------------

Contributions and bug reports are welcome and can be submitted on the
`GitHub page <https://github.com/miikanissi/zebrafy>`_.

The project does not yet have a well-defined scope, and I'm open to new feature
requests. Features currently in consideration are:

- HTML to ZPL conversion by implementing standard HTML elements into ZPL commands
- Extract text from a PDF to render it as a native ZPL command instead of graphic field

License
-------

This source is released under the
`GNU Lesser General Public License v3.0 <https://www.gnu.org/licenses/lgpl-3.0.en.html#license-text>`_.

Logo
----

.. image:: https://raw.githubusercontent.com/miikanissi/zebrafy/master/docs/zebrafy-long.png
   :alt: Zebrafy Logo
