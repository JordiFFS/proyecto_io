# ollama_analisis_pl.py - CON TIMEOUT AUMENTADO Y PROMPT OPTIMIZADO
import requests
import socket

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def verificar_ollama_disponible():
    """Verifica si Ollama está corriendo"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, socket.error):
        return False
    except:
        return False


def generar_analisis_ollama(origen, rutas, iteraciones, total_nodos):
    """Genera análisis con Ollama - Compatible con Gemini"""

    if not verificar_ollama_disponible():
        return """⚠️ OLLAMA NO DISPONIBLE

Para usar Ollama:
1. Abre una terminal y ejecuta: ollama serve
2. En otra terminal ejecuta: ollama pull llama2
3. Espera a que termine
4. Vuelve a intentar

Mientras tanto, usa Gemini o Hugging Face."""

    rutas_texto = ""
    for r in rutas:
        rutas_texto += f"- Destino: {r['destino']}, Distancia: {r['distancia']}, Ruta: {r['ruta']}\n"

    # Prompt más corto y directo para evitar procesamiento largo
    prompt = f"""Analiza este problema de ruta más corta y proporciona:

ANÁLISIS DE SENSIBILIDAD:
Cómo cambios en los pesos afectan las rutas óptimas

CONCLUSIONES:
Comportamiento matemático del sistema

RECOMENDACIONES:
Mejoras a la red

DATOS:
- Origen: {origen}
- Nodos totales: {total_nodos}
- Iteraciones: {iteraciones}
- Rutas:
{rutas_texto}"""

    try:
        print(f"📡 Enviando solicitud a Ollama (esto puede tardar 2-5 minutos)...")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 500,  # Limita la salida a 500 tokens
            },
            timeout=600  # 10 minutos en lugar de 2
        )

        if response.status_code == 200:
            resultado = response.json()
            respuesta = resultado.get("response", "").strip()
            return respuesta if respuesta else "Error: Respuesta vacía de Ollama"
        else:
            return f"❌ Error HTTP {response.status_code} de Ollama. Intenta de nuevo."

    except requests.exceptions.Timeout:
        return """⏱️ TIMEOUT: Ollama tardó demasiado (>10 min)

SOLUCIONES:
1. Tu PC es lenta para procesar - Intenta con Gemini o Hugging Face
2. Si quieres seguir con Ollama:
   - Descarga un modelo más pequeño: ollama pull orca-mini
   - O usa: ollama pull neural-chat (más rápido que llama2)

3. Edita ollama_analisis_pl.py y cambia MODEL_NAME = "orca-mini"
"""

    except requests.exceptions.ConnectionError:
        return """❌ Ollama desconectado

Solución:
1. Abre una terminal
2. Ejecuta: ollama serve
3. Mantén esa terminal abierta
4. Vuelve a intentar
"""
    except Exception as e:
        return f"❌ Error: {str(e)}"