#!/usr/bin/env python3
"""Transcribe los audios del chat de WhatsApp exportado (.opus, .ogg, .m4a, .mp3 o .wav).

Uso: python3 -I tr.py audio1.opus [audio2.opus ...] > transcripcion.txt

Necesita ffmpeg y faster-whisper (pip install faster-whisper numpy). La primera vez baja el
modelo "small". El .opus se pasa a WAV de 16 kHz con ffmpeg porque la librería falla al leerlo
directo; el WAV se lee con numpy (la versión de av instalada no acepta metadata_errors).
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from faster_whisper import WhisperModel


def a_wav(ruta, carpeta):
    if ruta.lower().endswith(".wav"):
        return ruta
    salida = os.path.join(carpeta, os.path.basename(ruta) + ".wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ruta, "-ac", "1", "-ar", "16000", salida], check=True)
    return salida


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    with tempfile.TemporaryDirectory() as tmp:
        for ruta in sys.argv[1:]:
            w = wave.open(a_wav(ruta, tmp))
            audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            partes, _ = modelo.transcribe(audio, language="es", beam_size=5)
            print("=== " + os.path.basename(ruta))
            print(" ".join(p.text.strip() for p in partes))
            print()


if __name__ == "__main__":
    main()
