#!/usr/bin/env python3
"""Saca las capturas de la página de ejemplo (la que arma molde_landing.py) para el mockup.

Uso: python3 -I capturar_landing.py pagina.html carpeta_salida

Deja en la carpeta:
  desk.png          computadora, 1360 × 800 (va en el mockup)
  desk-full.png     computadora, página completa
  movil-iphone.png  celular 390 × 780 simulando los 44 px del área segura del iPhone (va en el mockup),
                    así la barra llega por detrás del reloj y ocupa la pantalla entera
  movil-raw.png     celular 390 × 736, sin área segura
  movil-full.png    celular, página completa
Corta con error si alguna captura tiene scroll lateral.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

# Simula env(safe-area-inset-top) = 44 px: en Chromium vale 0.
AREA_SEGURA = "@media(max-width:640px){header{padding-top:54px!important}.cartel{padding-top:138px!important}}"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    origen = pathlib.Path(sys.argv[1]).resolve().as_uri()
    salida = pathlib.Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for nombre, w, h, completa in [("desk", 1360, 800, False), ("desk-full", 1360, 800, True),
                                        ("movil-iphone", 390, 780, False), ("movil-raw", 390, 736, False),
                                        ("movil-full", 390, 736, True)]:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if "movil" in nombre else 1)
            pg.goto(origen)
            if nombre == "movil-iphone":
                pg.add_style_tag(content=AREA_SEGURA)
            pg.wait_for_timeout(600)
            ancho = pg.evaluate("document.documentElement.scrollWidth")
            if ancho > w:
                sys.exit("%s: scroll lateral (%d px en una pantalla de %d)" % (nombre, ancho, w))
            pg.screenshot(path=str(salida / (nombre + ".png")), full_page=completa)
            pg.close()
        b.close()
    print("ok", salida)


if __name__ == "__main__":
    main()
