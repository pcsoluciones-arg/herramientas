#!/usr/bin/env python3
"""Corre revisar.py sobre los casos de prueba y compara las reglas que encuentra con las esperadas."""
import json, os, subprocess, sys, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
REVISAR = os.path.join(AQUI, "..", "revisar.py")
CASOS = os.path.join(AQUI, "casos")

# caso: (opciones, reglas que tienen que aparecer como FALLA)
ESPERADO = {
    "bueno-neutro.md": (["--idioma", "neutro"], set()),
    "malo-neutro.md": (["--idioma", "neutro"], {"guiones", "idioma", "titulos", "marcadores"}),
    "malo-voseo.md": (["--idioma", "voseo"], {"idioma"}),
    "sitio-malo": (["--perfil", "sitio", "--idioma", "voseo"], {"open-graph", "indexacion", "area-segura", "whatsapp", "copy-publico", "schema"}),
}


def correr(ruta, opciones):
    r = subprocess.run([sys.executable, REVISAR, "--json"] + opciones + [ruta], capture_output=True, text=True)
    return {h["regla"] for h in json.loads(r.stdout) if h["nivel"] == "FALLA"}


errores = 0
for caso, (opciones, esperado) in ESPERADO.items():
    hallado = correr(os.path.join(CASOS, caso), opciones)
    ok = hallado == esperado
    errores += not ok
    print(("ok   " if ok else "MAL  ") + caso + ("" if ok else "  esperado %s, hallado %s" % (sorted(esperado), sorted(hallado))))

with tempfile.TemporaryDirectory() as d:
    z = os.path.join(d, "paquete.zip")
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("index.html", "<h1>Hola</h1>")
        f.writestr("img/vacia.jpg", "")
    hallado = correr(z, [])
    ok = hallado == {"zip"}
    errores += not ok
    print(("ok   " if ok else "MAL  ") + "zip con un archivo vacío")

print("\n%s" % ("Todo bien." if not errores else "%d casos fallaron." % errores))
sys.exit(1 if errores else 0)
