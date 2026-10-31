# Instrucciones para agentes: herramientas de PC Soluciones

Leer `LEEME.md`. Índice general de PC Soluciones: documento del proyecto `claude/indice-cerebro.md`. Lista de reglas y su origen: `claude/reglas-verificables.md`.

- `revisar.py` solo lee. Nunca le agregues algo que cambie archivos: corregir es tarea de quien lo usa.
- Una regla entra al revisor solo si un script la puede decidir sin equivocarse seguido. Si hace falta criterio (títulos directos, explicar lo que sí, tono), queda para un revisor humano o agente.
- Si una regla da falsos positivos en material real, se ajusta o se baja a AVISO; no se deja sonando.
- Cada regla nueva entra con su caso de prueba en `pruebas/` y `python3 pruebas/correr.py` tiene que pasar.
- Sin bibliotecas externas: tiene que correr en la Mac, en la PC con Windows y en la nube tal cual.
- Documentación en español neutro con tuteo, sin guiones largos. Commits firmados como Manuel Tonnelier (pcsolucionesbelgrano@gmail.com).
