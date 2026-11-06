#!/usr/bin/env python3
"""Genera las imágenes de prueba del ejemplo (formas y degradés, sin fotos reales) en ejemplo/img/.

Uso: python3 -I hacer_imagenes.py
Sirven para probar el molde y las herramientas sin datos de ningún negocio real.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(AQUI, exist_ok=True)
random.seed(7)


def degrade(w, h, a, b):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return im


def taller(nombre, a, b):
    im = degrade(1600, 1000, a, b)
    d = ImageDraw.Draw(im)
    for _ in range(14):
        x, y, r = random.randint(0, 1600), random.randint(300, 1000), random.randint(60, 180)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(40, 40, 40), width=14)
        d.line([(x, y), (x + r, y - r)], fill=(60, 60, 60), width=10)
    im.filter(ImageFilter.GaussianBlur(1.5)).save(os.path.join(AQUI, nombre), quality=85)


taller("negocio.jpg", (232, 212, 190), (120, 90, 70))
taller("instalaciones.jpg", (220, 226, 230), (90, 100, 110))
banda = degrade(1600, 700, (250, 170, 90), (60, 40, 90))
banda.save(os.path.join(AQUI, "banda.jpg"), quality=85)
tex = Image.new("RGB", (1400, 900), (196, 74, 48))
d = ImageDraw.Draw(tex)
for x in range(0, 1400, 36):
    d.rectangle([x, 0, x + 14, 900], fill=(176, 62, 40))
tex.filter(ImageFilter.GaussianBlur(2)).save(os.path.join(AQUI, "textura.jpg"), quality=85)
logo = Image.new("RGBA", (360, 120), (0, 0, 0, 0))
d = ImageDraw.Draw(logo)
d.ellipse([4, 4, 116, 116], fill=(244, 240, 232, 255))
d.ellipse([30, 30, 90, 90], outline=(228, 87, 46, 255), width=10)
d.rounded_rectangle([132, 40, 352, 80], 20, fill=(244, 240, 232, 255))
logo.save(os.path.join(AQUI, "logo-negativo.png"))
print("ok", AQUI)
