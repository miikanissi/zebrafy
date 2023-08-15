# **Zebrafy**

**Zebrafy** is a Python 3 library for converting PDF and images to and from
[Zebra Programming Language (ZPL)](https://en.wikipedia.org/wiki/Zebra_Programming_Language)
graphic fields (^GF).

**Zebrafy** consists of three conversion tools:

- **ZebrafyImage** — convert an image into valid ZPL
- **ZebrafyPDF** — convert a PDF into valid ZPL
- **ZebrafyZPL** — convert valid ZPL graphic fields into images or PDF

If you want more control over the resulting ZPL data, **ZebrafyImage** and
**ZebrafyPDF** support the following optional parameters:

| Parameter          | Description                                                                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `compression_type` | ZPL graphic field compression type (`"A"` — ASCII hexadecimal (most compatible), `"B"` — Base64 Binary, or `"C"` — Z64 compressed binary (best compression), Default `"A"`) |
| `invert`           | Invert the black and white in the image/PDF output. (`True` or `False`, Default `False`)                                                                                    |
| `dither`           | Dither the result instead of hard limit on black pixels. (`True` or `False`, Default `True`)                                                                                |
| `threshold`        | Black pixel threshold for image without dithering (`0-255`, Default `128`)                                                                                                  |
| `width`            | Width of the image in the resulting ZPL, `0` to use original image/PDF width (Default `0`)                                                                                  |
| `height`           | Height of the image in the resulting ZPL, `0` to use original image/PDF height (Default `0`)                                                                                |
| `pos_x`            | Pixel x position of the graphic field in resulting ZPL (Default `0`)                                                                                                        |
| `pos_y`            | Pixel y position of the graphic field in resulting ZPL (Default `0`)                                                                                                        |
| `complete_zpl`     | Add ZPL header and footer for complete ZPL output which is ready to be sent on a printer, or only get the ZPL graphic field output (`True` or `False`, Default `True`)      |

## Getting Started

### Installation

```sh
pip install zebrafy
```

### Dependencies

Pip handles all dependencies automatically. This library is built on top of:

- [Pillow](https://pillow.readthedocs.io/) — Python Imaging Library
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) — Python 3 binding to
  [PDFium](https://pdfium.googlesource.com/pdfium/+/refs/heads/main)

### Example Usage

#### Image to ZPL Graphic Field with **ZebrafyImage**

Convert image bytes into a complete ZPL string and save to file:

```Python
from zebrafy import ZebrafyImage

with open("source.png", "rb") as image:
    zpl_string = ZebrafyImage(image.read()).to_zpl()

with open("output.zpl", "w") as zpl:
    zpl.write(zpl_string)
```

Example usage with optional parameters:

```Python
from zebrafy import ZebrafyImage

with open("source.png", "rb") as image:
    zpl_string = ZebrafyImage(
        image.read(),
        compression_type="C",
        invert=True,
        dither=False,
        threshold=128,
        width=720,
        height=1280,
        pos_x=100,
        pos_y=100,
        complete_zpl=True,
    ).to_zpl()

with open("output.zpl", "w") as zpl:
    zpl.write(zpl_string)
```

Alternatively, **ZebrafyImage** also accepts PIL Image as the image parameter instead of
image bytes:

```Python
from PIL import Image
from zebrafy import ZebrafyImage

pil_image = Image.new(mode="RGB", size=(100, 100))
zpl_string = ZebrafyImage(pil_image).to_zpl()

with open("output.zpl", "w") as zpl:
    zpl.write(zpl_string)
```

#### PDF to ZPL Graphic Field with **ZebrafyPDF**

Convert PDF bytes into a complete ZPL string and save to file:

```Python
from zebrafy import ZebrafyPDF

with open("source.pdf", "rb") as pdf:
    zpl_string = ZebrafyPDF(pdf.read()).to_zpl()

with open("output.zpl", "w") as zpl:
    zpl.write(zpl_string)
```

**ZebrafyPDF** conversion supports the same optional parameters as **ZebrafyImage**
conversion:

```Python
from zebrafy import ZebrafyPDF

with open("source.pdf", "rb") as pdf:
    zpl_string = ZebrafyPDF(
        pdf.read(),
        compression_type="C",
        invert=True,
        dither=False,
        threshold=128,
        width=720,
        height=1280,
        pos_x=100,
        pos_y=100,
        complete_zpl=True,
    ).to_zpl()

with open("output.zpl", "w") as zpl:
    zpl.write(zpl_string)
```

#### ZPL to PDF or Images with **ZebrafyZPL**

Convert all graphic fields from a valid ZPL file to PIL Images and save to image files:

```Python
from zebrafy import ZebrafyZPL

with open("source.zpl", "r") as zpl:
    pil_images = ZebrafyZPL(zpl.read()).to_images()
    for count, pil_image in enumerate(pil_images):
        pil_image.save(f"output_{count}.png", "PNG")
```

Convert all graphic fields from a valid ZPL file to PDF bytes and save to PDF file:

```Python
from zebrafy import ZebrafyZPL

with open("source.zpl", "r") as zpl:
    pdf_bytes = ZebrafyZPL(zpl.read()).to_pdf()

with open("output.pdf", "wb") as pdf:
    pdf.write(pdf_bytes)
```

## License

This source is released under the
[GNU Lesser General Public License v3.0](./LICENSE.txt).
