"""
Archivo: gemini_pruebas.py
Integrado en resolucion_ruta_mas_corta.py
Genera un análisis académico usando Gemini (Google)
"""

import google.generativeai as genai
import os

# ======================================================
# 🔑 CONFIGURACIÓN DEL TOKEN DE GEMINI
# ======================================================
def configurar_gemini():
    """Configura Gemini con la API key"""
    api_key = "AIzaSyCgqQn0Ok2n91mHooDByTUHbgnM8M2LuEg"
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno")
    genai.configure(api_key=api_key)

try:
    configurar_gemini()
except ValueError as e:
    print(f"⚠️ Advertencia: {e}")

MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)


def generar_analisis_gemini(origen, rutas, iteraciones, total_nodos) -> str:
    """
    Genera análisis académico usando Gemini

    Args:
        origen: Nodo origen del análisis
        rutas: Lista de rutas con destino, distancia y ruta óptima
        iteraciones: Número de iteraciones del algoritmo
        total_nodos: Total de nodos en la red

    Returns:
        str: Análisis académico generado por Gemini
    """

    rutas_texto = ""
    for r in rutas:
        rutas_texto += (
            f"- Destino: {r['destino']}\n"
            f"  Distancia mínima: {r['distancia']}\n"
            f"  Ruta óptima: {r['ruta']}\n\n"
        )

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
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1000,
                "top_p": 0.95,
            }
        )

        respuesta = response.text.strip()
        return respuesta

    except Exception as e:
        return f"Error al generar análisis con Gemini: {str(e)}"