#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Streamlit con ngrok
Expone la aplicación localmente y genera una URL pública
"""

import subprocess
import time
import os
import sys
from pathlib import Path


def ejecutar_app_con_ngrok(puerto: int = 8501, token_ngrok: str = None):
    """
    Ejecuta la aplicación Streamlit y la expone con ngrok

    Parámetros:
    - puerto: puerto en el que ejecutar streamlit (default: 8501)
    - token_ngrok: token de autenticación de ngrok (opcional)
    """

    # Verificar que ngrok esté disponible
    try:
        subprocess.run(['ngrok', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ngrok no está instalado o no está en PATH")
        print("\nPara instalar ngrok:")
        print("  Windows: choco install ngrok")
        print("  Linux/Mac: brew install ngrok")
        print("  O descargar desde: https://ngrok.com/download")
        sys.exit(1)

    # Si se proporciona token, configurar ngrok
    if token_ngrok:
        subprocess.run(['ngrok', 'config', 'add-authtoken', token_ngrok])
        print("✓ Token de ngrok configurado")

    print("\n" + "=" * 80)
    print("🚀 INICIANDO APLICACIÓN DE INVESTIGACIÓN OPERATIVA")
    print("=" * 80)
    print(f"📍 Inicio en: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔌 Puerto local: {puerto}")
    print("\nAbriendo túneles...")

    # Iniciar ngrok en segundo plano
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(puerto), '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Esperar a que ngrok se inicialice
    time.sleep(3)

    # Iniciar Streamlit
    print("\n✓ ngrok iniciado")
    print("✓ Iniciando Streamlit...\n")

    streamlit_process = subprocess.Popen(
        ['streamlit', 'run', 'app.py', f'--server.port={puerto}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(f"✓ Streamlit ejecutándose en: http://localhost:{puerto}")
    print("\n" + "=" * 80)
    print("🌐 URL PÚBLICA (ngrok): https://<id>.ngrok.io")
    print("=" * 80)
    print("\nPara ver la URL pública:")
    print("  1. Abre: http://localhost:4040 (panel de ngrok)")
    print("  2. O busca en los logs de ngrok la URL pública\n")

    try:
        # Esperar a que alguno de los procesos termine
        while True:
            if ngrok_process.poll() is not None:
                print("\n⚠️ ngrok se ha detenido")
                break
            if streamlit_process.poll() is not None:
                print("\n⚠️ Streamlit se ha detenido")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n📋 Deteniendo aplicación...")
        streamlit_process.terminate()
        ngrok_process.terminate()
        streamlit_process.wait(timeout=5)
        ngrok_process.wait(timeout=5)
        print("✓ Aplicación detenida correctamente")


def ejecutar_app_local():
    """Ejecuta solo la aplicación Streamlit sin ngrok"""
    print("\n" + "=" * 80)
    print("🚀 INICIANDO APLICACIÓN (MODO LOCAL)")
    print("=" * 80)
    print("📍 Accede a: http://localhost:8501")
    print("⏹️  Presiona Ctrl+C para detener\n")

    subprocess.run(['streamlit', 'run', 'app.py'])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Ejecutor de aplicación Streamlit con opciones de ngrok"
    )

    parser.add_argument(
        '--ngrok',
        action='store_true',
        help='Ejecutar con ngrok para acceso público'
    )

    parser.add_argument(
        '--token',
        type=str,
        help='Token de autenticación de ngrok'
    )

    parser.add_argument(
        '--puerto',
        type=int,
        default=8501,
        help='Puerto para Streamlit (default: 8501)'
    )

    parser.add_argument(
        '--local',
        action='store_true',
        help='Ejecutar solo localmente'
    )

    args = parser.parse_args()

    # Crear estructura de directorios si no existe
    Path('models/programacion_lineal').mkdir(parents=True, exist_ok=True)
    Path('models/transporte').mkdir(parents=True, exist_ok=True)
    Path('models/redes').mkdir(parents=True, exist_ok=True)
    Path('models/inventarios').mkdir(parents=True, exist_ok=True)
    Path('ia').mkdir(parents=True, exist_ok=True)
    Path('empresa').mkdir(parents=True, exist_ok=True)
    Path('utils').mkdir(parents=True, exist_ok=True)

    if args.ngrok:
        ejecutar_app_con_ngrok(puerto=args.puerto, token_ngrok=args.token)
    else:
        ejecutar_app_local()