#!/usr/bin/env python3
"""Registro de cada corrida de la fábrica de diagnósticos: pasos, tiempos y lo que decidió Manu.

Lo alimenta Claude durante la corrida, con la hora real de cada paso. Al cerrar deja el
"Registro de la corrida - <negocio>.md" en la carpeta del caso y una línea en el registro general
(08 - PCS Central/Registros/diagnosticos.jsonl), que lee el informe de PCS Central.

Uso:
  registro.py inicio   <carpeta> --negocio "Guardería Altos del Canal" --slug altosdelcanal
  registro.py paso     <carpeta> "Relevamiento" --quien claude|manu|ambos [--nota "..."]
  registro.py decision <carpeta> "Trato: a Pablo, de vos"
  registro.py problema <carpeta> "OneDrive: archivos solo en la nube" [--solucion "device_stage_files"]
  registro.py contar   <carpeta> rondas_precio|correcciones_mockup [--cuanto 1]
  registro.py revisor  <carpeta> aprobado|cambios [--nota "2 bloqueos: trato y gestión"]
  registro.py cerrar   <carpeta> [--jsonl ruta/diagnosticos.jsonl]

<carpeta> es donde se trabaja el caso (guarda ahí registro.json). Cada "paso" cierra el anterior:
el tiempo de un paso va desde que empieza hasta que empieza el siguiente o se cierra la corrida.
Un paso de "manu" es tiempo de espera o de decisión de Manu; uno de "ambos", una conversación.
"""
import argparse
import json
import os
import sys
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
except Exception:  # sin base de zonas horarias: hora local de la máquina
    ZONA = None

QUIEN = {"claude": "Claude", "manu": "Manu", "ambos": "Manu y Claude"}


def ahora():
    return datetime.now(ZONA).replace(microsecond=0)


def leer(carpeta):
    ruta = os.path.join(carpeta, "registro.json")
    if not os.path.exists(ruta):
        sys.exit("No hay registro en %s: correr primero «registro.py inicio»" % carpeta)
    return json.load(open(ruta, encoding="utf8"))


def guardar(carpeta, r):
    json.dump(r, open(os.path.join(carpeta, "registro.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)


def minutos(a, b):
    return round((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() / 60)


def cerrar_paso(r, momento):
    if r["pasos"] and not r["pasos"][-1].get("fin"):
        r["pasos"][-1]["fin"] = momento


def resumen(r):
    por = {"claude": 0, "manu": 0, "ambos": 0}
    for p in r["pasos"]:
        if p.get("fin"):
            p["minutos"] = minutos(p["inicio"], p["fin"])
            por[p["quien"]] += p["minutos"]
    total = minutos(r["inicio"], r["fin"]) if r.get("fin") else None
    return total, por


def markdown(r):
    total, por = resumen(r)
    hora = lambda s: s[11:16]
    L = ["# Registro de la corrida: %s" % r["negocio"], "",
         "Fábrica de diagnósticos, skill `fabrica-diagnosticos`. %s, de %s a %s (hora de Buenos Aires)." % (r["inicio"][:10], hora(r["inicio"]), hora(r.get("fin") or r["inicio"])), "",
         "## Resumen", "",
         "- **Duración total: %s minutos.** Trabajo de Claude: %d. Esperando o decidiendo Manu: %d. Conversando entre los dos: %d." % (total, por["claude"], por["manu"], por["ambos"]),
         "- Rondas de precio: %d. Correcciones del mockup: %d." % (r["contadores"].get("rondas_precio", 0), r["contadores"].get("correcciones_mockup", 0)),
         "- Revisor de datos: %s." % ("; ".join("%s (%s)%s" % (v["resultado"], hora(v["hora"]), ": " + v["nota"] if v.get("nota") else "") for v in r["revisor"]) or "no corrió"), "",
         "## Paso a paso", "", "| # | Paso | Hora | Duración | Quién | Qué pasó |", "|---|---|---|---|---|---|"]
    for i, p in enumerate(r["pasos"], 1):
        L.append("| %d | %s | %s | %s min | %s | %s |" % (i, p["nombre"], hora(p["inicio"]), p.get("minutos", "?"), QUIEN[p["quien"]], p.get("nota", "").replace("|", "/")))
    L += ["", "## Lo que decidió Manu", ""]
    L += ["%d. %s (%s)" % (i, d["texto"], hora(d["hora"])) for i, d in enumerate(r["decisiones"], 1)] or ["Sin decisiones registradas."]
    L += ["", "## Problemas técnicos y cómo se resolvieron", ""]
    L += ["- %s%s" % (p["texto"], ". Solución: " + p["solucion"] if p.get("solucion") else "") for p in r["problemas"]] or ["Ninguno."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=["inicio", "paso", "decision", "problema", "contar", "revisor", "cerrar"])
    ap.add_argument("carpeta")
    ap.add_argument("texto", nargs="?")
    ap.add_argument("--negocio")
    ap.add_argument("--slug")
    ap.add_argument("--quien", choices=list(QUIEN), default="claude")
    ap.add_argument("--nota", default="")
    ap.add_argument("--solucion", default="")
    ap.add_argument("--cuanto", type=int, default=1)
    ap.add_argument("--jsonl")
    a = ap.parse_args()
    t = ahora().isoformat()

    if a.accion == "inicio":
        if not a.negocio or not a.slug:
            sys.exit("inicio necesita --negocio y --slug")
        os.makedirs(a.carpeta, exist_ok=True)
        guardar(a.carpeta, {"negocio": a.negocio, "slug": a.slug, "inicio": t, "pasos": [], "decisiones": [], "problemas": [],
                            "contadores": {}, "revisor": []})
        print("inicio", t)
        return
    r = leer(a.carpeta)
    if a.accion == "paso":
        cerrar_paso(r, t)
        r["pasos"].append({"nombre": a.texto, "quien": a.quien, "inicio": t, "nota": a.nota})
    elif a.accion == "decision":
        r["decisiones"].append({"texto": a.texto, "hora": t})
    elif a.accion == "problema":
        r["problemas"].append({"texto": a.texto, "solucion": a.solucion, "hora": t})
    elif a.accion == "contar":
        r["contadores"][a.texto] = r["contadores"].get(a.texto, 0) + a.cuanto
    elif a.accion == "revisor":
        r["revisor"].append({"resultado": a.texto, "nota": a.nota, "hora": t})
    elif a.accion == "cerrar":
        cerrar_paso(r, t)
        r["fin"] = t
        total, por = resumen(r)
        md = os.path.join(a.carpeta, "Registro de la corrida - %s.md" % r["negocio"])
        open(md, "w", encoding="utf8").write(markdown(r))
        linea = {"fecha": r["inicio"][:10], "negocio": r["negocio"], "slug": r["slug"], "inicio": r["inicio"], "fin": t,
                 "minutos_total": total, "minutos_claude": por["claude"], "minutos_manu": por["manu"], "minutos_ambos": por["ambos"],
                 "pasos": len(r["pasos"]), "decisiones": len(r["decisiones"]), "problemas": len(r["problemas"]),
                 "rondas_precio": r["contadores"].get("rondas_precio", 0), "correcciones_mockup": r["contadores"].get("correcciones_mockup", 0),
                 "revisor": [v["resultado"] for v in r["revisor"]]}
        if a.jsonl:
            with open(a.jsonl, "a", encoding="utf8") as f:
                f.write(json.dumps(linea, ensure_ascii=False) + "\n")
        print(md)
        print(json.dumps(linea, ensure_ascii=False))
    guardar(a.carpeta, r)


if __name__ == "__main__":
    main()
