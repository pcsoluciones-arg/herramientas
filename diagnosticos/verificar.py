#!/usr/bin/env python3
"""Verifica la página armada del diagnóstico: pantallas en el celular, scroll lateral y PDF en hojas A4.
Repite los controles de test/fabrica_37_diagnostico_v2.py del repositorio del panel.

Uso: python3 -I verificar.py <pagina.html> <prefijo-salida>

Deja <prefijo>.pantallas.png (la tira de pantallas a 390 × 664) y <prefijo>.pdf.
Sale con código 1 si algo falla: scroll lateral, contenido más alto que su pantalla, hojas que
no son A4 o errores de consola. Necesita Playwright y Pillow.
"""
import os
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

TAMANOS = ((390, 664), (390, 750), (360, 640), (430, 740), (1360, 860))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    html, pref = os.path.abspath(sys.argv[1]), sys.argv[2]
    fallas, errores = [], []
    tmp = tempfile.mkdtemp()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in TAMANOS:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if (w, h) == (390, 664) else 1)
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.goto("file://" + html)
            pg.wait_for_timeout(900)
            lateral = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
            desborde = pg.evaluate("[...document.querySelectorAll('.slide')].map(s=>{const c=s.querySelector('.cont');return c?Math.round(c.scrollHeight - c.clientHeight):0})")
            print("%dx%d lateral=%d desborde por pantalla=%s" % (w, h, lateral, desborde))
            if lateral > 0:
                fallas.append("scroll lateral a %d px" % w)
            if w < 1000 and any(x > 0 for x in desborde):
                fallas.append("contenido más alto que la pantalla a %dx%d" % (w, h))
            if (w, h) == (390, 664):
                tiras = []
                for k in range(len(desborde)):
                    pg.evaluate("document.getElementById('deck').scrollTo({left: document.querySelectorAll('.slide')[%d].offsetLeft, behavior:'auto'})" % k)
                    pg.wait_for_timeout(350)
                    f = os.path.join(tmp, "s%d.png" % k)
                    pg.screenshot(path=f)
                    tiras.append(Image.open(f))
                if tiras:
                    ancho = sum(i.width for i in tiras) + 20 * (len(tiras) - 1)
                    hoja = Image.new("RGB", (ancho, tiras[0].height), "white")
                    x = 0
                    for i in tiras:
                        hoja.paste(i, (x, 0))
                        x += i.width + 20
                    hoja.save(pref + ".pantallas.png")
            if (w, h) == (390, 750):
                pg.evaluate("window.__prepararPDF()")
                pg.emulate_media(media="print")
                hojas = pg.evaluate("[...document.querySelectorAll('.slide')].map(s => Math.round(s.getBoundingClientRect().height))")
                entran = pg.evaluate("""[...document.querySelectorAll('.slide:not(.portada)')].map(s => { const c = s.querySelector('.cont'), cs = getComputedStyle(s);
                  return !c || c.getBoundingClientRect().height <= s.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom) + 1; })""")
                print("hojas A4:", hojas, "entran:", entran)
                if len(set(hojas)) != 1 or abs(hojas[0] - 1123) > 2 or not all(entran):
                    fallas.append("PDF: hojas que no son A4 o contenido que no entra")
                pg.pdf(path=pref + ".pdf", format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            pg.close()
        b.close()
    if errores:
        fallas.append("errores de consola: %s" % errores)
    print("FALLAS:", fallas or "ninguna")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
