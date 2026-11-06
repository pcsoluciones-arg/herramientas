#!/usr/bin/env python3
"""Molde de la página de ejemplo para el mockup del diagnóstico ("Cómo se vería").

Uso: python3 -I molde_landing.py <marca.json> <salida.html>

Sale de la página de Altos del Canal (6/11/2026), con la estructura que quedó después de las
correcciones de Manu. Para cada negocio cambian solo los datos de marca.json: textos, fotos,
textura, paleta (incluido el blanco de la marca, medido en sus fotos), tipografías y logo.
La estructura y los estilos no se tocan por negocio. Ejemplo completo: ejemplo/marca-ejemplo.json.

Estructura:
- Barra de un solo vidrio satinado, sin tinte, que flota sobre la cabecera y toma su color; logo
  en negativo, menú en el blanco de la marca y botón de WhatsApp. En el celular llega por detrás
  del reloj (viewport-fit=cover y env(safe-area-inset-top)) y lleva menú de tres líneas.
- Cabecera en dos partes: la textura del lugar con los textos y la foto del negocio, unidas por
  una sombra, con una ondulación de dos líneas en colores de la marca. En el celular, la textura
  es solo una franja con el título; abajo, la foto con la ondulación y los textos sobre el blanco.
- Tres recuadros con íconos de línea en círculos del color de detalle.
- Instalaciones: foto real y lista con tildes.
- Franja final con foto del lugar y la dirección.
- WhatsApp flotante en el celular.
Los textos van más grandes que en una página real: el negocio ve el mockup en chiquito.

Las rutas de marca.json son relativas al propio marca.json. Las tipografías son woff2
(se bajan con npm: @fontsource/<fuente>); si falta una, se usa la letra del sistema y se avisa.
"""
import base64
import html
import io
import json
import os
import re
import sys

from PIL import Image, ImageOps

ICONOS = {
    "lancha": '<path d="M3 16h18l-2.6 4H5.6z"/><path d="M6 16l1.5-5h9L18 16"/><path d="M9 11V7h5l2 4"/><path d="M2 21.5c1.5 0 1.5-.8 3-.8s1.5.8 3 .8 1.5-.8 3-.8 1.5.8 3 .8 1.5-.8 3-.8 1.5.8 3 .8"/>',
    "reloj": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "llave": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6"/>',
    "estrella": '<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>',
    "calendario": '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "telefono": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "corazon": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "tijera": '<circle cx="6" cy="7" r="2.6"/><circle cx="6" cy="17" r="2.6"/><path d="M8.2 8.4L20 17M8.2 15.6L20 7"/>',
    "casa": '<path d="M3.5 11L12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>',
    "auto": '<path d="M4 16v-4l2-5h12l2 5v4"/><path d="M3 16h18v3H3z"/><circle cx="7.5" cy="16" r="1.2"/><circle cx="16.5" cy="16" r="1.2"/>',
    "escudo": '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8-7.5 9.5-4.3-1.5-7.5-4.9-7.5-9.5V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "herramienta": '<path d="M14.5 5.5l4 4-9.5 9.5H5v-4z"/><path d="M12.5 7.5l4 4"/>',
    "hoja": '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19l7-7"/>',
}

# Grano del repertorio (--grano del panel)
GRANO = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='g'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix "
         "values='0 0 0 0 .5 0 0 0 0 .55 0 0 0 0 .58 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' "
         "filter='url(%23g)' opacity='.16'/%3E%3C/svg%3E\")")

COLORES = ("principal", "oscuro", "boton", "detalle", "ola1", "ola2", "blanco", "tilde")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a):
    return "rgba(%d,%d,%d,%s)" % (*rgb(h), a)


def esc(s):
    return html.escape(str(s), quote=True)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ruta_marca = os.path.abspath(sys.argv[1])
    base = os.path.dirname(ruta_marca)
    M = json.load(open(ruta_marca, encoding="utf8"))
    avisos = []

    def ruta(p):
        return p if os.path.isabs(p) else os.path.join(base, p)

    def foto(clave, ancho, calidad=80):
        f = M["fotos"][clave]
        im = ImageOps.exif_transpose(Image.open(ruta(f["ruta"]))).convert("RGB")
        if f.get("recorte"):
            im = im.crop(tuple(f["recorte"]))
        if im.width > ancho:
            im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, "JPEG", quality=f.get("calidad", calidad))
        return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

    def pos(clave, defecto):
        return M["fotos"][clave].get("pos", defecto)

    C = M["colores"]
    falta = [c for c in COLORES if not re.fullmatch(r"#[0-9A-Fa-f]{6}", C.get(c, ""))]
    if falta:
        sys.exit("Faltan colores en marca.json (#rrggbb): %s" % ", ".join(falta))
    T = M["textos"]

    # tipografías
    fuentes, fam_titulo, fam_texto = "", "sans-serif", "sans-serif"
    tit = M.get("tipografias", {}).get("titulo", {})
    tex = M.get("tipografias", {}).get("texto", {})
    if tit.get("archivo") and os.path.exists(ruta(tit["archivo"])):
        b64 = base64.b64encode(open(ruta(tit["archivo"]), "rb").read()).decode()
        fuentes += "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s);font-weight:100 900;font-stretch:50%% 125%%;font-style:%s}" % (
            tit["familia"], b64, tit.get("estilo", "normal"))
        fam_titulo = "'%s',sans-serif" % tit["familia"]
    else:
        avisos.append("sin tipografía de títulos: se usa la del sistema")
    for peso, archivo in (tex.get("archivos") or {}).items():
        if os.path.exists(ruta(archivo)):
            b64 = base64.b64encode(open(ruta(archivo), "rb").read()).decode()
            fuentes += "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s);font-weight:%s}" % (tex["familia"], b64, peso)
            fam_texto = "'%s',sans-serif" % tex["familia"]
        else:
            avisos.append("no encuentro %s" % archivo)
    estilo_t = tit.get("estilo", "normal")
    peso_t = tit.get("peso", 800)
    ancho_t = tit.get("ancho", "100%")

    # logo (versión en negativo, para leerse sobre el vidrio) y WhatsApp oficial
    logo = "data:image/png;base64," + base64.b64encode(open(ruta(M["logo"]), "rb").read()).decode()
    wa_paths = ""
    if M.get("whatsapp_svg") and os.path.exists(ruta(M["whatsapp_svg"])):
        wa_paths = "".join(re.findall(r"<path[^>]*/>", open(ruta(M["whatsapp_svg"]), encoding="utf8").read()))
        wa_paths = re.sub(r'\s(class|fill)="[^"]*"', "", wa_paths)
    else:
        avisos.append("sin whatsapp_svg (logo oficial de Meta): los botones van sin ícono y no hay botón flotante")
    WA = lambda color: '<svg viewBox="0 0 720 720" fill="%s" aria-hidden="true">%s</svg>' % (color, wa_paths) if wa_paths else ""

    def I(k, s=26):
        cuerpo = ICONOS.get(k, k if k.startswith("<") else ICONOS["check"])
        return ('<svg viewBox="0 0 24 24" width="%d" height="%d" fill="none" stroke="currentColor" stroke-width="1.8" '
                'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (s, s, cuerpo))

    negocio = foto("negocio", 1500)
    textura = foto("textura", 1400, 78)
    instal = foto("instalaciones", 800, 85)
    banda = foto("banda", 1600, 78)

    blanco, ola1, ola2 = C["blanco"], C["ola1"], C["ola2"]
    ola = ('<svg class="ola" viewBox="0 0 1440 110" preserveAspectRatio="none" aria-hidden="true">'
           '<path d="M0 70 C 280 112, 560 30, 840 64 S 1260 104, 1440 56 V110 H0Z" fill="%s"/>'
           '<path d="M0 58 C 280 100, 560 18, 840 52 S 1260 92, 1440 44" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>'
           '<path d="M0 68 C 280 110, 560 28, 840 62 S 1260 102, 1440 54" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/></svg>') % (blanco, ola1, ola2)
    ola_m = ('<svg class="ola-m" viewBox="0 0 390 40" preserveAspectRatio="none" aria-hidden="true">'
             '<path d="M0 26 C 100 42, 200 10, 290 27 S 365 38, 390 24 V40 H0Z" fill="%s"/>'
             '<path d="M0 19 C 100 35, 200 3, 290 20 S 365 31, 390 17" fill="none" stroke="%s" stroke-width="2.5"/>'
             '<path d="M0 25 C 100 41, 200 9, 290 26 S 365 37, 390 23" fill="none" stroke="%s" stroke-width="2.5"/></svg>') % (blanco, ola1, ola2)

    o, p, bt, dt = C["oscuro"], C["principal"], C["boton"], C["detalle"]
    texto_boton = C.get("texto_boton", blanco)
    css = f"""{fuentes}
:root{{--principal:{p};--oscuro:{o};--boton:{bt};--detalle:{dt};--blanco:{blanco};--tilde:{C['tilde']};--grano:{GRANO}}}
*{{box-sizing:border-box;margin:0}}body{{font-family:{fam_texto};color:#1d2433;background:var(--blanco);font-size:17px}}
.t{{font-family:{fam_titulo};font-style:{estilo_t};font-weight:{peso_t};font-stretch:{ancho_t};letter-spacing:-.01em;text-wrap:balance}}
header{{position:absolute;top:0;left:0;right:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:24px;padding:12px 44px;
 background-color:rgba(255,255,255,.10);background-image:var(--grano),linear-gradient(180deg,rgba(255,255,255,.14),rgba(255,255,255,.04));
 -webkit-backdrop-filter:blur(22px) saturate(1.7);backdrop-filter:blur(22px) saturate(1.7);border-bottom:1px solid rgba(255,255,255,.26);
 box-shadow:inset 0 1px 0 rgba(255,255,255,.32),0 10px 26px -14px {rgba(o, .55)}}}
header .logo{{height:62px;width:auto;display:block}}
nav{{display:flex;gap:32px;font-weight:600;font-size:19px;color:var(--blanco);letter-spacing:.01em}}
.btn{{display:inline-flex;align-items:center;gap:9px;border-radius:999px;font-weight:600;color:{texto_boton};text-shadow:0 1px 1px rgba(0,0,0,.3);
 background-color:{rgba(bt, .92)};background-image:var(--grano);border:1px solid rgba(255,255,255,.35);box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 8px 18px -8px {rgba(bt, .8)}}}
.btn svg{{width:20px;height:20px}}header .btn{{padding:12px 20px;font-size:15.5px}}
.menu{{display:none}}
.hero{{position:relative;overflow:hidden;display:grid;grid-template-columns:53% 47%;min-height:560px;background:var(--oscuro)}}
.hero .ft{{background:url({negocio}) {pos('negocio', '70% 50%')}/cover;position:relative;z-index:1}}
.hero .tx{{position:relative;z-index:2;padding:150px 48px 120px 44px;display:flex;flex-direction:column;justify-content:center;gap:18px;color:#fff;
 background:linear-gradient(90deg,{rgba(o, .42)},{rgba(o, .22)}),url({textura}) left center/auto 120%;box-shadow:18px 0 36px -6px rgba(0,0,0,.55),6px 0 10px -4px rgba(0,0,0,.4)}}
.hero h1{{font-size:54px;line-height:1.02;color:var(--blanco);text-shadow:0 2px 8px rgba(0,0,0,.35)}}
.raya{{width:72px;height:5px;border-radius:999px;background:var(--boton)}}
.hero p{{font-size:20px;line-height:1.45;color:var(--blanco);max-width:520px}}
.acc{{display:flex;gap:14px;flex-wrap:wrap}}.acc .btn{{padding:14px 24px;font-size:17px}}
.sec{{display:inline-flex;align-items:center;padding:13px 24px;border-radius:999px;border:1.5px solid {rgba(blanco, .75)};color:var(--blanco);font-weight:600;font-size:17px;background:{rgba(blanco, .06)}}}
.st{{font-size:15px;color:{rgba(blanco, .88)}}}.st b{{color:var(--detalle)}}
.ola{{position:absolute;left:0;right:0;bottom:-1px;width:100%;height:96px;z-index:3}}
.feat{{display:grid;grid-template-columns:repeat(3,1fr);padding:22px 60px 40px;text-align:center}}
.feat div{{padding:6px 20px;display:grid;justify-items:center;gap:6px}}.feat div+div{{border-left:1px solid {rgba(p, .15)}}}
.feat .i{{width:76px;height:76px;margin-bottom:14px;border-radius:999px;display:grid;place-items:center;color:var(--oscuro);background-color:var(--detalle);background-image:var(--grano);
 border:1px solid rgba(255,255,255,.6);box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 8px 16px -10px {rgba(dt, .9)}}}
.feat .i svg{{width:38px;height:38px}}.feat b{{font-family:{fam_titulo};font-style:{estilo_t};font-weight:700;font-size:21px;color:var(--principal)}}.feat span{{color:#4d5468;font-size:16.5px}}
.inst{{display:grid;grid-template-columns:44% 1fr;gap:44px;align-items:center;padding:30px 60px 48px;background:{rgba(blanco, .55)}}}
.inst .foto{{height:330px;border-radius:22px;background:url({instal}) {pos('instalaciones', 'center 40%')}/cover;box-shadow:0 18px 40px -18px {rgba(o, .55)}}}
.inst h2{{font-size:36px;color:var(--oscuro)}}.inst p{{color:var(--principal);font-size:19px;margin:8px 0 16px}}
.inst ul{{list-style:none;padding:0;display:grid;gap:10px;font-size:18.5px}}.inst li{{display:flex;gap:10px;align-items:center}}.inst li svg{{color:var(--tilde);flex:none}}
.banda{{position:relative;height:230px;background:url({banda}) {pos('banda', 'center 62%')}/cover;display:flex;align-items:center;justify-content:flex-end;padding:0 60px}}
.banda:before{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,{rgba(o, 0)} 30%,{rgba(o, .7)})}}
.banda div{{position:relative;color:var(--blanco);display:flex;gap:12px;align-items:flex-start;max-width:420px}}.banda b{{font-family:{fam_titulo};font-style:{estilo_t};font-weight:700;font-size:24px;display:block}}
.cartel,.resto{{display:flex;flex-direction:column;gap:18px}}.ola-m{{display:none}}.wa{{display:none}}
@media(max-width:640px){{body{{font-size:16px}}header{{padding:calc(10px + env(safe-area-inset-top)) 16px 10px}}header .logo{{height:46px}}nav,header .btn{{display:none}}
.menu{{display:grid;gap:5px;background:none;border:0;padding:8px}}.menu span{{display:block;width:26px;height:2.5px;border-radius:2px;background:var(--blanco)}}
.hero{{display:flex;flex-direction:column;min-height:0;background:var(--blanco)}}.hero .tx{{display:contents}}.ola{{display:none}}
.cartel{{order:0;gap:12px;padding:calc(94px + env(safe-area-inset-top)) 18px 20px;color:var(--blanco);background:linear-gradient(90deg,{rgba(o, .42)},{rgba(o, .22)}),url({textura}) left center/auto 150%;box-shadow:0 10px 22px -6px rgba(0,0,0,.5);position:relative;z-index:2}}
.hero .ft{{order:1;height:240px;flex:none;position:relative}}.ola-m{{display:block;position:absolute;left:0;right:0;bottom:-1px;width:100%;height:34px}}
.resto{{order:2;gap:14px;padding:12px 18px 26px}}.resto p{{color:#2b3245}}.resto .st{{color:#4d5468}}.resto .st b{{color:var(--detalle);filter:brightness(.9)}}.resto .sec{{color:var(--principal);border-color:{rgba(p, .5)};background:{rgba(blanco, .6)}}}
.hero h1{{font-size:30px}}.hero p{{font-size:17px}}.acc .btn,.sec{{font-size:15.5px;padding:12px 18px}}
.feat{{grid-template-columns:1fr;padding:14px 18px 24px;gap:6px}}.feat div+div{{border-left:0;border-top:1px solid {rgba(p, .12)};padding-top:14px}}.feat .i{{width:66px;height:66px;margin-bottom:10px}}.feat .i svg{{width:32px;height:32px}}
.inst{{grid-template-columns:1fr;padding:22px 18px 30px;gap:18px}}.inst .foto{{height:230px}}.inst h2{{font-size:28px}}
.banda{{justify-content:flex-start;padding:0 18px}}.banda:before{{background:{rgba(o, .55)}}}.banda b{{font-size:21px}}
.wa{{display:grid;place-items:center;position:fixed;right:18px;bottom:20px;z-index:20;width:62px;height:62px;border-radius:999px;background:#25D366;box-shadow:0 10px 24px -6px {rgba(o, .45)},0 3px 8px {rgba(o, .25)}}}.wa svg{{width:34px;height:34px}}}}
"""
    rec = T["recuadros"][:3]
    inst = T["instalaciones"]
    nombre = esc(M["nombre"])
    pagina = f"""<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{nombre}</title><style>{css}</style></head><body>
<header><img class="logo" src="{logo}" alt="{nombre}"><nav>{''.join('<span>%s</span>' % esc(x) for x in T['menu'])}</nav>
<span class="btn">{WA(blanco)}{esc(T['boton'])}</span><button class="menu" aria-label="Abrir el menú"><span></span><span></span><span></span></button></header>
<section class="hero"><div class="tx"><div class="cartel"><h1 class="t">{esc(T['titulo'])}</h1><div class="raya"></div></div>
<div class="resto"><p>{esc(T['bajada'])}</p>
<div class="acc"><span class="btn">{WA(blanco)}{esc(T['boton'])}</span><span class="sec">{esc(T['secundario'])}</span></div>
<span class="st"><b>★★★★★</b> {esc(T['estrellas'])}</span></div></div><div class="ft">{ola_m}</div>{ola}</section>
<section class="feat">{''.join('<div><span class="i">%s</span><b>%s</b><span>%s</span></div>' % (I(r['icono'], 28), esc(r['titulo']), esc(r['texto'])) for r in rec)}</section>
<section class="inst"><div class="foto" role="img" aria-label="{esc(inst.get('foto_alt', inst['titulo']))}"></div><div><h2 class="t">{esc(inst['titulo'])}</h2>
<p>{esc(inst['bajada'])}</p>
<ul>{''.join('<li>%s%s</li>' % (I('check', 22), esc(x)) for x in inst['lista'])}</ul></div></section>
<section class="banda"><div>{I('pin', 34)}<span><b>{esc(T['banda']['titulo'])}</b>{esc(T['banda']['texto'])}</span></div></section>
{'<a class="wa" aria-label="Escribir por WhatsApp">%s</a>' % WA('#fff') if wa_paths else ''}</body></html>"""
    if "—" in pagina or "–" in pagina:
        sys.exit("Hay un guion largo o semilargo en los textos de marca.json")
    open(sys.argv[2], "w", encoding="utf8").write(pagina)
    for a in avisos:
        print("AVISO", a)
    print("ok", len(pagina) // 1024, "KB")


if __name__ == "__main__":
    main()
