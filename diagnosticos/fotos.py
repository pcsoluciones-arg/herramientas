#!/usr/bin/env python3
"""Pasa una foto a data URL JPEG para el diagnóstico: 1000 px de ancho y calidad 76, debajo de 1 MB.

Uso como script:  python3 -I fotos.py foto.jpg [ancho] [calidad]   (imprime la data URL)
Uso como módulo:  from fotos import dataurl

Las fotos de Maps se bajan grandes agregando =w1600-h1600-k-no a la URL de lh3.googleusercontent.com.
"""
import base64
import io
import sys

from PIL import Image, ImageOps


def dataurl(ruta, ancho=1000, calidad=76, recorte=None):
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    if recorte:
        im = im.crop(recorte)
    if im.width > ancho:
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=calidad, optimize=True, progressive=True)
    if b.tell() >= 1_000_000:
        raise ValueError("%s pesa %d KB después de comprimir: bajar el ancho o la calidad" % (ruta, b.tell() // 1024))
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(dataurl(sys.argv[1], *(int(x) for x in sys.argv[2:4])))
