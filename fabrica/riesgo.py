#!/usr/bin/env python3
"""Filtro de riesgo del repositorio herramientas.

Decide si un pedido de cambio (PR) se junta solo en main (riesgo bajo) o espera la aprobación de
Manu (riesgo alto), mirando qué archivos toca. Es código y no un modelo: siempre da lo mismo para
el mismo cambio. Ante la duda, alto.

Uso:
    python3 fabrica/riesgo.py BASE HEAD [--cuerpo archivo]   # BASE y HEAD: commits de git
    python3 fabrica/riesgo.py BASE HEAD --json

--cuerpo es el texto del PR: el tarifario de diagnósticos solo sale solo si el PR cita una
decisión de Manu con fecha (por ejemplo "Manu confirmó el 6/11/2026").
"""
import fnmatch
import json
import re
import subprocess
import sys

# La fábrica no puede aflojar sus propias reglas: .github/, fabrica/ y CLAUDE.md siempre esperan a Manu.
ALTO = [
    ".github/*", "fabrica/*", "CLAUDE.md", "revisar.py",
    "sitios/*",          # lo copia instalar.py a los sitios en vivo
    "skills/*",          # el criterio de los revisores
    "repertorio/*",      # copia del Repertorio de estilo
    "diagnosticos/*",    # los scripts de la fábrica de diagnósticos (salvo lo de BAJO)
]
BAJO = [
    "*.md",
    "pruebas/casos/*",
    "diagnosticos/ejemplo/*",
]
# Dentro de las carpetas de ALTO, lo único que sale solo: documentación para personas y el ejemplo.
EXCEPCIONES_ALTO = ["diagnosticos/LEEME.md", "diagnosticos/ejemplo/*", "sitios/LEEME*.md"]
TARIFARIO = "diagnosticos/tarifario.json"
DECISION = re.compile(r"\b(Manu|Manuel)\b[^\n]{0,80}?\b\d{1,2}/\d{1,2}/\d{4}\b")
MAX_LINEAS = 300


def coincide(ruta, patrones):
    return any(fnmatch.fnmatch(ruta, p) for p in patrones)


def clasificar(archivos, cuerpo="", lineas=0):
    """archivos: rutas cambiadas. Devuelve (riesgo, motivos)."""
    motivos = []
    for a in archivos:
        if a == TARIFARIO:
            if DECISION.search(cuerpo or ""):
                continue
            motivos.append(f"{a}: el PR no cita una decisión de Manu con fecha")
        elif a == "CLAUDE.md" or a.endswith("/CLAUDE.md"):
            motivos.append(f"{a}: instrucciones para agentes")
        elif coincide(a, ALTO) and not coincide(a, EXCEPCIONES_ALTO):
            motivos.append(f"{a}: archivo de riesgo alto")
        elif not coincide(a, BAJO):
            motivos.append(f"{a}: no está en la lista de riesgo bajo")
    if lineas > MAX_LINEAS:
        motivos.append(f"cambio de {lineas} líneas (más de {MAX_LINEAS})")
    if not archivos:
        motivos.append("el cambio no toca archivos")
    return ("alto" if motivos else "bajo"), motivos


def main():
    args = sys.argv[1:]
    como_json = "--json" in args
    cuerpo = ""
    if "--cuerpo" in args:
        i = args.index("--cuerpo")
        with open(args[i + 1], encoding="utf8") as f:
            cuerpo = f.read()
        del args[i:i + 2]
    args = [a for a in args if a != "--json"]
    if len(args) != 2:
        sys.exit(__doc__)
    base, head = args
    archivos = subprocess.run(["git", "diff", "--name-only", f"{base}...{head}"], capture_output=True, text=True, check=True).stdout.split()
    num = subprocess.run(["git", "diff", "--numstat", f"{base}...{head}"], capture_output=True, text=True, check=True).stdout
    lineas = sum(int(a) + int(b) for a, b, *_ in (l.split("\t") for l in num.splitlines()) if a.isdigit() and b.isdigit())
    riesgo, motivos = clasificar(archivos, cuerpo, lineas)
    if como_json:
        print(json.dumps({"riesgo": riesgo, "motivos": motivos, "archivos": archivos}, ensure_ascii=False))
    else:
        print("Riesgo " + riesgo)
        for m in motivos:
            print("- " + m)


if __name__ == "__main__":
    main()
