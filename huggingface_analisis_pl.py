# huggingface_analisis_pl.py - CORREGIDO
import requests
from typing import List

MODELOS_DISPONIBLES = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.1",
    "llama2": "meta-llama/Llama-2-7b-chat-hf",
}

MODEL_ACTUAL = "mistral"
API_TOKEN = None


def configurar_huggingface(api_token=None, modelo="mistral"):
    global MODEL_ACTUAL, API_TOKEN
    MODEL_ACTUAL = modelo
    API_TOKEN = api_token


def generar_analisis_huggingface(origen, rutas, iteraciones, total_nodos):
    """Genera análisis con Hugging Face - Compatible con Gemini"""
    rutas_texto = ""
    for r in rutas:
        rutas_texto += f"- Destino: {r['destino']}\n  Distancia: {r['distancia']}\n  Ruta: {r['ruta']}\n\n"

    prompt = f"""INSTRUCCIÓN:
Redacta un texto académico EN ESPAÑOL con lenguaje matemático formal.
NO repitas el enunciado del problema.
RESPONDE ÚNICAMENTE con las secciones solicitadas.

ESTRUCTURA OBLIGATORIA (respétala exactamente):

ANÁLISIS DE SENSIBILIDAD:
(explica cómo cambios en los pesos afectan las rutas óptimas)

CONCLUSIONES:
(interpreta el comportamiento matemático del sistema)

RECOMENDACIONES:
(propón mejoras a la red y decisiones operativas)

DATOS DEL PROBLEMA:
Nodo origen: {origen}
Total de nodos: {total_nodos}
Iteraciones: {iteraciones}

RUTAS ÓPTIMAS CALCULADAS:
{rutas_texto}"""

    try:
        modelo_url = MODELOS_DISPONIBLES.get(MODEL_ACTUAL, MODELOS_DISPONIBLES["mistral"])
        url = f"https://api-inference.huggingface.co/models/{modelo_url}"
        headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.3,
                "top_p": 0.95,
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=120)

        if response.status_code == 200:
            resultado = response.json()
            if isinstance(resultado, list) and len(resultado) > 0:
                respuesta = resultado[0].get("generated_text", "").strip()
                if prompt in respuesta:
                    respuesta = respuesta.split(prompt)[-1].strip()
                return respuesta if respuesta else "Error: Respuesta vacía"
            return "Error: Formato de respuesta inesperado"
        elif response.status_code == 429:
            return "⚠️ LÍMITE ALCANZADO. Obtén token gratis en: https://huggingface.co/settings/tokens"
        elif response.status_code == 401:
            return "❌ Token inválido o expirado. Obtén uno en: https://huggingface.co/settings/tokens"
        else:
            return f"Error HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"Error: {str(e)}"