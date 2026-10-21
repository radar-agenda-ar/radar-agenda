#!/usr/bin/env python3
"""Radar de Agenda - recolector de datos.

Solo biblioteca estandar de Python 3.9+ (sin pip, sin claves, sin IA).
Lee RSS de medios, tendencias de X (trends24 / getdaytrends), Google Trends AR,
calendario del INDEC, Boletin Oficial y CEPA; agrupa los titulares en temas con
heuristicas de texto y escribe sitio/data/tendencias.json (contrato en
notas/ESQUEMA.md) mas una copia en sitio/data/archivo/AAAA-MM-DD.json.

Uso:  python3 scripts/recolectar.py
"""
import html
import json
import math
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Argentina/Buenos_Aires")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "sitio" / "data" / "tendencias.json"
ARCHIVO = RAIZ / "sitio" / "data" / "archivo"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 20
VENTANA_HORAS = 24
MAX_TEMAS = 60

# --------------------------------------------------------------------------
# Fuentes
# --------------------------------------------------------------------------
# (medio, nombre de feed, url, seccion por defecto si el link no la trae)
FEEDS = [
    ("Infobae", "General", "https://www.infobae.com/arc/outboundfeeds/rss/", None),
    ("Infobae", "Política", "https://www.infobae.com/arc/outboundfeeds/rss/category/politica/", "politica"),
    ("Infobae", "Economía", "https://www.infobae.com/arc/outboundfeeds/rss/category/economia/", "economia"),
    ("Infobae", "Sociedad", "https://www.infobae.com/arc/outboundfeeds/rss/category/sociedad/", "sociedad"),
    ("Infobae", "Deportes", "https://www.infobae.com/arc/outboundfeeds/rss/category/deportes/", "deportes"),
    ("Infobae", "Espectáculos", "https://www.infobae.com/arc/outboundfeeds/rss/category/entretenimiento/", "espectaculos"),
    ("Clarín", "General", "https://www.clarin.com/rss/lo-ultimo/", None),
    ("Clarín", "Política", "https://www.clarin.com/rss/politica/", "politica"),
    ("Clarín", "Economía", "https://www.clarin.com/rss/economia/", "economia"),
    ("Clarín", "Sociedad", "https://www.clarin.com/rss/sociedad/", "sociedad"),
    ("Clarín", "Deportes", "https://www.clarin.com/rss/deportes/", "deportes"),
    ("Clarín", "Espectáculos", "https://www.clarin.com/rss/espectaculos/", "espectaculos"),
    ("La Nación", "General", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/", None),
    ("La Nación", "Política", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/politica/", "politica"),
    ("La Nación", "Economía", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/", "economia"),
    ("La Nación", "Sociedad", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/sociedad/", "sociedad"),
    ("La Nación", "Deportes", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/deportes/", "deportes"),
    ("La Nación", "Espectáculos", "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/espectaculos/", "espectaculos"),
    ("Página/12", "Portada", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/portada", None),
    ("Página/12", "El País", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/el-pais/notas", "politica"),
    ("Página/12", "Economía", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/economia/notas", "economia"),
    ("Página/12", "Sociedad", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/sociedad/notas", "sociedad"),
    ("Página/12", "Deportes", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/deportes/notas", "deportes"),
    ("Página/12", "Espectáculos", "https://www.pagina12.com.ar/arc/outboundfeeds/rss/suplementos/cultura-y-espectaculos/notas", "espectaculos"),
    ("Ámbito", "General", "https://www.ambito.com/rss/pages/home.xml", None),
    ("Ámbito", "Política", "https://www.ambito.com/rss/pages/politica.xml", "politica"),
    ("Ámbito", "Economía", "https://www.ambito.com/rss/pages/economia.xml", "economia"),
    ("Ámbito", "Deportes", "https://www.ambito.com/rss/pages/deportes.xml", "deportes"),
    ("Ámbito", "Espectáculos", "https://www.ambito.com/rss/pages/espectaculos.xml", "espectaculos"),
    ("Ámbito", "Últimas", "https://www.ambito.com/rss/pages/ultimas-noticias.xml", None),
    ("TN", "General", "https://tn.com.ar/rss.xml", None),
]

URL_TRENDS24 = "https://trends24.in/argentina/"
URL_GETDAYTRENDS = "https://getdaytrends.com/argentina/"
URL_GOOGLE = "https://trends.google.com/trending/rss?geo=AR"
URL_INDEC = "https://www.indec.gob.ar/Calendario/FiltrosCalendario/dia/{fecha}/es"
URL_INDEC_PAGINA = "https://www.indec.gob.ar/indec/web/Calendario-Fecha-0"
URL_BORA = "https://www.boletinoficial.gob.ar/seccion/primera"
URL_CEPA = "https://centrocepa.com.ar/documentos/informes?format=feed&type=rss"

# Medios por autoridad (para elegir el titulo representativo)
AUTORIDAD = {"La Nación": 3, "Infobae": 3, "Clarín": 3, "Ámbito": 2, "TN": 2, "Página/12": 2}

# Segmento del link -> categoria
SECCION_A_CAT = {
    "politica": "politica", "el-pais": "politica", "elecciones": "politica",
    "economia": "economia", "finanzas": "economia", "negocios": "economia",
    "dolar": "economia", "campo": "economia", "empresas": "economia",
    "sociedad": "social", "policiales": "social", "salud": "social",
    "educacion": "social", "clima": "social", "comunidad": "social",
    "ciudades": "social", "medio-ambiente": "social", "seguridad": "social",
    "deportes": "deportes", "futbol": "deportes", "tenis": "deportes",
    "espectaculos": "espectaculos", "show": "espectaculos", "teleshow": "espectaculos",
    "entretenimiento": "espectaculos", "tv": "espectaculos", "cine": "espectaculos",
    "series": "espectaculos", "famosos": "espectaculos", "musica": "espectaculos",
    "mundo": "otros", "internacional": "otros", "estados-unidos": "otros",
    "tecnologia": "otros", "cultura": "otros", "lifestyle": "otros", "cocina": "otros",
    "videos": "otros", "estilo": "otros", "turismo": "otros", "autos": "otros",
    "ciencia": "otros", "america": "otros", "europa": "otros", "mexico": "otros",
    "opinion": "otros", "viajes": "otros", "juegos": "otros", "horoscopo": "otros",
}

PRIORITARIAS = {"economia", "politica", "trabajo", "jubilaciones", "social"}

# Pronósticos del clima: se descartan salvo que hablen de alertas, inundaciones o destrozos
CLIMA = re.compile(r"\b(clima|pronostico|lluvia|lluvias|lloviznas?|temperatura|calor|frio|nublado|"
                   r"soleado|cielo|smn|servicio meteorologico|como estara el tiempo)\b")
CLIMA_ALARMA = re.compile(r"\b(alerta|alertas|inundacion|inundaciones|inundad[oa]s?|anegad[oa]s?|"
                          r"evacuad[oa]s?|temporal|tormenta fuerte|granizo|tornado|destrozos|"
                          r"danos|victimas|muertos?|emergencia|desbord)")


def es_pronostico_comun(titulo):
    t = norm(titulo)
    return bool(CLIMA.search(t)) and not CLIMA_ALARMA.search(t)

# --------------------------------------------------------------------------
# Utilidades de texto
# --------------------------------------------------------------------------


def quitar_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s):
    return quitar_acentos(s).lower()


STOP = set(norm("""
a al algo algun alguna algunas alguno algunos ante antes aqui asi aun aunque bajo bien cada casi como con contra cual
cuales cuando cuanto de del desde donde dos e el ella ellas ello ellos en entre era eran es esa esas ese eso esos esta
estaba estan estar este esto estos fue fueron ha haber habia han hasta hay hace hacen hacia hizo la las le les lo los
mas me mi mientras mismo mucho muchos muy nada ni no nos nuestro nuestra o os otra otras otro otros para pero poco por
porque que quien quienes se sea segun ser si sido sin sobre solo son su sus tambien tanto te tiene tienen todo toda
todos todas tras tu tus un una unas uno unos usted va vamos van vez y ya yo
asi ahora hoy ayer manana tras luego durante despues dice dijo dicen sera seran seria puede pueden podria podrian
debe deben deberia tiene tendra tendran hubo habra cuanto cuantos cuanta cuantas cual quien donde
lunes martes miercoles jueves viernes sabado domingo enero febrero marzo abril mayo junio julio agosto septiembre
setiembre octubre noviembre diciembre
nuevo nueva nuevos nuevas primer primera primeros ultimo ultima ultimos ultimas gran grandes mejor mejores peor
tras vs video fotos foto minuto minutos hora horas dia dias semana semanas mes meses ano anos
paso pasa pasan pasar vuelve volvio quedo queda siguen sigue seguir mostro muestra claves clave
quien quienes todas cuales cuanto asi aca alli
como cuales
""").split())

# Palabras demasiado comunes en la agenda: cuentan poco y nunca unen titulares por si solas
DEBILES = set(norm("""
gobierno argentina argentino argentinos argentinas milei presidente nacional pais paises gobierno
ministro ministra ministerio dolar peso pesos millones mil anuncio anuncia anuncio
buenos aires bonaerense provincia ciudad mundo caso casos causa cambios cambio
informe datos dato precio precios precio nota noticias noticia
trump estados unidos eeuu usd dolares
""").split())

# Sinonimos simples (para cruzar tendencias / oficiales con titulares)
SINONIMOS = {"ipc": "inflacion", "emae": "actividad", "paritarias": "paritaria"}

# Palabras de organismos que no sirven para cruzar normas del Boletin
OFICIAL_STOP = set(norm("""
resolucion resoluciones disposicion decreto ministerio secretaria administracion nacional direccion general
instituto agencia consejo comision subsecretaria jefatura gabinete ministros republica argentina aviso oficial
oficiales conjunta conjuntas apn mec mecon jgm sgm anexo ley registro
""").split())


def stem(t):
    if len(t) > 4 and t.endswith("es") and not t.endswith("ees"):
        # "jubilaciones" -> "jubilacion", pero "paises" -> "pais"
        return t[:-2] if t[-3] not in "aeiou" or t.endswith("ones") else t[:-1]
    if len(t) > 3 and t.endswith("s"):
        return t[:-1]
    return t


def tokens_de(texto):
    """Devuelve lista de (token_normalizado_stem, es_entidad) en orden."""
    out = []
    crudo = re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ$#@]+", texto)
    inicio = True
    for i, w in enumerate(crudo):
        w2 = w.lstrip("#@$")
        if not w2:
            continue
        n = norm(w2)
        es_ent = False
        if len(w2) >= 2 and w2.isupper() and not w2.isdigit():
            es_ent = True  # siglas: INDEC, BCRA, AFA
        elif w2[0].isupper() and i > 0 and len(w2) >= 3:
            es_ent = True  # nombre propio (no inicio de titular)
        if n.isdigit() or n in STOP or len(n) < 3 and not es_ent:
            continue
        if n in STOP:
            continue
        t = SINONIMOS.get(n, stem(n))
        out.append((t, es_ent))
    return out


def limpiar_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def limpiar_titulo(t):
    t = limpiar_html(t)
    t = re.sub(r"\s+[-|–—]\s+(Infobae|Clarín|La Nación|TN|Ámbito|Página/12|Página12)$", "", t)
    return t


def slug(s, n=60):
    s = re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")
    return s[:n].strip("-") or "tema"


# --------------------------------------------------------------------------
# Red
# --------------------------------------------------------------------------


def bajar(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read()
    return data.decode("utf-8", errors="replace")


def bajar_seguro(url):
    """(texto, None) o (None, mensaje_de_error)."""
    try:
        return bajar(url), None
    except Exception as e:  # noqa: BLE001 - cualquier falla de red no debe romper la corrida
        return None, "%s: %s" % (type(e).__name__, e)


def parse_fecha(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:  # noqa: BLE001
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(TZ)


def iso(d):
    return d.astimezone(TZ).replace(microsecond=0).isoformat()


def local(tag):
    return tag.rsplit("}", 1)[-1]


def hijos_texto(el, nombre):
    for c in el:
        if local(c.tag) == nombre:
            return (c.text or "").strip()
    return ""


# --------------------------------------------------------------------------
# Lectores de fuentes
# --------------------------------------------------------------------------


def seccion_de_link(link, defecto):
    m = re.match(r"https?://[^/]+/([^/?#]+)/", link)
    if m:
        seg = m.group(1).lower()
        if seg in SECCION_A_CAT:
            return SECCION_A_CAT[seg]
    return SECCION_A_CAT.get(defecto, defecto) if defecto else None


def leer_feed(medio, nombre, url, defecto):
    txt, err = bajar_seguro(url)
    if err:
        return [], err
    try:
        raiz = ET.fromstring(txt.encode("utf-8"))
    except ET.ParseError as e:
        return [], "XML invalido: %s" % e
    items = []
    for it in raiz.iter():
        if local(it.tag) != "item":
            continue
        titulo = limpiar_titulo(hijos_texto(it, "title"))
        link = hijos_texto(it, "link")
        fecha = parse_fecha(hijos_texto(it, "pubDate"))
        if not titulo or not link or not fecha:
            continue
        items.append({
            "medio": medio, "titulo": titulo, "link": link, "fecha": fecha,
            "cat_seccion": seccion_de_link(link, defecto),
        })
    return items, None


def leer_x():
    """Devuelve (lista [{posicion,nombre,link}], fuente_usada, errores)."""
    errores = []
    txt, err = bajar_seguro(URL_TRENDS24)
    if txt:
        m = re.search(r"<ol[^>]*trend-card__list[^>]*>(.*?)</ol>", txt, re.S)
        if m:
            out = []
            for href, nombre in re.findall(
                    r'<a\s+href="?([^"\s>]+)"?\s+class="?trend-link"?[^>]*>([^<]*)</a>', m.group(1)):
                nombre = html.unescape(nombre).strip()
                href = html.unescape(href).replace("://twitter.com/", "://x.com/")
                if nombre:
                    out.append({"posicion": len(out) + 1, "nombre": nombre, "link": href})
            if out:
                return out, "trends24", errores
        err = "trends24: sin tendencias en el HTML"
    errores.append(("trends24", err))
    txt, err = bajar_seguro(URL_GETDAYTRENDS)
    if txt:
        out = []
        for pos, nombre in re.findall(
                r'<th[^>]*class="pos"[^>]*>\s*(\d+)\s*</th>\s*<td class="main"><a class="string"[^>]*>([^<]*)</a>', txt):
            nombre = html.unescape(nombre).strip()
            if nombre:
                out.append({
                    "posicion": int(pos), "nombre": nombre,
                    "link": "https://x.com/search?q=" + urllib.parse.quote(nombre)})
        if out:
            return out, "getdaytrends", errores
        err = "getdaytrends: sin tendencias en el HTML"
    errores.append(("getdaytrends", err))
    return [], None, errores


ES_PALABRAS = set(norm("el la los las de del que en y a un una por con para se su al es lo como mas pero sus le ya o fue este si porque esta entre cuando muy sin sobre tambien me hasta hay donde quien desde todo nos durante todos uno les ni contra otros ese eso ante ellos e esto mi antes algunos que unos yo otro otras otra el tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas algo nosotros").split())
HOSTS_AR = ("infobae.com", "clarin.com", "lanacion.com.ar", "tn.com.ar", "ambito.com", "pagina12.com.ar",
            "perfil.com", "cronista.com", "ole.com.ar", "tycsports.com", "minutouno.com", "elDoce.tv".lower(),
            "eltrecetv.com.ar", "telefe.com", "a24.com", "c5n.com", "lavoz.com.ar", "losandes.com.ar",
            "mdzol.com", "diariouno.com.ar", "pagina12.com.ar", "iprofesional.com", "bae negocio".replace(" ", ""),
            "baenegocios.com", "lanacion.com", "tycsports", "cienradios.com", "radiomitre.cienradios.com",
            "la100.cienradios.com", "eldiarioar.com", "tiempoar.com.ar", "infocielo.com", "diputados.gob.ar",
            "argentina.gob.ar", "lapoliticaonline.com", "noticiasargentinas.com", "dib.com.ar", "urgente24.com")


def es_texto_espanol(textos):
    palabras = re.findall(r"[a-z]+", norm(" ".join(textos)))
    if len(palabras) < 4:
        return False
    return sum(1 for p in palabras if p in ES_PALABRAS) / len(palabras) >= 0.12


def leer_google():
    """Devuelve (lista, error). Descarta tendencias que no parecen argentinas."""
    txt, err = bajar_seguro(URL_GOOGLE)
    if err:
        return [], err
    try:
        raiz = ET.fromstring(txt.encode("utf-8"))
    except ET.ParseError as e:
        return [], "XML invalido: %s" % e
    out = []
    descartadas = 0
    for it in raiz.iter():
        if local(it.tag) != "item":
            continue
        nombre = hijos_texto(it, "title")
        trafico = hijos_texto(it, "approx_traffic")
        noticias = []
        for ni in it:
            if local(ni.tag) == "news_item":
                noticias.append({
                    "titulo": hijos_texto(ni, "news_item_title"),
                    "url": hijos_texto(ni, "news_item_url"),
                    "fuente": hijos_texto(ni, "news_item_source"),
                })
        hosts = [re.sub(r"^www\.", "", urllib.parse.urlparse(n["url"]).netloc.lower()) for n in noticias if n["url"]]
        es_ar = any(h.endswith(".ar") or any(h == a or h.endswith("." + a) for a in HOSTS_AR) for h in hosts)
        if not es_ar:
            es_ar = es_texto_espanol([nombre] + [n["titulo"] for n in noticias]) and not any(
                h.endswith((".pl", ".br", ".pt", ".fr", ".de", ".it", ".ru", ".jp", ".in", ".uk")) for h in hosts)
        if not nombre or not es_ar:
            descartadas += 1
            continue
        out.append({
            "nombre": nombre, "trafico": trafico,
            "link": "https://www.google.com/search?q=" + urllib.parse.quote(nombre),
            "noticias": noticias, "fecha": parse_fecha(hijos_texto(it, "pubDate")),
        })
    return out, None


def leer_indec(hoy):
    url = URL_INDEC.format(fecha=hoy.strftime("%Y-%m-%d"))
    txt, err = bajar_seguro(url)
    if err:
        return [], err
    titulos = re.findall(r'<div class="cal-content text-calendario">\s*(.*?)\s*</div>', txt, re.S)
    horas = re.findall(r'<div class="cal-content text-calendario text-center">\s*(\d{1,2}:\d{2})\s*hs', txt, re.S)
    out = []
    for i, t in enumerate(titulos):
        t = limpiar_html(t)
        if not t:
            continue
        h = horas[i] if len(horas) == len(titulos) else ""
        out.append({"hora": h.zfill(5) if h else "", "titulo": t, "fuente": "INDEC", "link": URL_INDEC_PAGINA})
    if not out and "nro-dia" not in txt:
        return [], "estructura del calendario cambió (no se encontró el día)"
    return sorted(out, key=lambda x: x["hora"]), None


def leer_boletin(hoy):
    txt, err = bajar_seguro(URL_BORA)
    if err:
        return [], err
    fecha = hoy.strftime("%Y%m%d")
    out = []
    rubro = ""
    patron = re.compile(
        r'<h5[^>]*seccion-rubro[^>]*>(.*?)</h5>|<a\s+href="(/detalleAviso/primera/\d+/(\d{8}))"[^>]*>(.*?)</a>', re.S)
    for m in patron.finditer(txt):
        if m.group(1) is not None:
            rubro = limpiar_html(m.group(1))
            continue
        if rubro.upper().endswith("ANTERIOR") or m.group(3) != fecha:
            continue
        cuerpo = m.group(4)
        org = re.search(r'<p class="item">(.*?)</p>', cuerpo, re.S)
        det = re.findall(r"<small>(.*?)</small>", cuerpo, re.S)
        organismo = limpiar_html(org.group(1)) if org else ""
        corto = limpiar_html(det[0]) if det else ""
        titulo = (organismo.title() + ": " + corto) if organismo else corto
        if not titulo.strip():
            continue
        out.append({"fuente": "Boletín Oficial", "titulo": titulo.strip(": "), "rubro": rubro,
                    "link": "https://www.boletinoficial.gob.ar" + m.group(2)})
    if not out:
        return [], "sin avisos de hoy (¿sin edición o cambió el HTML?)"
    return out, None


def leer_cepa(ahora):
    txt, err = bajar_seguro(URL_CEPA)
    if err:
        return [], err
    try:
        raiz = ET.fromstring(txt.encode("utf-8"))
    except ET.ParseError as e:
        return [], "XML invalido: %s" % e
    out = []
    for it in raiz.iter():
        if local(it.tag) != "item":
            continue
        f = parse_fecha(hijos_texto(it, "pubDate"))
        t = limpiar_html(hijos_texto(it, "title"))
        if t and f and f >= ahora - timedelta(days=7):
            out.append({"fuente": "CEPA", "titulo": t, "link": hijos_texto(it, "link")})
    return out, None


# --------------------------------------------------------------------------
# Categorias
# --------------------------------------------------------------------------
KW_TRABAJO = {"empleo", "desempleo", "despido", "paritaria", "salario", "sueldo", "gremio", "sindical",
               "sindicato", "cgt", "trabajador", "desocupacion", "aguinaldo", "convenio", "laboral",
               "suspension", "paro", "obrero", "docente", "estatal"}
KW_JUBILACIONES = {"jubilacion", "jubilado", "jubilatorio", "anses", "haber", "bono", "pension",
                   "pami", "previsional", "movilidad", "pensionado"}


def categoria_de_titular(n):
    """n = nota con 'tokens' (set) y 'cat_seccion'."""
    tk = n["tokens"]
    sec = n["cat_seccion"]
    if sec not in ("deportes", "espectaculos"):
        if tk & (KW_JUBILACIONES - {"haber", "bono"}) or (tk & {"haber", "bono"} and "anses" in tk):
            return "jubilaciones"
        if tk & KW_TRABAJO - {"paro", "laboral", "convenio", "docente", "estatal", "suspension"}:
            return "trabajo"
        if "paro" in tk and not (tk & {"cardiaco", "cardiorrespiratorio"}):
            return "trabajo"
        if "laboral" in tk and sec in ("economia", "politica", "social"):
            return "trabajo"
    return sec or "otros"


KW_DEPORTES = set(norm("boca river racing independiente futbol seleccion mundial copa partido gol messi liga tenis nba f1 formula "
                        "libertadores sudamericana champions jugador dt entrenador club afa").split())
KW_ESPECT = set(norm("serie pelicula cine actriz actor cantante recital show famosa famoso farandula netflix disney "
                      "telefe cantante banda album gran hermano bailando festival").split())


def categoria_texto(texto):
    tk = {t for t, _ in tokens_de(texto)}
    if tk & {stem(x) for x in KW_JUBILACIONES - {"bono", "haber", "movilidad"}}:
        return "jubilaciones"
    if tk & {stem(x) for x in KW_TRABAJO - {"paro", "laboral", "convenio", "docente", "estatal", "suspension"}}:
        return "trabajo"
    if tk & {stem(x) for x in KW_DEPORTES}:
        return "deportes"
    if tk & {stem(x) for x in KW_ESPECT}:
        return "espectaculos"
    return "otros"


# --------------------------------------------------------------------------
# Agrupacion de titulares
# --------------------------------------------------------------------------


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[b] = a


def preparar_notas(notas):
    for n in notas:
        toks = tokens_de(n["titulo"])
        n["tok_list"] = toks
        n["tokens"] = {t for t, _ in toks}
        n["entidades"] = {t for t, e in toks if e}
        seq = [t for t, _ in toks]
        n["bigramas"] = {(seq[i], seq[i + 1]) for i in range(len(seq) - 1)}


def agrupar_con_tope(notas, df, N, tope=25, umbral=7.0):
    """Agrupa titulares sin IA: aglomerativo guiado por terminos compartidos.

    1. Se buscan pares de titulares que comparten terminos significativos (con peso
       tipo IDF: los terminos raros pesan mas; nombres propios/siglas pesan x1.3; los
       terminos comunes como "gobierno", "milei" o "argentina" no cuentan solos).
    2. Los pares se procesan de mayor a menor puntaje y se fusionan sus grupos solo si
       los terminos que comparten estan en al menos ~1/3 de los titulares de AMBOS grupos
       (evita el encadenamiento: A parecido a B, B parecido a C, pero A y C sin relacion).
    3. Ningun grupo supera `tope` titulares.
    """
    debil_df = max(10, int(N * 0.02))

    def fuerte(t):
        return t not in DEBILES and df[t] <= debil_df

    def peso(t, ents):
        w = math.log(N / df[t])
        return w * 1.3 if t in ents else w

    def cumple(comunes, ents, bonus=0.0, ents_ambos=None):
        if not comunes:
            return 0.0
        score = sum(peso(c, ents) for c in comunes) + bonus
        if len(comunes) >= 2:
            return score if score >= umbral else 0.0
        ents = ents if ents_ambos is None else ents_ambos
        c = next(iter(comunes))
        if df[c] <= 3 and (c in ents or len(c) >= 8) and score >= umbral * 0.8:
            return score
        return 0.0

    inv = defaultdict(list)
    for i, n in enumerate(notas):
        for t in n["tokens"]:
            if fuerte(t):
                inv[t].append(i)
    aristas = {}
    for t, lista in inv.items():
        if len(lista) > 40:
            continue
        for a in range(len(lista)):
            for b in range(a + 1, len(lista)):
                i, j = lista[a], lista[b]
                if (i, j) in aristas:
                    continue
                ni, nj = notas[i], notas[j]
                comunes = {c for c in ni["tokens"] & nj["tokens"] if fuerte(c)}
                ents = ni["entidades"] | nj["entidades"]
                bi = [b2 for b2 in ni["bigramas"] & nj["bigramas"] if fuerte(b2[0]) or fuerte(b2[1])]
                sc = cumple(comunes, ents, 2.0 * len(bi), ni["entidades"] & nj["entidades"])
                aristas[(i, j)] = sc
    ordenadas = sorted(((sc, i, j) for (i, j), sc in aristas.items() if sc > 0), reverse=True)

    padre = list(range(len(notas)))
    miembros = {i: [i] for i in range(len(notas))}
    perfil = {i: Counter(notas[i]["tokens"]) for i in range(len(notas))}
    ents_g = {i: set(notas[i]["entidades"]) for i in range(len(notas))}

    def raiz(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for sc, i, j in ordenadas:
        a, b = raiz(i), raiz(j)
        if a == b:
            continue
        if len(miembros[a]) + len(miembros[b]) > tope:
            continue
        la, lb = len(miembros[a]), len(miembros[b])
        # terminos presentes en >=1/3 de los titulares de cada grupo (o en ambos si son chicos)
        # (en grupos de 3+ el termino debe estar en al menos 2 titulares)
        comunes = set()
        need_a = 1 if la <= 2 else max(2, math.ceil(0.34 * la))
        need_b = 1 if lb <= 2 else max(2, math.ceil(0.34 * lb))
        for t, ca in perfil[a].items():
            if fuerte(t) and ca >= need_a and perfil[b].get(t, 0) >= need_b:
                comunes.add(t)
        if not cumple(comunes, ents_g[a] | ents_g[b], 0.0, ents_g[a] & ents_g[b]):
            continue
        if la < lb:
            a, b = b, a
        padre[b] = a
        miembros[a].extend(miembros.pop(b))
        perfil[a].update(perfil.pop(b))
        ents_g[a] |= ents_g.pop(b)
    return list(miembros.values())


def elegir_titulo(grupo_notas):
    cont = Counter()
    for n in grupo_notas:
        for t in n["tokens"]:
            cont[t] += 1
    mejor, mejor_s = None, -1e9
    for n in grupo_notas:
        toks = [t for t in n["tokens"] if t not in DEBILES]
        if not toks:
            toks = list(n["tokens"])
        cobertura = sum(cont[t] for t in toks) / math.sqrt(max(len(n["tokens"]), 1))
        largo = len(n["titulo"])
        pen = 0
        if largo > 120:
            pen += (largo - 120) * 0.2
        if largo < 25:
            pen += 5
        if n["titulo"].count("?") and False:
            pen += 1
        if re.search(r"\b(video|fotos?|en vivo|minuto a minuto)\b", norm(n["titulo"])):
            pen += 3
        s = cobertura + AUTORIDAD.get(n["medio"], 1) * 0.8 - pen
        if s > mejor_s:
            mejor, mejor_s = n, s
    return mejor["titulo"]


# --------------------------------------------------------------------------
# Tendencias -> temas
# --------------------------------------------------------------------------


def tokens_tendencia(nombre):
    """Tokens significativos de una tendencia (separa CamelCase en hashtags)."""
    txt = re.sub(r"(?<=[a-záéíóúñ])(?=[A-ZÁÉÍÓÚÑ])", " ", nombre)
    return [t for t, _ in tokens_de(txt) if t not in DEBILES or len(tokens_de(txt)) == 1]


def trafico_a_num(s):
    m = re.search(r"([\d.,]+)\s*(mil|k|m|millon)?", (s or "").lower())
    if not m:
        return 0
    try:
        v = float(m.group(1).replace(".", "").replace(",", "."))
    except ValueError:
        return 0
    suf = m.group(2) or ""
    if suf in ("mil", "k"):
        v *= 1000
    elif suf in ("m", "millon"):
        v *= 1000000
    return v


def puntaje_match(tk_tend, tf_cluster, links_cluster, noticias_g, n_notas):
    """Cuanto encaja una tendencia en un cluster; 0 si no encaja."""
    if noticias_g:
        for nw in noticias_g:
            if nw["url"] in links_cluster:
                return 100.0
    if not tk_tend:
        return 0.0
    presentes = [t for t in tk_tend if tf_cluster.get(t, 0) >= 1]
    if len(tk_tend) == 1:
        t = tk_tend[0]
        # un solo termino: debe aparecer en >=2 titulares o en >=60% de un cluster chico
        if tf_cluster.get(t, 0) >= 2 or (n_notas <= 3 and tf_cluster.get(t, 0) >= 1 and len(t) >= 5):
            return 5.0 + tf_cluster[t] / n_notas * 3
        return 0.0
    if len(presentes) == len(tk_tend) or (len(presentes) >= 2 and len(presentes) >= len(tk_tend) * 0.75):
        return 8.0 + sum(tf_cluster[t] for t in presentes) / n_notas
    return 0.0


# --------------------------------------------------------------------------
# Calor
# --------------------------------------------------------------------------
def calcular_calor(n_medios, n_notas, pos_x, trafico_g, en_google, ultima, ahora):
    """Calor 0-100 = suma ponderada (maximo 100):
      - Medios distintos  : hasta 35  (35 * min(medios, 6) / 6, curva raiz para premiar 2-3 medios)
      - Cantidad de notas : hasta 15  (15 * min(notas, 12) / 12)
      - Presencia en X    : hasta 20  (20 en posicion 1, baja linealmente hasta 6 en posicion 50)
      - Presencia Google  : hasta 15  (10 por estar + hasta 5 segun trafico, escala log; 100 -> 0, 100k+ -> 5)
      - Recencia          : hasta 15  (15 si la ultima nota tiene <2 h, baja lineal a 0 a las 24 h)
    """
    c = 35.0 * math.sqrt(min(n_medios, 6) / 6.0)
    c += 15.0 * min(n_notas, 12) / 12.0
    if pos_x:
        c += max(6.0, 20.0 - (pos_x - 1) * (14.0 / 49.0))
    if en_google:
        c += 10.0
        if trafico_g > 0:
            c += max(0.0, min(5.0, (math.log10(trafico_g) - 2.0) * 2.5))
    if ultima:
        horas = max(0.0, (ahora - ultima).total_seconds() / 3600.0)
        if horas <= 2:
            c += 15.0
        else:
            c += max(0.0, 15.0 * (1 - (horas - 2) / 22.0))
    return int(round(max(0.0, min(100.0, c))))


# --------------------------------------------------------------------------
# Principal
# --------------------------------------------------------------------------


def proxima_actualizacion(ahora):
    for h in (8, 12, 16, 20):
        c = ahora.replace(hour=h, minute=0, second=0, microsecond=0)
        if c > ahora:
            return c
    return (ahora + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)


def cargar_previo():
    try:
        d = json.loads(SALIDA.read_text(encoding="utf-8"))
        if d.get("ejemplo"):
            return []
        return d.get("temas", [])
    except Exception:  # noqa: BLE001
        return []


def main():
    ahora = datetime.now(TZ)
    hoy = ahora
    estado = []

    # ---- descargas en paralelo
    with ThreadPoolExecutor(max_workers=8) as ex:
        f_feeds = [(f, ex.submit(leer_feed, *f)) for f in FEEDS]
        f_x = ex.submit(leer_x)
        f_g = ex.submit(leer_google)
        f_i = ex.submit(leer_indec, hoy)
        f_b = ex.submit(leer_boletin, hoy)
        f_c = ex.submit(leer_cepa, ahora)

        crudas = []
        por_medio = {}
        for (medio, nombre, url, _d), fut in f_feeds:
            items, err = fut.result()
            crudas.extend(items)
            m = por_medio.setdefault(medio, {"fuente": medio, "ok": False, "items": 0, "fallas": []})
            m["items"] += len(items)
            if err:
                m["fallas"].append("%s (%s)" % (nombre, err))
            elif items or True:
                m["ok"] = True
        for m in por_medio.values():
            e = {"fuente": m["fuente"], "ok": m["ok"], "items": m["items"]}
            if m["fallas"]:
                e["error"] = "; ".join(m["fallas"])
            estado.append(e)

        x_lista, x_fuente, x_errs = f_x.result()
        for nom, err in x_errs:
            estado.append({"fuente": "X · " + nom, "ok": False, "items": 0, "error": err})
        if x_fuente:
            estado.append({"fuente": "X · " + x_fuente, "ok": True, "items": len(x_lista)})
        g_lista, g_err = f_g.result()
        estado.append({"fuente": "Google Trends AR", "ok": g_err is None, "items": len(g_lista),
                       **({"error": g_err} if g_err else {})})
        agenda, i_err = f_i.result()
        estado.append({"fuente": "INDEC (calendario)", "ok": i_err is None, "items": len(agenda),
                       **({"error": i_err} if i_err else {})})
        bora, b_err = f_b.result()
        estado.append({"fuente": "Boletín Oficial", "ok": b_err is None, "items": len(bora),
                       **({"error": b_err} if b_err else {})})
        cepa, c_err = f_c.result()
        estado.append({"fuente": "CEPA", "ok": c_err is None, "items": len(cepa),
                       **({"error": c_err} if c_err else {})})

    # ---- ventana de 24 h y deduplicado por link
    desde_min = ahora - timedelta(hours=VENTANA_HORAS)
    por_link = {}
    for n in crudas:
        if not (desde_min <= n["fecha"] <= ahora + timedelta(hours=2)):
            continue
        if es_pronostico_comun(n["titulo"]):
            continue
        clave = n["link"].split("#")[0].split("?")[0].rstrip("/")
        previa = por_link.get(clave)
        if previa is None:
            por_link[clave] = n
        elif previa["cat_seccion"] is None and n["cat_seccion"]:
            por_link[clave] = n
    notas = list(por_link.values())
    # mismo titular exacto en el mismo medio (links distintos)
    vistos = set()
    unicas = []
    for n in notas:
        k = (n["medio"], norm(n["titulo"]))
        if k in vistos:
            continue
        vistos.add(k)
        unicas.append(n)
    notas = unicas
    for n in notas:
        if not n["cat_seccion"]:
            n["cat_seccion"] = "otros"
    preparar_notas(notas)
    for n in notas:
        n["cat"] = categoria_de_titular(n)
    N = max(len(notas), 1)
    df = Counter()
    for n in notas:
        for t in n["tokens"]:
            df[t] += 1

    # ---- clusters
    grupos = agrupar_con_tope(notas, df, N)

    clusters = []
    for g in grupos:
        gn = [notas[i] for i in g]
        medios = {n["medio"] for n in gn}
        clusters.append({"notas": gn, "medios": medios})

    # ---- tendencias
    x_items = []
    for t in x_lista:
        x_items.append({**t, "tk": tokens_tendencia(t["nombre"])})
    g_items = []
    for t in g_lista:
        g_items.append({**t, "tk": tokens_tendencia(t["nombre"])})

    for c in clusters:
        c["tf"] = Counter(t for n in c["notas"] for t in n["tokens"])
        c["links"] = {n["link"] for n in c["notas"]}
        c["x"] = []
        c["g"] = []

    def asignar(items, clave):
        sueltos = []
        for it in items:
            mejor, mejor_s = None, 0.0
            for c in clusters:
                s = puntaje_match(it["tk"], c["tf"], c["links"], it.get("noticias"), len(c["notas"]))
                s += 0.01 * len(c["notas"])
                if s > mejor_s and s > 0.5:
                    mejor, mejor_s = c, s
            if mejor is not None and mejor_s >= 5.0:
                mejor[clave].append(it)
            else:
                sueltos.append(it)
        return sueltos

    x_sueltos = asignar(x_items, "x")
    g_sueltos = asignar(g_items, "g")

    # ---- temas candidatos
    temas = []
    for c in clusters:
        gn = c["notas"]
        if len(gn) < 2 and not c["x"] and not c["g"]:
            continue
        temas.append({"notas": gn, "x": c["x"], "g": c["g"], "tf": c["tf"]})

    # temas sin titulares: tendencias fuertes de X (top 12) y todas las de Google
    usados_g = set()
    for it in x_sueltos:
        if it["posicion"] <= 12:
            temas.append({"notas": [], "x": [it], "g": [], "tf": Counter(it["tk"]), "titulo_t": it["nombre"]})
    for it in g_sueltos:
        # si coincide con una tendencia de X suelta, fusionar
        fus = None
        for t in temas:
            if not t["notas"] and t["x"]:
                tk_x = set(tokens_tendencia(t["x"][0]["nombre"]))
                if tk_x and set(it["tk"]) and (tk_x <= set(it["tk"]) or set(it["tk"]) <= tk_x):
                    fus = t
                    break
        if fus is not None:
            fus["g"].append(it)
        else:
            temas.append({"notas": [], "x": [], "g": [it], "tf": Counter(it["tk"]), "titulo_t": it["nombre"],
                          "noticias_g": it.get("noticias", [])})

    # ---- oficiales
    oficiales_pool = []
    for it in agenda:
        oficiales_pool.append({"fuente": "INDEC", "titulo": it["titulo"], "link": it["link"]})
    for it in bora:
        oficiales_pool.append({"fuente": it["fuente"], "titulo": it["titulo"], "link": it["link"]})
    for it in cepa:
        oficiales_pool.append({"fuente": "CEPA", "titulo": it["titulo"], "link": it["link"]})
    for o in oficiales_pool:
        o["tk"] = {t for t, _ in tokens_de(o["titulo"]) if t not in OFICIAL_STOP}
    # terminos repetidos en muchas normas (nombres de organismos) no sirven para cruzar
    df_of = Counter(t for o in oficiales_pool for t in o["tk"])
    for o in oficiales_pool:
        o["tk"] = {t for t in o["tk"] if df_of[t] < 3}

    previos = cargar_previo()

    salida = []
    ids_usados = set()
    for t in temas:
        gn = sorted(t["notas"], key=lambda n: n["fecha"])
        medios = []
        for n in sorted(gn, key=lambda n: (-AUTORIDAD.get(n["medio"], 1), n["fecha"])):
            if n["medio"] not in medios:
                medios.append(n["medio"])
        if gn:
            titulo = elegir_titulo(gn)
        else:
            titulo = t["titulo_t"]
        pos_x = min((x["posicion"] for x in t["x"]), default=None)
        traf = max((trafico_a_num(g["trafico"]) for g in t["g"]), default=0)

        # categoria
        if gn:
            votos = Counter()
            for n in gn:
                votos[n["cat"]] += 0.5 if n["cat"] == "otros" else 1.0
            top = max(votos.values())
            cands = [k for k, v in votos.items() if v == top]
            cats = sorted(cands, key=lambda k: (k not in PRIORITARIAS, k))
            categoria = cats[0]
        else:
            texto = titulo + " " + " ".join(nw["titulo"] for g in t["g"] for nw in g.get("noticias", []))
            categoria = categoria_texto(texto)

        ultima = max((n["fecha"] for n in gn), default=None)
        if ultima is None:
            fg = [g["fecha"] for g in t["g"] if g.get("fecha")]
            ultima = max(fg) if fg else ahora
        primera = min((n["fecha"] for n in gn), default=ultima)

        calor = calcular_calor(len(medios), len(gn), pos_x, traf, bool(t["g"]), ultima, ahora)

        # oficiales: >=2 terminos significativos compartidos (o 1 termino raro de >=6 letras que sea sigla/largo)
        tf = t["tf"]
        terminos = {k for k, v in tf.items() if k not in DEBILES and k not in OFICIAL_STOP and
                    (v >= 2 or len(gn) <= 1)}
        ofi = []
        for o in oficiales_pool:
            comunes = o["tk"] & terminos
            if len(comunes) >= 2 or any(len(c) >= 6 and df[c] <= 3 and tf.get(c, 0) >= 2 for c in comunes):
                ofi.append({"fuente": o["fuente"], "titulo": o["titulo"], "link": o["link"]})
        ofi = ofi[:5]

        # id / desde: reutiliza el tema previo si comparte links o titulos parecidos
        links_actuales = {n["link"] for n in gn}
        id_prev, desde_prev = None, None
        mejor_ov = 0.0
        tk_titulo = {tt for tt, _ in tokens_de(titulo) if tt not in DEBILES}
        for p in previos:
            lp = {n.get("link") for n in p.get("notas", [])}
            ov = len(lp & links_actuales)
            if ov == 0 and tk_titulo:
                tp = {tt for tt, _ in tokens_de(p.get("titulo", "")) if tt not in DEBILES}
                if tp:
                    j = len(tp & tk_titulo) / len(tp | tk_titulo)
                    ov = j if j >= 0.5 else 0
            if ov > mejor_ov:
                mejor_ov = ov
                id_prev, desde_prev = p.get("id"), parse_fecha(p.get("desde"))
        tid = id_prev or slug(titulo)
        base, k = tid, 2
        while tid in ids_usados:
            tid = "%s-%d" % (base, k)
            k += 1
        ids_usados.add(tid)
        desde = primera
        if desde_prev and desde_prev < desde:
            desde = desde_prev

        notas_out = [{"medio": n["medio"], "titulo": n["titulo"], "link": n["link"], "hora": iso(n["fecha"])}
                     for n in sorted(gn, key=lambda n: n["fecha"], reverse=True)]
        # temas solo de Google: usar sus notas de referencia como contexto (sin contarlas como medios propios)
        salida.append({
            "id": tid,
            "titulo": titulo,
            "categoria": categoria,
            "prioritaria": categoria in PRIORITARIAS,
            "desde": iso(desde),
            "calor": calor,
            "medios": medios,
            "en_x": bool(t["x"]),
            "posicion_x": pos_x,
            "en_google": bool(t["g"]),
            "notas": notas_out,
            "oficiales": ofi,
            "resumen": None,
            "angulos": [],
        })

    salida.sort(key=lambda x: (-x["calor"], x["desde"]))
    salida = salida[:MAX_TEMAS]

    resultado = {
        "actualizado": iso(ahora),
        "proxima_actualizacion": iso(proxima_actualizacion(ahora)),
        "ia_disponible": False,
        "agenda_hoy": [{"hora": a["hora"], "titulo": a["titulo"], "fuente": a["fuente"], "link": a["link"]}
                       for a in agenda],
        "temas": salida,
        "tendencias_x": x_lista,
        "google_trends": [{"nombre": g["nombre"], "trafico": g["trafico"], "link": g["link"]} for g in g_lista],
        "estado_fuentes": estado,
    }

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    SALIDA.write_text(texto, encoding="utf-8")
    (ARCHIVO / (ahora.strftime("%Y-%m-%d") + ".json")).write_text(texto, encoding="utf-8")

    fallas = [e["fuente"] for e in estado if not e["ok"]]
    print("Notas en ventana: %d | clusters: %d | temas: %d | fuentes con falla: %s" % (
        len(notas), len(grupos), len(salida), ", ".join(fallas) or "ninguna"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
