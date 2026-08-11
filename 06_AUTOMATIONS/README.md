# AUTOMATIONS

## Objetivo
Reducir el trabajo manual repetitivo.

## Automatizaciones objetivo
- Investigación de tendencias.
- Generación de ideas.
- Guiones.
- Voz.
- Edición.
- Subtítulos.
- Repurpose entre plataformas.
- Calendario de publicación.
- Seguimiento de métricas.
- Organización de archivos.
- Backups de contexto y prompts.

## Principio
Automatizar después de validar que el proceso manual produce resultados.

---

## Ya funcionando

### `crear_video.py` — arma el video solo (reemplaza CapCut)

Junta las imágenes + el audio y saca el video vertical listo, con zoom lento
automático en cada imagen para que no se vea quieto.

```bash
python crear_video.py <carpeta_imagenes> <audio.mp3> <video_salida.mp4>
```

Necesita ffmpeg instalado (ya lo está en esta computadora):
`winget install --id Gyan.FFmpeg -e`

## Qué está automático y qué no

| Paso | ¿Automático? |
|---|---|
| Buscar tendencias e ideas | Sí |
| Escribir el guion | Sí |
| Generar la voz (ElevenLabs) | Sí |
| Crear las imágenes (Canva) | Sí |
| Armar el video | Sí (`crear_video.py`) |
| Poner subtítulos | No — se hace en CapCut |
| Publicar en TikTok / Shorts / Reels | No — hay que subirlo a mano |

Los dos últimos pasos no tienen conexión disponible, así que se hacen a mano.
