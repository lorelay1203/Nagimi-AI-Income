"""
Arma un video vertical (para TikTok / Shorts / Reels) juntando imagenes + audio.

Cada imagen lleva un zoom lento automatico para que el video NO se vea quieto
ni aburrido. La duracion de cada imagen se calcula sola para que todo cuadre
exacto con el audio.

USO:
    python crear_video.py <carpeta_imagenes> <archivo_audio> <video_salida>

EJEMPLO:
    python crear_video.py ../03_CONTENT_FACTORY/GUIONES/001_imagenes \
                          ../03_CONTENT_FACTORY/GUIONES/001_audio.mp3 \
                          ../03_CONTENT_FACTORY/GUIONES/001_video.mp4

Las imagenes se ordenan por nombre de archivo (1_, 2_, 3_...).
"""

import os
import subprocess
import sys
from pathlib import Path

# Formato vertical para redes sociales
ANCHO, ALTO, FPS = 1080, 1920, 30

# Rutas donde puede estar ffmpeg si no esta en el PATH del sistema
RUTAS_FFMPEG = [
    r"C:\Users\lorel\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0-full_build\bin",
]


def buscar(programa):
    """Devuelve la ruta a ffmpeg/ffprobe, buscando primero en el PATH."""
    from shutil import which

    encontrado = which(programa)
    if encontrado:
        return encontrado
    for carpeta in RUTAS_FFMPEG:
        candidato = Path(carpeta) / f"{programa}.exe"
        if candidato.exists():
            return str(candidato)
    sys.exit(
        f"ERROR: no encuentro {programa}. Instalalo con:\n"
        f"    winget install --id Gyan.FFmpeg -e"
    )


FFMPEG = buscar("ffmpeg")
FFPROBE = buscar("ffprobe")


def duracion_audio(ruta_audio):
    """Lee cuantos segundos dura el audio."""
    salida = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ruta_audio)],
        capture_output=True, text=True, check=True,
    )
    return float(salida.stdout.strip())


def filtro_zoom(indice, segundos):
    """
    Construye el efecto de zoom lento para una imagen.

    Alterna: las imagenes pares hacen zoom hacia adentro, las impares hacia
    afuera. Asi el video no se siente repetitivo.
    """
    frames = max(int(segundos * FPS), 1)
    # Se agranda la imagen antes de hacer zoom para que se vea nitido y no tiemble
    base = (
        f"scale={ANCHO * 2}:{ALTO * 2}:force_original_aspect_ratio=increase,"
        f"crop={ANCHO * 2}:{ALTO * 2},setsar=1"
    )

    if indice % 2 == 0:
        # Acercarse poco a poco
        zoom = "min(zoom+0.0009,1.18)"
    else:
        # Alejarse poco a poco (empieza acercado)
        zoom = "if(lte(zoom,1.001),1.18,max(zoom-0.0009,1.0))"

    return (
        f"{base},zoompan=z='{zoom}':d={frames}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={ANCHO}x{ALTO}:fps={FPS}"
    )


def crear_video(carpeta_imagenes, ruta_audio, ruta_salida):
    carpeta = Path(carpeta_imagenes)
    imagenes = sorted(
        p for p in carpeta.iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    )
    if not imagenes:
        sys.exit(f"ERROR: no hay imagenes en {carpeta}")

    total = duracion_audio(ruta_audio)
    # Cada imagen dura lo mismo; todas juntas cubren el audio completo
    por_imagen = total / len(imagenes)

    print(f"Imagenes: {len(imagenes)}")
    print(f"Audio: {total:.1f} segundos")
    print(f"Cada imagen: {por_imagen:.1f} segundos")
    if por_imagen > 6:
        print(
            f"AVISO: {por_imagen:.1f}s por imagen es mucho para redes sociales.\n"
            f"       Con {len(imagenes)} imagenes se ve lento. Para este audio\n"
            f"       lo ideal serian {int(total / 5)}-{int(total / 4)} imagenes."
        )

    comando = [FFMPEG, "-y"]
    for imagen in imagenes:
        comando += ["-loop", "1", "-t", f"{por_imagen:.3f}", "-i", str(imagen)]
    comando += ["-i", str(ruta_audio)]

    # Se le aplica el zoom a cada imagen y luego se pegan una tras otra
    partes = [
        f"[{i}:v]{filtro_zoom(i, por_imagen)}[v{i}]"
        for i in range(len(imagenes))
    ]
    cadena = "".join(f"[v{i}]" for i in range(len(imagenes)))
    partes.append(f"{cadena}concat=n={len(imagenes)}:v=1:a=0[vid]")

    comando += [
        "-filter_complex", ";".join(partes),
        "-map", "[vid]",
        "-map", f"{len(imagenes)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        # Se corta exacto en el largo del audio, para que no quede
        # un pedazo final en silencio
        "-t", f"{total:.3f}",
        str(ruta_salida),
    ]

    print("\nArmando el video... (esto tarda un poco)")
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        print(resultado.stderr[-2500:])
        sys.exit("ERROR: no se pudo armar el video.")

    tamano = os.path.getsize(ruta_salida) / (1024 * 1024)
    print(f"\nLISTO: {ruta_salida}  ({tamano:.1f} MB)")
    print("Falta ponerle los subtitulos antes de publicar (ver ESTRATEGIA.md).")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    crear_video(sys.argv[1], sys.argv[2], sys.argv[3])
