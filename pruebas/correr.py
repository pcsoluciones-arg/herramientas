#!/usr/bin/env python3
"""Corre revisar.py sobre los casos de prueba y compara las reglas que encuentra con las esperadas.
Al final corre las pruebas de la Fábrica de presencia (sitios/pruebas/correr.py)."""
import json, os, subprocess, sys, tempfile, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
REVISAR = os.path.join(AQUI, "..", "revisar.py")
CASOS = os.path.join(AQUI, "casos")
URL_CERRAJERO = ["--url", "https://llavesmartin.com.ar/"]

# caso: (opciones, reglas que tienen que aparecer como FALLA, reglas que tienen que aparecer como AVISO o None si no se miran)
ESPERADO = {
    "bueno-neutro.md": (["--idioma", "neutro"], set(), None),
    "malo-neutro.md": (["--idioma", "neutro"], {"guiones", "idioma", "titulos", "marcadores"}, None),
    "codigo-citado.md": (["--idioma", "neutro"], set(), None),
    "malo-voseo.md": (["--idioma", "voseo"], {"idioma"}, None),
    "sitio-malo": (["--perfil", "sitio", "--idioma", "voseo"],
                   {"open-graph", "indexacion", "area-segura", "whatsapp", "copy-publico", "schema", "publicado"}, None),
    # 1/11/2026, Fábrica de presencia: reglas nuevas del perfil sitio
    "sitio-bueno": (["--perfil", "sitio", "--idioma", "voseo"] + URL_CERRAJERO, set(), set()),
    "sitio-malo-publicado": (["--perfil", "sitio", "--idioma", "voseo"] + URL_CERRAJERO,
                             {"open-graph", "indexacion", "schema", "fijo-mezcla", "publicado"},
                             {"open-graph", "area-segura", "plazos", "cabecera", "imagenes"}),
}


def correr(ruta, opciones):
    r = subprocess.run([sys.executable, REVISAR, "--json"] + opciones + [ruta], capture_output=True, text=True)
    h = json.loads(r.stdout)
    return {x["regla"] for x in h if x["nivel"] == "FALLA"}, {x["regla"] for x in h if x["nivel"] == "AVISO"}


errores = 0
for caso, (opciones, esperado, avisos) in ESPERADO.items():
    fallas, hallados = correr(os.path.join(CASOS, caso), opciones)
    ok = fallas == esperado and (avisos is None or hallados == avisos)
    errores += not ok
    detalle = "" if ok else "  esperado %s / %s, hallado %s / %s" % (sorted(esperado), sorted(avisos or []), sorted(fallas), sorted(hallados))
    print(("ok   " if ok else "MAL  ") + caso + detalle)

# El sitio propio sí usa plazos («Tu página lista en 3 días»): ahí no se avisa.
with tempfile.TemporaryDirectory() as d:
    with open(os.path.join(CASOS, "sitio-malo-publicado", "index.html"), encoding="utf8") as f:
        pagina = f.read()
    with open(os.path.join(d, "index.html"), "w", encoding="utf8") as f:
        f.write(pagina)
    _, avisos = correr(os.path.join(d, "index.html"), ["--perfil", "sitio", "--url", "https://pcsoluciones.com.ar/"])
    ok = "plazos" not in avisos
    errores += not ok
    print(("ok   " if ok else "MAL  ") + "plazos: el sitio propio no avisa")

with tempfile.TemporaryDirectory() as d:
    z = os.path.join(d, "paquete.zip")
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("index.html", "<h1>Hola</h1>")
        f.writestr("img/vacia.jpg", "")
    hallado, _ = correr(z, [])
    ok = hallado == {"zip"}
    errores += not ok
    print(("ok   " if ok else "MAL  ") + "zip con un archivo vacío")

print("\n== Fábrica de presencia (sitios/)")
errores += subprocess.run([sys.executable, os.path.join(AQUI, "..", "sitios", "pruebas", "correr.py")]).returncode != 0

print("\n%s" % ("Todo bien." if not errores else "%d casos fallaron." % errores))
sys.exit(1 if errores else 0)
