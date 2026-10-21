# Fuentes gratuitas para el radar de noticias y tendencias

Pruebas hechas el 21/10/2026 desde Mac con `curl -sL -A "Mozilla/5.0" --max-time 20`. Sin APIs pagas, sin login, sin claves.

## Resumen rápido

| Fuente | Estado | Formato |
|---|---|---|
| Infobae (general + secciones) | Funciona | RSS 2.0 |
| Clarín (general + secciones) | Funciona | RSS 2.0 |
| La Nación (general + secciones) | Funciona | RSS 2.0 |
| Página/12 (portada + secciones) | Funciona (sin feed de Política propio) | RSS 2.0 |
| Ámbito (general + secciones) | Funciona (sin feed de Sociedad) | RSS 2.0 |
| TN (feed general) | Funciona (sin feeds por sección) | RSS 2.0 |
| trends24.in/argentina | Funciona | HTML estático |
| getdaytrends.com/argentina | Funciona | HTML estático |
| Google Trends AR | Funciona | RSS 2.0 |
| INDEC calendario | Funciona (endpoint interno) | HTML fragmento |
| Boletín Oficial, Primera sección | Funciona (HTML) | HTML estático |
| Boletín Oficial, RSS | NO funciona | — |
| CEPA (informes) | Funciona | RSS 2.0 (y Atom) |

Convención de categorías sugerida (según ESQUEMA.md): `economia`, `politica`, `social` (= sociedad), `deportes`, `espectaculos`, `otros`.

---

## 1. Medios argentinos (RSS)

Todos devuelven HTTP 200 y RSS 2.0 con ítems de hoy (21/10/2026). Campos comunes: `<title>`, `<link>`, `<guid>`, `<pubDate>` (RFC 822 con zona horaria), `<description>`. Algunos traen además `<category>` (La Nación) o `<content:encoded>`, `<media:content>` (TN, Infobae).

### 1.1 Infobae : VERIFICADO
- General: `https://www.infobae.com/arc/outboundfeeds/rss/` (200, 100 ítems)
- Política: `https://www.infobae.com/arc/outboundfeeds/rss/category/politica/` (200, 100 ítems)
- Economía: `https://www.infobae.com/arc/outboundfeeds/rss/category/economia/` (200, 100 ítems)
- Sociedad: `https://www.infobae.com/arc/outboundfeeds/rss/category/sociedad/` (200, 100 ítems)
- Deportes: `https://www.infobae.com/arc/outboundfeeds/rss/category/deportes/` (200, 100 ítems)
- Espectáculos: usar `.../category/entretenimiento/` (200, 100 ítems). `.../category/espectaculos/` devuelve 0 ítems.
- NO funciona: `https://www.infobae.com/feeds/rss/` (404).
- Mapeo: `item > title`, `item > link`, `item > pubDate`. La sección no viene como campo: sale del primer segmento del link (`/politica/`, `/economia/`, `/sociedad/`, `/deportes/`, `/teleshow/`, `/entretenimiento/`, `/mexico/`...).
- Ejemplo 1: "La indirecta de Mauro Icardi a Wanda Nara desde México por una foto de la China Suárez" · https://www.infobae.com/teleshow/2026/10/21/la-indirecta-de-mauro-icardi-a-wanda-nara-desde-mexico-por-una-foto-de-la-china-suarez/ · Wed, 21 Oct 2026 13:57:21 +0000
- Ejemplo 2: "La gente no llega a fin de mes: qué dijo el autor de la encuesta..." (feed economía) · https://www.infobae.com/economia/2026/10/21/la-gente-no-llega-a-fin-de-mes-que-dijo-el-autor-de-la-encuesta-que-irrito-al-presidente-milei/ · Wed, 21 Oct 2026 13:54:46 +0000
- Caveats: el feed pesa ~700 KB a 1 MB (trae contenido completo); conviene leer solo título, link y fecha. Las categorías de 100 ítems cubren varios días (política llega hasta el 16/10), así que el filtro de "últimas 24-48 h" se hace por fecha.

### 1.2 Clarín : VERIFICADO
- General ("Lo último"): `https://www.clarin.com/rss/lo-ultimo/` (200, 10 ítems)
- Política: `https://www.clarin.com/rss/politica/` (200, 10 ítems)
- Economía: `https://www.clarin.com/rss/economia/` (200, 10 ítems). Incluye subsecciones (ej. `energia-y-mineria`).
- Sociedad: `https://www.clarin.com/rss/sociedad/` (200, 10 ítems)
- Deportes: `https://www.clarin.com/rss/deportes/` (200, 10 ítems)
- Espectáculos: `https://www.clarin.com/rss/espectaculos/` (200, 10 ítems)
- Mapeo: `item > title`, `item > link`, `item > pubDate`. Sección = primer segmento del link (`/politica/`, `/economia/`, `/sociedad/`...).
- Ejemplo 1: "Un falso Donald Trump preso baila y se pelea con la gente en un espectáculo callejero..." · https://www.clarin.com/mundo/falso-donald-trump-preso-baila-pelea-gente-espectaculo-callejero-sorprende-capital-iran_0_AwaSsdOMQ7.html · Wed, 21 Oct 2026 13:43:03 +0000
- Ejemplo 2: "Qué ver en Disney+ hoy: las 10 series y películas que lideran el ranking este miércoles 21" · https://www.clarin.com/espectaculos/que-ver-en-disney-hoy-las-10-series-y-peliculas-que-lideran-el-ranking-este-miercole... · Wed, 21 Oct 2026 10:15:03 +0000
- Caveats: solo 10 ítems por feed; en horas de poco movimiento pueden cubrir menos de 24 h. Hay que pedir feeds frecuentes o combinar con otras fuentes.

### 1.3 La Nación : VERIFICADO
- General: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/` (200, 93 ítems)
- Política: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/politica/` (200, 77 ítems)
- Economía: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/` (200, 99 ítems)
- Sociedad: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/sociedad/` (200, 83 ítems)
- Deportes: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/deportes/` (200, 73 ítems)
- Espectáculos: `https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/espectaculos/` (200, 88 ítems)
- NO funciona: `.../rss/seccion/<nombre>/` (404).
- Mapeo: `item > title`, `item > link`, `item > pubDate`, `item > category` (texto con la sección o subtema: "Política", "Campo", "Fútbol", "Personajes"...). Para la categoría del radar usar el primer segmento del link (`/politica/`, `/economia/`...) porque el campo `category` a veces es un subtema.
- Ejemplo 1: "A qué hora llegan las tormentas fuertes a Buenos Aires hoy, según el SMN" · https://www.lanacion.com.ar/sociedad/a-que-hora-llegan-las-tormentas-fuertes-a-buenos-aires-hoy-segun-el-smn-nid21102026/ · Wed, 21 Oct 2026 13:57:17 +0000
- Ejemplo 2: "Plazo fijo: cuál es la tasa de interés banco por banco este miércoles 21 de octubre" · https://www.lanacion.com.ar/economia/plazo-fijo-cual-es-la-tasa-de-interes-banco-por-banco-este-miercoles-21-de-octubre-nid21102026/ · Wed, 21 Oct 2026 13:56:52 +0000
- Caveats: el feed general pesa ~740 KB. Los links traen `nid` + fecha (`nid21102026`).

### 1.4 Página/12 : VERIFICADO (con excepciones)
- Portada: `https://www.pagina12.com.ar/arc/outboundfeeds/rss/portada` (200, 6 ítems)
- Economía: `https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/economia/notas` (200, 25 ítems)
- Sociedad: `https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/sociedad/notas` (200, 25 ítems)
- Deportes: `https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/deportes/notas` (200, 25 ítems)
- El País (la sección que hace de política): `https://www.pagina12.com.ar/arc/outboundfeeds/rss/secciones/el-pais/notas` (200, 25 ítems)
- Espectáculos (suplemento Cultura y espectáculos): `https://www.pagina12.com.ar/arc/outboundfeeds/rss/suplementos/cultura-y-espectaculos/notas` (200, 25 ítems)
- NO funciona: `.../secciones/politica/notas` y `.../secciones/espectaculos/notas` (200 pero HTML de error, 0 ítems), `.../secciones/cultura/notas` (0 ítems). Tampoco `https://www.pagina12.com.ar/rss/portada` (HTML).
- Índice de feeds: la página `https://www.pagina12.com.ar/rss` (HTML) lista todos los feeds `arc/outboundfeeds/rss/...` si hace falta buscar más.
- Mapeo: `item > title`, `item > link`, `item > pubDate`. Sección por primer segmento del link o por la URL del feed.
- Ejemplo 1: "Gisela Magri: 'El tango está más vivo que nunca'" (espectáculos) · https://www.pagina12.com.ar/2026/10/21/gisela-magri-el-tango-esta-mas-vivo-que-nunca/ · Wed, 21 Oct 2026 03:01:00 +0000
- Ejemplo 2: "Dólar blue, dólar hoy: a cuánto cotizan el miércoles 21 de octubre de 2026" (economía) · https://www.pagina12.com.ar/2026/10/21/dolar-blue-dolar-hoy-a-cuanto-cotizan-el-miercoles-21-de-octubre-de-2026/ · Wed, 21 Oct 2026 11:50:00 +0000
- Caveats: la fecha de muchos ítems viene como "03:01:00 +0000" (hora fija de carga), así que la hora no es exacta. Las fechas de la sección pueden ser de días anteriores.

### 1.5 Ámbito : VERIFICADO (sin feed de Sociedad)
- General (portada): `https://www.ambito.com/rss/pages/home.xml` (200, 20 ítems)
- Política: `https://www.ambito.com/rss/pages/politica.xml` (200, 20 ítems)
- Economía: `https://www.ambito.com/rss/pages/economia.xml` (200, 20 ítems)
- Deportes: `https://www.ambito.com/rss/pages/deportes.xml` (200, 20 ítems)
- Espectáculos: `https://www.ambito.com/rss/pages/espectaculos.xml` (200, 100 ítems, algunos de hace más de 10 días)
- Sociedad: NO hay feed propio. `https://www.ambito.com/rss/pages/sociedad.xml` devuelve 0 bytes. Alternativa: `https://www.ambito.com/rss/pages/ultimas-noticias.xml` (200, 15 ítems, mezcla de secciones) y filtrar por link.
- Mapeo: `item > title`, `item > link`, `item > pubDate` (con offset -0300), `item > category` (ej. "Política", "Economía", "Finanzas", "Mundo"). En los feeds por sección la categoría viene siempre igual a la sección.
- Ejemplo 1: "Inflación: en qué provincias cuesta más llenar el changuito y en cuáles hubo mayores aumentos" · https://www.ambito.com/economia/inflacion-que-provincias-cuesta-mas-llenar-el-changuito-y-cuales-hubo-mayores-aumentos-mensuales-n6336188 · Wed, 21 Oct 2026 09:48:00 -0300
- Ejemplo 2: "Biocombustibles: reparto del mercado genera ruido en Diputados entre las provincias" · https://www.ambito.com/politica/biocombustibles-reparto-del-mercado-genera-ruido-diputados-las-provincias-n6336171 · Wed, 21 Oct 2026 10:52:00 -0300

### 1.6 TN (Todo Noticias) : VERIFICADO (sin feeds por sección)
- General: `https://tn.com.ar/rss.xml` (200, 100 ítems, ~490 KB). `https://tn.com.ar/feed` devuelve lo mismo.
- NO funcionan (404): `https://tn.com.ar/rss/`, `https://tn.com.ar/rss/politica.xml`, `https://tn.com.ar/politica/rss.xml`, `https://tn.com.ar/deportes/rss.xml`, `https://tn.com.ar/economia/rss.xml`, `https://tn.com.ar/sociedad/rss.xml`, `https://tn.com.ar/espectaculos/rss.xml`, y los `.../arc/outboundfeeds/rss/...`.
- Conclusión: se usa el feed general y la sección sale del primer segmento del link. Valores vistos: `politica`, `economia`, `deportes`, `sociedad`, `show` (espectáculos), `salud`, `policiales`, `estados-unidos`, `videos`, `clima`, `cocina`, `musica`, `internacional`, `estilo`, `campo`. Mapear `show` → `espectaculos`.
- Mapeo: `item > title`, `item > link`, `item > guid`, `item > pubDate` (ISO 8601 con offset, ej. `2026-10-21T10:48:46-03:00`), `item > description`, `item > content:encoded` (HTML completo), `media:content@url` (imagen). `dc:creator` vacío en los ejemplos.
- Ejemplo 1: "Según medios españoles, la Casa Real le negó a Milei un encuentro con el rey Felipe VI..." · https://tn.com.ar/politica/2026/10/21/en-madrid-milei-se-reunio-con-el-presidente-del-senado-espanol-y-con-los-embajadores-de-eeuu-e-israel/ · 2026-10-21T10:48:46-03:00
- Ejemplo 2: "Murió un nene de 10 años por la ameba 'comecerebros' en Catamarca" · https://tn.com.ar/salud/noticias/2026/10/21/murio-un-nene-de-10-anos-por-la-ameba-comecerebros-en-catamarca-que-es-y-com... · 2026-10-21T10:48:37-03:00
- Caveats: el feed es grande; las fechas tienen formato ISO, distinto al de los demás medios (usar un parser de fechas que acepte ambos).

---

## 2. Tendencias en X (Twitter) para Argentina

No se usa la API de X. Se leen agregadores públicos con HTTP plano (HTML ya renderizado en el servidor, sin JavaScript).

### 2.1 trends24.in/argentina : VERIFICADO (recomendado)
- URL: `https://trends24.in/argentina/` (200, text/html, ~260 KB)
- Contenido: el HTML trae varios bloques, uno por cada corrida horaria aproximada. El primer bloque es el más reciente. Cada bloque tiene su hora.
- Selectores:
  - Contenedor de cada corrida: `div.list-container`
  - Hora de la corrida: `div.list-container > h3.title` (atributo `data-timestamp`, texto "Wed Oct 21 2026 13:15:15 GMT+0000")
  - Lista de tendencias: `div.list-container > ol.trend-card__list > li`
  - Nombre: `li > span.trend-name > a.trend-link` (texto del enlace)
  - Enlace a X: `a.trend-link[href]` (ej. `https://twitter.com/search?q=Paredes`)
  - Volumen de tweets: `span.tweet-count` (atributo `data-count`; en la prueba venía vacío)
  - Ranking: posición del `li` dentro del `ol` (1 = primero). El HTML no trae número de posición explícito.
- Ejemplo del bloque más reciente (13:15 UTC, 10:15 hora AR), posiciones 1-10: Paredes, Pedro Sánchez, jungkook, Maracaná, España, Villa, Vamos Boca, #BuenMiercoles, Valenzuela, Di Lollo.
- Caveats: los `href` apuntan a twitter.com y no a x.com. Los nombres pueden venir con "#". Para el "primer bloque" usar el primer `div.list-container` que tenga `ol.trend-card__list`.

### 2.2 getdaytrends.com/argentina : VERIFICADO (alternativa)
- URL: `https://getdaytrends.com/argentina/` (200, text/html, ~68 KB)
- Selectores:
  - Tabla de ranking: `table.ranking.trends`
  - Posición: `tbody > tr > th.pos` (texto = 1, 2, 3...)
  - Nombre: `tbody > tr > td.main > a.string` (texto); enlace relativo `/argentina/trend/<nombre>/`
  - Mini gráfico: `td.graph svg` (no se necesita)
- Ejemplo, posiciones 1-10: Paredes, Jungkook, Pedro Sánchez, Maracaná, Villa, España, Vamos Boca, El TAS, Valenzuela, Di Lollo.
- Caveats: no trae volumen de tweets en la prueba. Tiene el ranking con posición explícita (más fácil de parsear).

---

## 3. Google Trends (tendencias del momento, AR)

- URL: `https://trends.google.com/trending/rss?geo=AR` (200, application/xml, ~22 KB, 10 ítems)
- Namespace de Google: `xmlns:ht="https://trends.google.com/trending/rss"`
- Mapeo:
  - Nombre de la tendencia: `item > title`
  - Tráfico aproximado: `item > ht:approx_traffic` (ej. "200+", "500+")
  - Imagen y su fuente: `item > ht:picture`, `item > ht:picture_source`
  - Fecha: `item > pubDate` (RFC 822 con -0700)
  - Notas relacionadas (varias por tendencia): `item > ht:news_item`, con hijos `ht:news_item_title`, `ht:news_item_url` (link a la nota), `ht:news_item_source` (medio), `ht:news_item_picture`.
  - `item > link` y `item > description` no aportan nada útil (siempre el mismo link y descripción vacía).
- Ejemplo: tendencia "ahora caigo" (approx_traffic "200+"), con notas de eltrecetv.com.ar, la100.cienradios.com y eldoce.tv.
- Caveats: la lista puede traer tendencias de otros países (en la prueba apareció "mateusz chmura", de un medio polaco). Conviene filtrar por fuente o palabras. El feed tiene pocas tendencias (10) y no siempre trae resúmenes.

---

## 4. INDEC: calendario de difusión

- La página `https://www.indec.gob.ar/indec/web/Calendario-Fecha-0` responde 200, pero es solo la cáscara HTML. Los datos se cargan por JavaScript (`Scripts/calendario.js` y `Scripts/CalendarioFull.js`), así que no sirve para leer directo.
- Endpoint interno que sí devuelve HTML con los datos (sin JS):
  - Día: `https://www.indec.gob.ar/Calendario/FiltrosCalendario/dia/AAAA-MM-DD/es` (200). Ejemplo: `.../dia/2026-10-21/es`.
  - Mes: `https://www.indec.gob.ar/Calendario/FiltrosCalendario/mes/Octubre-2026/es` (200, 61 KB, trae los días con eventos en `div.nro-dia`).
- Formato de fecha: solo `AAAA-MM-DD` funciona (probado con 2026-10-15, 2026-10-21, 2026-10-22, 2026-10-28, cada uno con resultados distintos). `DD-MM-AAAA` devuelve un fragmento vacío y `DD/MM/AAAA` devuelve la página completa; no usar.
- Cómo sacar los lanzamientos de hoy: pedir `.../dia/<hoy>/es` y parsear:
  - Cada lanzamiento está en un bloque `div.row` dentro de `div.col-xl-9`.
  - Hora: `div.text-calendario.text-center` (texto "16:00hs").
  - Título: `div.cal-content.text-calendario` (texto del informe, ej. "Estimador mensual de actividad económica (EMAE). Agosto de 2026").
  - Fecha/hora exacta de respaldo: enlace "Agregar a Google Calendar" (`a[href*="calendar.google.com"]`), parámetro `dates=AAAAMMDDTHHMMSS/...` y `ctz=America/Argentina/Buenos_Aires`.
  - El `<a>` del título no tiene `href` (el informe se abre por JavaScript), así que el link del radar debe ser la página general `https://www.indec.gob.ar/indec/web/Calendario-Fecha-0` o la de la fecha.
- Ejemplo hoy (21/10/2026): 16:00hs "Estimador mensual de actividad económica (EMAE). Agosto de 2026"; 16:00hs "Índice de salarios. Agosto de 2026".
- Caveats: las horas son de Buenos Aires. Las fuentes no tienen un feed; el endpoint es interno y podría cambiar. Conviene guardar la respuesta y avisar si cambia la estructura.

---

## 5. Boletín Oficial de la República Argentina: Primera sección

- RSS: NO funciona. `https://www.boletinoficial.gob.ar/rss` y `https://www.boletinoficial.gob.ar/rss/` devuelven la página de inicio en HTML (~24 KB).
- HTML que sí funciona: `https://www.boletinoficial.gob.ar/seccion/primera` (200, ~146 KB). Muestra la edición del día.
- Selectores:
  - Sección o rubro: `h5.seccion-rubro` (ej. "RESOLUCIONES", "DISPOSICIONES", "AVISOS OFICIALES", "CONVENCIONES COLECTIVAS DE TRABAJO", "TRATADOS Y CONVENIOS INTERNACIONALES", "RESOLUCIONES CONJUNTAS").
  - Cada norma: `a[href^="/detalleAviso/primera/"]`. El href tiene el ID de la norma y la fecha de la edición: `/detalleAviso/primera/349355/20261021`. Link completo: `https://www.boletinoficial.gob.ar` + href.
  - Organismo que la emite: `a p.item` (1er párrafo, ej. "ADMINISTRACIÓN NACIONAL DE AVIACIÓN CIVIL").
  - Título corto de la norma: `a p.item-detalle` (1er párrafo: "Resolución 808/2026"; 2do: código "RESOL-2026-808-APN-ANAC#MEC").
- Ejemplo 1: ADMINISTRACIÓN NACIONAL DE AVIACIÓN CIVIL, "Resolución 808/2026" · https://www.boletinoficial.gob.ar/detalleAviso/primera/349355/20261021
- Ejemplo 2: ADMINISTRACIÓN NACIONAL DE AVIACIÓN CIVIL, "Resolución 809/2026" · https://www.boletinoficial.gob.ar/detalleAviso/primera/349356/20261021
- Total en la prueba: 52 avisos de hoy.
- Caveats: la página también trae secciones con el sufijo "- ANTERIOR" (ej. "DISPOSICIONES - ANTERIOR"). Parecen ser de la edición anterior; conviene filtrarlas por la fecha del href (`/AAAAMMDD`) antes de publicar. El HTML no trae un título descriptivo (el título largo está en la página de detalle). No hay fecha de publicación en el listado más allá de la del href.

---

## 6. CEPA (Centro de Economía Política Argentina)

- Feed RSS: `https://centrocepa.com.ar/documentos/informes?format=feed&type=rss` (200, application/rss+xml, 15 ítems). Canal: "Informes - Centro CEPA".
- Alternativa Atom: `https://centrocepa.com.ar/documentos/informes?format=feed&type=atom` (200, 32 KB).
- NO funciona: `https://centrocepa.com.ar/feed` (404). La portada no tiene `<link rel="alternate">` de RSS.
- Listado HTML de respaldo: `https://centrocepa.com.ar/documentos/informes` (200, ~46 KB). Cada informe tiene su link `/documentos/informes/<id>-<slug>`.
- Mapeo: `item > title`, `item > link`, `item > guid`, `item > pubDate` (RFC 822, -0300), `item > category` ("Informes"), `item > description` (HTML con imagen y "Resumen ejecutivo").
- Ejemplo 1: "El mercado inmobiliario en CABA: datos al 3° trimestre 2026" · https://centrocepa.com.ar/documentos/informes/872-el-mercado-inmobiliario-en-caba-datos-al-3-trimestre-2026 · Fri, 16 Oct 2026 21:06:25 -0300
- Ejemplo 2: "Financiamiento de la Educación Universitaria: análisis de la evolución considerando presupuesto 2028" · https://centrocepa.com.ar/documentos/informes/874-financiamiento-de-la-educacion-universitaria-analisis-de-la-evolucion-considerando-presupuesto-2028 · Thu, 15 Oct 2026 00:29:45 -0300
- Caveats: publica con poca frecuencia. En la prueba no había ítems de los últimos 2 días (los más nuevos son del 15 y 16 de octubre), así que el radar puede mostrar "sin novedades" con frecuencia. Para ver si hubo algo nuevo, comparar `guid` con la corrida anterior.

---

## Notas generales para el recolector

- User-Agent: todas las pruebas usaron `Mozilla/5.0`. Conviene mandarlo siempre.
- Tiempo de espera: 20 segundos por URL fue suficiente. No se observó bloqueo ni límite de tasa en las pruebas (unas 60 peticiones en total).
- Tamaño: los feeds de Infobae, La Nación y TN pesan 0,5 a 1 MB. Conviene pedirlos una vez por corrida, no por sección cuando el feed general basta.
- Fechas: los formatos cambian entre medios (RFC 822 con -0300 o +0000, ISO 8601 en TN, y la hora fija "03:01:00" de Página/12). Normalizar todo a `America/Argentina/Buenos_Aires`.
- Ventana de 24 h: Clarín y CEPA traen pocos ítems o ninguno reciente; el recolector debe tolerar listas vacías y registrarlo en `estado_fuentes`.
