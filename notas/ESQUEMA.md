# Esquema de datos: sitio/data/tendencias.json

Contrato compartido entre el recolector (scripts/) y la página (sitio/index.html).

```json
{
  "actualizado": "2026-10-21T16:00:00-03:00",
  "proxima_actualizacion": "2026-10-21T20:00:00-03:00",
  "ia_disponible": true,
  "agenda_hoy": [
    {"hora": "16:00", "titulo": "IPC septiembre", "fuente": "INDEC", "link": "https://..."}
  ],
  "temas": [
    {
      "id": "inflacion-septiembre",
      "titulo": "Dato de inflación de septiembre",
      "categoria": "economia",
      "prioritaria": true,
      "desde": "2026-10-21T16:05:00-03:00",
      "calor": 87,
      "medios": ["Infobae", "Clarín", "La Nación"],
      "en_x": true,
      "posicion_x": 2,
      "en_google": true,
      "notas": [
        {"medio": "Infobae", "titulo": "...", "link": "https://...", "hora": "2026-10-21T16:10:00-03:00"}
      ],
      "oficiales": [
        {"fuente": "INDEC", "titulo": "...", "link": "https://..."}
      ],
      "resumen": "Una línea o null si no hay IA",
      "angulos": ["...", "..."]
    }
  ],
  "tendencias_x": [{"posicion": 1, "nombre": "#Inflacion", "link": "https://x.com/search?q=..."}],
  "google_trends": [{"nombre": "inflación", "trafico": "50 mil+", "link": "https://..."}],
  "estado_fuentes": [{"fuente": "Infobae", "ok": true, "items": 40}]
}
```

- `categoria`: economia | politica | trabajo | jubilaciones | social | deportes | espectaculos | otros
- `prioritaria` = categoria en {economia, politica, trabajo, jubilaciones, social}
- `calor`: 0–100. Sube con cantidad de medios, presencia en X / Google y novedad.
- `temas` ordenados por `calor` descendente. Ventana: últimas 24 h.
- Archivo diario: `sitio/data/archivo/AAAA-MM-DD.json` (mismo formato, última corrida del día).
