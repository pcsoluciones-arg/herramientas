#!/usr/bin/env python3
"""Arma la grilla de portadas candidatas con el molde real del diagnóstico, para que Manu elija.

Uso: python3 -I portadas.py <base.json> <salida.jpg> foto1.jpg[@posición] foto2.jpg[@posición] ...

  base.json  el diagnóstico armado hasta ahora (alcanza con datos.negocio, corto, portada y fecha).
  posición   el foco de la foto en CSS, por ejemplo center 30%. Si no se pone, center.
Cada portada se ve como en el celular (390 × 664, con el velo y el título) y lleva una letra.
Usa render.mjs de esta misma carpeta (y el repositorio del panel, ver render.mjs).
"""
import json
import os
import string
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from fotos import dataurl  # noqa: E402


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    base = json.load(open(sys.argv[1], encoding="utf8"))
    salida, candidatas = sys.argv[2], sys.argv[3:]
    tmp = tempfile.mkdtemp()
    capturas = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 390, "height": 664}, device_scale_factor=2)
        for k, c in enumerate(candidatas):
            ruta, _, pos = c.partition("@")
            base["fotos"] = {"portada": dataurl(ruta), "portada_pos": pos or "center"}
            j, h = os.path.join(tmp, "p.json"), os.path.join(tmp, "p%d.html" % k)
            json.dump(base, open(j, "w", encoding="utf8"))
            subprocess.run(["node", os.path.join(AQUI, "render.mjs"), j, h], check=True, capture_output=True)
            pg.goto("file://" + h)
            pg.wait_for_timeout(700)
            f = os.path.join(tmp, "port%d.png" % k)
            pg.screenshot(path=f)
            capturas.append((string.ascii_uppercase[k], os.path.basename(ruta), f))
        b.close()
    W, H = 780, 1328
    cols = min(len(capturas), 4)
    filas = (len(capturas) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * (W + 30) + 30, filas * (H + 110) + 30), "white")
    d = ImageDraw.Draw(hoja)
    letra = ImageFont.load_default(size=64)
    for k, (L, nombre, f) in enumerate(capturas):
        x, y = 30 + (k % cols) * (W + 30), 30 + (k // cols) * (H + 110)
        d.text((x, y), "%s  (%s)" % (L, nombre[:24]), fill="black", font=letra)
        hoja.paste(Image.open(f), (x, y + 90))
    hoja.resize((hoja.width // 2, hoja.height // 2)).save(salida, quality=85)
    print("ok", salida)


if __name__ == "__main__":
    main()
