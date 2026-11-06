#!/usr/bin/env python3
"""Arma el diagnostico-<slug>.json (formato diagnostico/v2) que se arrastra al panel.

Uso: python3 -I armar.py <caso.json> <salida.json>

caso.json lleva todo el diagnóstico con los textos ya escritos, pero con las fotos como rutas
(relativas al caso.json) en vez de data URL:
  "fotos": {"portada": "fotos/f21.jpg", "portada_pos": "center 30%",
            "galeria": ["fotos/f51.jpg", ...], "galeria_pos": [...],
            "ficha": {"ruta": "capturas/ficha.jpg", "ancho": 800, "calidad": 82}, ...},
  "captura": "capturas/chatgpt.jpg"
Las claves que terminan en _pos se copian tal cual. Cada foto sale como JPEG de menos de 1 MB.
Ejemplo con un negocio inventado: ejemplo/caso-ejemplo.json. El campo de cada dato está en
DOC_DIAGNOSTICO_V2 de src/diagnostico.js (repositorio del panel) y en /api/formato-diagnostico.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fotos import dataurl  # noqa: E402

ANCHOS = {"ficha": (800, 82), "nombre": (1200, 82), "mockup": (1400, 82), "ia2": (1000, 82), "captura": (1000, 82)}


def convertir(valor, clave, base):
    if isinstance(valor, list):
        return [convertir(v, clave, base) for v in valor]
    if isinstance(valor, dict):
        ruta, ancho, calidad = valor["ruta"], valor.get("ancho"), valor.get("calidad")
    else:
        ruta, ancho, calidad = valor, None, None
    if ruta.startswith("data:"):
        return ruta
    a, c = ANCHOS.get(clave, (1000, 76))
    return dataurl(os.path.join(base, ruta), ancho or a, calidad or c)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    caso = json.load(open(sys.argv[1], encoding="utf8"))
    caso.pop("_leeme", None)
    fotos = {}
    for k, v in (caso.get("fotos") or {}).items():
        fotos[k] = v if k.endswith("_pos") else convertir(v, k, base)
    caso["fotos"] = fotos
    if caso.get("captura"):
        caso["captura"] = convertir(caso["captura"], "captura", base)
    caso.setdefault("formato", "diagnostico/v2")
    txt = json.dumps(caso, ensure_ascii=False)
    if "—" in txt or "–" in txt:
        sys.exit("Hay un guion largo o semilargo en los textos")
    open(sys.argv[2], "w", encoding="utf8").write(txt)
    print("ok", len(txt) // 1024, "KB")


if __name__ == "__main__":
    main()
