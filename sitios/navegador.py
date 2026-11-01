#!/usr/bin/env python3
"""Controles de un sitio en un navegador real (Chromium), a 390 px (celular) y 1360 px (computadora).

Completa a revisar.py con lo que solo se puede medir con la página armada y el estilo calculado:

    FALLA  scroll lateral (el documento es más ancho que la ventana)
    FALLA  body.bottom - pie.bottom distinto de 0 (queda caja del body debajo del pie y se ve al rebotar)
    FALLA  elemento position:fixed que cubre la pantalla con mix-blend-mode o backdrop-filter (rompe lo fijo en
           iPhone; ver la memoria area-segura-iphone)
    FALLA  imágenes rotas, archivos del sitio que responden 404 y errores de consola
    FALLA  botones con contraste menor a 4,5:1 entre el texto y su fondo
    AVISO  controles de menos de 44 px en el celular
    AVISO  LCP en el celular de más de 2,5 s (con la red y el procesador limitados como Lighthouse en celular)

Deja capturas con el scroll en 0 (pantalla y página completa) para el revisor visual. Las capturas de una página
scrolleada dibujan corridos los elementos fijos: por eso se vuelve arriba antes de sacarlas.

Lo que Chromium no reproduce de un iPhone (el compositor de WebKit, los env() del área segura) no se puede dar por
resuelto con esto: queda para el revisor técnico.

Uso:
    python3 sitios/navegador.py CARPETA_O_URL [--rutas / /otra.html] [--capturas DIR] [--json] [--sin-limitar]

Una carpeta (por ejemplo dist/) se sirve en 127.0.0.1 y se bloquea lo que pide a otros dominios (Analytics, Clarity),
así la prueba no depende de la red. Una URL se prueba tal cual, en vivo.
Necesita Playwright con Chromium (pip install playwright; python3 -m playwright install chromium). Solo lee.
Sale con código 1 si hay alguna FALLA.
"""
import argparse
import functools
import http.server
import json
import os
import pathlib
import sys
import threading
import urllib.parse

ANCHOS = [  # (ancho, alto, celular)
    (390, 844, True),
    (1360, 900, False),
]
MIN_CONTRASTE = 4.5
MIN_TOQUE = 44
MAX_LCP_MS = 2500
# Red y procesador de Lighthouse para celular ("Slow 4G" y 4x de procesador).
RED_CELULAR = {"offline": False, "latency": 150, "downloadThroughput": 1638.4 * 1024 / 8, "uploadThroughput": 675 * 1024 / 8}
CPU_CELULAR = 4

hallazgos = []


def anotar(nivel, ancho, ruta, regla, detalle):
    hallazgos.append({"nivel": nivel, "ancho": ancho, "ruta": ruta, "regla": regla, "detalle": detalle})


# ---------------------------------------------------------------- medición en la página

MEDIR = r"""
() => {
  const vw = innerWidth, vh = innerHeight;
  const desc = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    else if (typeof el.className === 'string' && el.className.trim()) s += '.' + el.className.trim().split(/\s+/)[0];
    const t = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 30);
    return t ? `${s} «${t}»` : s;
  };
  const rgba = (s) => {
    const m = /^rgba?\(([^)]+)\)$/.exec(s || '');
    if (!m) return null;
    const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(parseFloat);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const sobre = (arriba, abajo) => {
    const a = arriba.a + abajo.a * (1 - arriba.a);
    const c = (k) => a ? (arriba[k] * arriba.a + abajo[k] * abajo.a * (1 - arriba.a)) / a : 0;
    return { r: c('r'), g: c('g'), b: c('b'), a };
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const hex = (c) => '#' + [c.r, c.g, c.b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  const visible = (el, cs) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0;
  };

  // ancho y pie
  const res = { vw, scrollWidth: document.documentElement.scrollWidth };
  const pies = document.querySelectorAll('footer');
  const pie = pies[pies.length - 1];
  res.pie = pie ? Math.round(document.body.getBoundingClientRect().bottom - pie.getBoundingClientRect().bottom) : null;
  // qué se sale por la derecha (para poder arreglar el scroll lateral)
  res.anchos = [];
  if (res.scrollWidth > vw + 1) {
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.right > vw + 1 && r.width > 0) {
        let p = el.parentElement, recortado = false;
        while (p && p !== document.body) {
          const o = getComputedStyle(p).overflowX;
          if (o === 'hidden' || o === 'auto' || o === 'scroll' || o === 'clip') { recortado = true; break; }
          p = p.parentElement;
        }
        if (!recortado) res.anchos.push(`${desc(el)} llega a ${Math.round(r.right)} px`);
      }
      if (res.anchos.length >= 3) break;
    }
  }

  // elementos fijos con mezcla o desenfoque
  res.fijos = [];
  for (const el of document.querySelectorAll('*')) {
    for (const ps of [null, '::before', '::after']) {
      const cs = getComputedStyle(el, ps);
      if (cs.position !== 'fixed') continue;
      if (ps && (cs.content === 'none' || cs.content === 'normal')) continue;
      const mezcla = cs.mixBlendMode && cs.mixBlendMode !== 'normal' ? cs.mixBlendMode : null;
      const bf = cs.backdropFilter || cs.webkitBackdropFilter || 'none';
      const desenfoque = bf !== 'none' ? bf : null;
      if (!mezcla && !desenfoque) continue;
      let w, h;
      if (!ps) {
        const r = el.getBoundingClientRect();
        w = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0));
        h = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      } else { w = Math.min(parseFloat(cs.width) || 0, vw); h = Math.min(parseFloat(cs.height) || 0, vh); }
      res.fijos.push({ el: desc(el) + (ps || ''), mezcla, desenfoque, cubre: Math.round(100 * w * h / (vw * vh)) });
    }
  }

  // imágenes rotas
  res.rotas = [...document.images].filter((i) => i.currentSrc && i.complete && i.naturalWidth === 0).map((i) => i.currentSrc);

  // contraste de botones: button, role=button, inputs de envío, y enlaces con fondo propio (con forma de botón)
  res.contraste = []; res.sinMedir = [];
  for (const el of document.querySelectorAll('a[href], button, [role=button], input[type=submit], input[type=button]')) {
    const cs = getComputedStyle(el);
    if (!visible(el, cs)) continue;
    const texto = (el.innerText || el.value || '').trim();
    if (!texto) continue;  // botones solo con ícono: el contraste de un ícono se mide aparte (3:1)
    const propio = rgba(cs.backgroundColor);
    const conFondo = cs.backgroundImage !== 'none' || (propio && propio.a > 0);
    if (el.tagName === 'A' && !conFondo) continue;  // enlace de texto, no botón
    const capas = []; let imagen = false;
    for (let n = el; n; n = n.parentElement) {
      const c = getComputedStyle(n);
      if (c.backgroundImage !== 'none') { imagen = true; break; }
      const col = rgba(c.backgroundColor);
      if (!col) { imagen = true; break; }
      if (col.a > 0) capas.push(col);
      if (col.a >= 1) break;
    }
    if (imagen) { res.sinMedir.push(desc(el)); continue; }
    let fondo = { r: 255, g: 255, b: 255, a: 1 };
    for (const c of capas.reverse()) fondo = sobre(c, fondo);
    const tinta = rgba(cs.color);
    if (!tinta) { res.sinMedir.push(desc(el)); continue; }
    const t = sobre(tinta, fondo);
    const l1 = lum(t), l2 = lum(fondo);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    res.contraste.push({ el: desc(el), texto: hex(t), fondo: hex(fondo), ratio: Math.round(ratio * 100) / 100 });
  }

  // controles chicos (se mira solo en el celular). Los enlaces dentro de un párrafo (display inline) no cuentan.
  res.chicos = [];
  for (const el of document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button]')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'inline' || !visible(el, cs)) continue;
    const r = el.getBoundingClientRect();
    if (r.height < __MIN__ || r.width < __MIN__) res.chicos.push(`${desc(el)} ${Math.round(r.width)}×${Math.round(r.height)}`);
  }
  return res;
}
""".replace("__MIN__", str(MIN_TOQUE))

RECORRER = """
async () => {
  const pausa = (ms) => new Promise((r) => setTimeout(r, ms));
  // instant: con scroll-behavior:smooth, cada salto sería una animación que el siguiente interrumpe
  const ir = (y) => scrollTo({ top: y, left: 0, behavior: 'instant' });
  for (let y = 0; y < document.documentElement.scrollHeight; y += Math.round(innerHeight * 0.7)) { ir(y); await pausa(120); }
  ir(document.documentElement.scrollHeight); await pausa(300);
  document.querySelectorAll('img[loading=lazy]').forEach((i) => { i.loading = 'eager'; });
  await Promise.race([
    Promise.all([...document.images].map((i) => i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; }))),
    pausa(6000),
  ]);
  ir(0); await pausa(900);
}
"""

LCP = """
() => new Promise((listo) => {
  let v = null;
  new PerformanceObserver((l) => { const e = l.getEntries(); if (e.length) v = e[e.length - 1].startTime; })
    .observe({ type: 'largest-contentful-paint', buffered: true });
  setTimeout(() => listo(v), 1500);
})
"""


# ---------------------------------------------------------------- servidor local

class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servir(carpeta):
    manejador = functools.partial(_Silencioso, directory=str(carpeta))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


# ---------------------------------------------------------------- recorrido

def probar(navegador, base, ruta, local, capturas, limitar):
    url = urllib.parse.urljoin(base + "/", ruta.lstrip("/"))
    origen = urllib.parse.urlparse(url).netloc
    nombre = (ruta.strip("/").replace("/", "-").replace(".html", "") or "inicio")
    propio = lambda u: urllib.parse.urlparse(u).netloc == origen

    for ancho, alto, celular in ANCHOS:
        ctx = navegador.new_context(viewport={"width": ancho, "height": alto}, device_scale_factor=2 if celular else 1,
                                    is_mobile=celular, has_touch=celular, locale="es-AR")
        pagina = ctx.new_page()
        errores, faltan = [], []
        if local:
            pagina.route(lambda u: not propio(u), lambda r: r.abort())
        pagina.on("pageerror", lambda e: errores.append(f"error de JavaScript: {e}"[:200]))
        pagina.on("console", lambda m: errores.append(f"consola: {m.text}"[:200])
                  if m.type == "error" and (propio(m.location.get("url") or url) or not local) else None)
        pagina.on("response", lambda r: faltan.append(f"{r.status} {r.url}") if r.status >= 400 and propio(r.url) else None)
        pagina.on("requestfailed", lambda r: faltan.append(f"no cargó {r.url}") if propio(r.url) else None)

        try:
            pagina.goto(url, wait_until="load", timeout=45000)
        except Exception as e:
            anotar("FALLA", ancho, ruta, "carga", f"la página no cargó: {e}"[:200])
            ctx.close()
            continue
        pagina.evaluate(RECORRER)
        m = pagina.evaluate(MEDIR)

        if m["scrollWidth"] > m["vw"] + 1:
            anotar("FALLA", ancho, ruta, "scroll-lateral", f"el documento mide {m['scrollWidth']} px de ancho y la ventana {m['vw']}"
                   + (": " + "; ".join(m["anchos"]) if m["anchos"] else ""))
        if m["pie"] is None:
            anotar("AVISO", ancho, ruta, "pie", "la página no tiene <footer>: no se puede medir body.bottom - pie.bottom")
        elif abs(m["pie"]) > 1:
            anotar("FALLA", ancho, ruta, "pie", f"body.bottom - pie.bottom = {m['pie']} px (tiene que dar 0: lo que sobra se ve al rebotar)")
        for f in m["fijos"]:
            if f["cubre"] >= 90:
                que = " y ".join(x for x in (f["mezcla"] and f"mix-blend-mode:{f['mezcla']}", f["desenfoque"] and f"backdrop-filter:{f['desenfoque']}") if x)
                anotar("FALLA", ancho, ruta, "fijo-mezcla", f"{f['el']} es position:fixed, cubre el {f['cubre']} % de la pantalla y tiene {que}: "
                       "en iPhone rompe lo fijo y pinta fuera de la página. Pasarlo a absolute sobre el body")
        for i in m["rotas"]:
            anotar("FALLA", ancho, ruta, "imagenes", f"imagen rota: {i}")
        for f in dict.fromkeys(faltan):
            anotar("FALLA", ancho, ruta, "archivos", f)
        for e in dict.fromkeys(errores):
            anotar("FALLA", ancho, ruta, "consola", e)

        malos = {}
        for c in m["contraste"]:
            if c["ratio"] < MIN_CONTRASTE:
                malos.setdefault((c["texto"], c["fondo"], c["ratio"]), []).append(c["el"])
        for (t, f, r), els in malos.items():
            anotar("FALLA", ancho, ruta, "contraste", f"texto {t} sobre {f}: {str(r).replace('.', ',')}:1 (mínimo 4,5:1) en "
                   f"{len(els)} {'botón' if len(els) == 1 else 'botones'}, por ejemplo {els[0]}")
        if m["sinMedir"]:
            anotar("AVISO", ancho, ruta, "contraste", f"{len(m['sinMedir'])} botones con fondo de imagen o degradado: el contraste se mira a ojo "
                   f"(por ejemplo {m['sinMedir'][0]})")
        if celular and m["chicos"]:
            grupos = {}
            for c in m["chicos"]:
                grupos[c] = grupos.get(c, 0) + 1
            ejemplos = [c + (f" (×{k})" if k > 1 else "") for c, k in grupos.items()]
            anotar("AVISO", ancho, ruta, "toque", f"{len(m['chicos'])} controles de menos de {MIN_TOQUE} px: " + "; ".join(ejemplos[:5])
                   + ("…" if len(ejemplos) > 5 else ""))

        if capturas:
            capturas.mkdir(parents=True, exist_ok=True)
            pagina.evaluate("() => scrollTo({ top: 0, left: 0, behavior: 'instant' })")
            pagina.wait_for_timeout(300)
            pagina.screenshot(path=str(capturas / f"{nombre}-{ancho}-pantalla.png"))
            pagina.screenshot(path=str(capturas / f"{nombre}-{ancho}-completa.png"), full_page=True)
        ctx.close()

        if celular:
            medir_lcp(navegador, url, ancho, alto, ruta, local, limitar, propio)


def medir_lcp(navegador, url, ancho, alto, ruta, local, limitar, propio):
    ctx = navegador.new_context(viewport={"width": ancho, "height": alto}, device_scale_factor=2, is_mobile=True,
                                has_touch=True, locale="es-AR")
    pagina = ctx.new_page()
    if local:
        pagina.route(lambda u: not propio(u), lambda r: r.abort())
    if limitar:
        cdp = ctx.new_cdp_session(pagina)
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", RED_CELULAR)
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": CPU_CELULAR})
    try:
        pagina.goto(url, wait_until="load", timeout=90000)
        lcp = pagina.evaluate(LCP)
    except Exception as e:
        lcp = None
        anotar("AVISO", ancho, ruta, "lcp", f"no se pudo medir el LCP: {e}"[:200])
    ctx.close()
    if lcp is None:
        return
    como = "con red y procesador de celular" if limitar else "sin limitar la red"
    texto = f"LCP de {lcp / 1000:.1f} s ({como})".replace(".", ",")
    if lcp > MAX_LCP_MS:
        anotar("AVISO", ancho, ruta, "lcp", texto + f": más de {MAX_LCP_MS / 1000:.1f} s".replace(".", ","))
    else:
        anotar("INFO", ancho, ruta, "lcp", texto)


def main():
    ap = argparse.ArgumentParser(description="Controles de un sitio en Chromium a 390 y 1360 px (solo lee).")
    ap.add_argument("objetivo", help="carpeta armada (por ejemplo dist/) o URL")
    ap.add_argument("--rutas", nargs="+", default=["/"], help="páginas a probar dentro del sitio (por defecto /)")
    ap.add_argument("--capturas", help="carpeta donde dejar las capturas para el revisor visual")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sin-limitar", action="store_true", help="mide el LCP sin limitar la red ni el procesador")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright

    local = not a.objetivo.startswith(("http://", "https://"))
    srv = None
    if local:
        carpeta = pathlib.Path(a.objetivo).resolve()
        if not (carpeta / "index.html").exists():
            sys.exit(f"{carpeta} no tiene index.html: pasar la carpeta armada (por ejemplo dist/).")
        srv, base = servir(carpeta)
    else:
        base = a.objetivo.rstrip("/")
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            for ruta in a.rutas:
                probar(navegador, base, ruta, local, pathlib.Path(a.capturas) if a.capturas else None, not a.sin_limitar)
            navegador.close()
    finally:
        if srv:
            srv.shutdown()

    if a.json:
        print(json.dumps(hallazgos, ensure_ascii=False, indent=1))
    else:
        for h in hallazgos:
            print("%-5s %4d px %s  [%s] %s" % (h["nivel"], h["ancho"], h["ruta"], h["regla"], h["detalle"]))
        fallas = sum(1 for h in hallazgos if h["nivel"] == "FALLA")
        avisos = sum(1 for h in hallazgos if h["nivel"] == "AVISO")
        print("\n%d fallas, %d avisos." % (fallas, avisos))
        if a.capturas:
            print("Capturas en", a.capturas)
    sys.exit(1 if any(h["nivel"] == "FALLA" for h in hallazgos) else 0)


if __name__ == "__main__":
    main()
