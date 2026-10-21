# Radar de Agenda

Panel gratuito de temas del momento en Argentina (noticias + tendencias de X) pensado para un equipo de comunicación política. Se actualiza solo cuatro veces por día (8, 12, 16 y 20 hs) y se publica en GitHub Pages.

No usa claves, no usa IA y no cuesta nada: un script en Python (solo biblioteca estándar) junta las fuentes, agrupa los titulares por tema y escribe un JSON que lee la página.

## Qué junta

- Medios: Infobae, Clarín, La Nación, Página/12, Ámbito y TN (RSS, últimas 24 h).
- Tendencias de X Argentina (trends24, con getdaytrends de respaldo) y Google Trends AR.
- Agenda del día: calendario del INDEC.
- Fuentes oficiales: Boletín Oficial (primera sección) y CEPA.

Si una fuente falla, el resto sigue funcionando y la falla queda registrada en el panel ("Estado de las fuentes").

## Cómo correrlo a mano

Hace falta Python 3.9 o más nuevo (viene en la Mac). Desde esta carpeta:

```
python3 scripts/recolectar.py
```

Escribe `sitio/data/tendencias.json` y una copia diaria en `sitio/data/archivo/AAAA-MM-DD.json`.

Para ver la página en tu compu:

```
cd sitio
python3 -m http.server 8765
```

y abrí http://localhost:8765

## Cómo se actualiza solo

`.github/workflows/actualizar.yml` corre en GitHub Actions a las 8:07, 12:07, 16:07 y 20:07 (hora Argentina), guarda los datos nuevos en el repositorio y publica la carpeta `sitio/` en GitHub Pages. También se puede lanzar a mano desde la pestaña Actions ("Run workflow"), y corre cuando cambia algo dentro de `sitio/` en la rama `main`.

Para activarlo: en el repositorio, Settings > Pages > Source: "GitHub Actions".

## Estructura

- `scripts/recolectar.py`: el recolector.
- `sitio/`: la página (`index.html`) y los datos (`data/`).
- `notas/`: contrato del JSON (`ESQUEMA.md`) y notas sobre las fuentes (`FUENTES.md`).
