#!/usr/bin/env python3
"""Compone el mockup de "Cómo se vería": la computadora y el iPhone, en 1400 × 870.

Uso: python3 -I mockup.py desk.png movil-iphone.png salida.jpg

Las capturas salen de capturar_landing.py (desk.png a 1360 × 800 y movil-iphone.png a 390 × 780).
"""
import sys

from PIL import Image, ImageDraw, ImageFilter


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    W, H = 1400, 870
    cv = Image.new("RGB", (W, H), "white")
    desk = Image.open(sys.argv[1]).convert("RGB").resize((1080, 635))
    sombra = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sombra).rounded_rectangle([60, 60, 1180, 800], 30, fill=90)
    cv.paste((200, 200, 205), (0, 0), sombra.filter(ImageFilter.GaussianBlur(28)))
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([40, 40, 1164, 778], 28, fill="#1b1c20")
    cv.paste(desk, (62, 62))
    d.rounded_rectangle([0, 728, 1200, 762], 16, fill="#d9dadf")
    d.rounded_rectangle([500, 728, 660, 738], 6, fill="#b8bac1")
    movil = Image.open(sys.argv[2]).convert("RGB").resize((300, 600))
    px, py = 1060, 220
    sombra2 = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sombra2).rounded_rectangle([px + 10, py + 20, px + 340, py + 660], 52, fill=110)
    cv.paste((190, 190, 195), (0, 0), sombra2.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([px, py, px + 324, py + 640], 50, fill="#111216")
    mascara = Image.new("L", (300, 600), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, 300, 600], 40, fill=255)
    cv.paste(movil, (px + 12, py + 20), mascara)
    d.rounded_rectangle([px + 117, py + 28, px + 207, py + 52], 12, fill="#111216")
    cv.save(sys.argv[3], quality=86)
    print("ok", sys.argv[3])


if __name__ == "__main__":
    main()
