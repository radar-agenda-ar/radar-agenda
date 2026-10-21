# IA gratis desde GitHub Actions (investigado 2026-10-21)

**VEREDICTO: 100% gratis: NO** — con GitHub Models no es posible porque el servicio fue cerrado el 30 de julio de 2026. Lo que sigue siendo gratis es Actions (ver punto 5).

## 1. ¿Sigue disponible el plan gratis de GitHub Models?
No. GitHub Models está totalmente retirado: el playground, el catálogo de modelos, la API de inferencia y BYOK "ya no están disponibles para ningún cliente", incluidos los que ya lo usaban.
- Documentación oficial: https://docs.github.com/en/github-models ("As of July 30, 2026, GitHub Models has been fully retired.")
- Aviso del 1 de julio: https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/
- Aviso de cierre: https://github.blog/changelog/2026-07-30-github-models-is-now-retired/
- Consecuencia: ni `GITHUB_TOKEN` con `permissions: models: read` ni el endpoint de inferencia sirven ya. No verifiqué el endpoint antiguo (el servicio ya no existe), así que no lo documento.

## 2. Límites del plan gratis, 3. Facturación, 4. Modelo recomendado
No aplican: sin servicio no hay límites vigentes, ni opción de pago, ni modelo que recomendar. Las páginas de límites y facturación de GitHub Models solo muestran el aviso de retiro (https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-models).
Alternativas que cita GitHub (no evaluadas aquí, y ninguna garantiza ser gratis sin tarjeta):
- Azure AI Foundry: https://ai.azure.com/ (requiere cuenta Azure, normalmente con tarjeta).
- GitHub Copilot: https://docs.github.com/en/copilot (el plan Free solo da selección automática de modelo: https://docs.github.com/en/copilot/concepts/models ; no es una API para llamar desde Actions).
Siguiente paso sugerido: investigar por separado otro proveedor con capa gratuita sin tarjeta (p. ej. Gemini API, Groq, OpenRouter modelos ":free") y verificar sus límites actuales.

## 5. Minutos de Actions
- Los runners estándar alojados por GitHub son gratis en repos públicos, sin tope indicado; solo los runners "larger" se cobran siempre: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions
- Cron (`schedule`): https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
  - Puede haber retrasos en horas de mucha carga (sobre todo al inicio de cada hora) e incluso descartarse ejecuciones: programar en minutos "raros" (ej. `17 */6 * * *`).
  - Solo corre si el archivo está en la rama por defecto.
  - En repos públicos se desactiva tras 60 días sin actividad en el repo; se reactiva a mano (pestaña Actions > workflow > Enable). Para evitarlo: que el workflow haga un commit periódico (p. ej. actualizar un archivo de datos) o reactivarlo cada tanto.
  - Intervalo mínimo: 5 minutos.
