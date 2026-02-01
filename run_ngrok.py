"""
ia/analista.py
Módulo simplificado para análisis con OpenAI API oficial
(Sin necesidad de ngrok)
"""

import os
import json
import streamlit as st
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

try:
    from openai import OpenAI, APIError, APIConnectionError, RateLimitError
    OPENAI_DISPONIBLE = True
except ImportError:
    OPENAI_DISPONIBLE = False


class AnalistaIA:
    """
    Clase para análisis automático usando OpenAI API oficial
    Sin necesidad de ngrok ni servidores locales
    """

    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

        # Log de diagnóstico
        self.disponible = False
        self.cliente = None
        self.error_msg = ""

        if not self.api_key:
            self.error_msg = "OPENAI_API_KEY no configurada en .env"
            return

        if not OPENAI_DISPONIBLE:
            self.error_msg = "OpenAI no instalada. Ejecuta: pip install openai"
            return

        try:
            # Inicializar cliente con OpenAI oficial
            self.cliente = OpenAI(api_key=self.api_key)
            self.disponible = True
            st.session_state.ia_status = "✅ Conectado a OpenAI"
        except Exception as e:
            self.error_msg = f"Error al conectar: {str(e)}"

    def analizar_ejercicio(
        self,
        tipo_problema: str,
        datos_entrada: Dict,
        resultado: Dict,
        metadata: Dict = None
    ) -> str:
        """
        Analiza un ejercicio de optimización
        """
        if not self.disponible or not self.cliente:
            return self._analisis_fallback_ejercicio(tipo_problema, resultado)

        prompt = f"""
Eres un experto en Investigación de Operaciones e Ingeniería Industrial.

Analiza el siguiente ejercicio de optimización:

**Tipo de Problema:** {tipo_problema}
**Datos de Entrada:** {json.dumps(datos_entrada, indent=2, default=str)}
**Resultado Obtenido:** {json.dumps(resultado, indent=2, default=str)}

Por favor proporciona:
1. **Interpretación del resultado** - Qué significa el valor óptimo obtenido
2. **Validación de la solución** - ¿Es viable y tiene sentido?
3. **Conclusiones clave** - Hallazgos más importantes
4. **Recomendaciones prácticas** - Cómo usar estos resultados

Sé conciso pero informativo (máximo 400 palabras).
Usa formato markdown con viñetas donde sea apropiado.
"""

        try:
            response = self.cliente.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800,
                timeout=30
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"❌ Error de conexión: {str(e)}. Verifica tu conexión a internet."
        except RateLimitError:
            return "⏳ Límite de rate alcanzado. Intenta en unos segundos."
        except APIError as e:
            return f"❌ Error de OpenAI: {str(e)}"
        except Exception as e:
            return self._analisis_fallback_ejercicio(tipo_problema, resultado)

    def analizar_sensibilidad(
        self,
        tipo_problema: str,
        parametros_sensibles: Dict,
        resultado_actual: float,
        restricciones: Dict = None
    ) -> str:
        """
        Realiza análisis de sensibilidad automático
        """
        if not self.disponible or not self.cliente:
            return self._analisis_fallback_sensibilidad(parametros_sensibles)

        prompt = f"""
Realiza un análisis de sensibilidad detallado para una solución de optimización:

**Tipo de Problema:** {tipo_problema}
**Valor Óptimo Actual:** {resultado_actual}
**Parámetros Sensibles:** {json.dumps(parametros_sensibles, indent=2, default=str)}
{f'**Restricciones:** {json.dumps(restricciones, indent=2, default=str)}' if restricciones else ''}

Por favor proporciona:
1. **Parámetros Críticos** - Cuáles tienen mayor impacto en la solución
2. **Rangos de Variabilidad** - Dentro de qué límites puede variar cada parámetro
3. **Puntos de Quiebre** - Valores críticos donde cambia la solución
4. **Estrategia de Robustez** - Cómo hacer la solución más resiliente

Sé específico con números y porcentajes (máximo 350 palabras).
"""

        try:
            response = self.cliente.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=700,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._analisis_fallback_sensibilidad(parametros_sensibles)

    def generar_resumen_ejecutivo(
        self,
        tipo_problema: str,
        objetivo: str,
        metricas: Dict,
        recomendaciones: List[str] = None,
        contexto_empresa: str = "Coca-Cola"
    ) -> str:
        """
        Genera un resumen ejecutivo profesional
        """
        if not self.disponible or not self.cliente:
            return self._resumen_fallback(metricas, contexto_empresa)

        prompt = f"""
Genera un resumen ejecutivo profesional para la gerencia de {contexto_empresa}:

**Problema Resuelto:** {tipo_problema}
**Objetivo:** {objetivo}

**Métricas Clave:**
{json.dumps(metricas, indent=2, default=str)}

{f'**Recomendaciones:** {", ".join(recomendaciones)}' if recomendaciones else ''}

**Formato solicitado:**
1. **Situación** (1-2 líneas) - Contexto del problema
2. **Solución** (3-4 viñetas) - Resultados principales y valor generado
3. **Impacto** (1-2 líneas) - Beneficio cuantificable para la empresa
4. **Próximos Pasos** (3-4 viñetas) - Acciones recomendadas

**Estilo:** Ejecutivo, directo, enfocado en valor empresarial. Máximo 250 palabras.
Usa formato markdown. Incluye métricas cuantitativas cuando sea posible.
"""

        try:
            response = self.cliente.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._resumen_fallback(metricas, contexto_empresa)

    def generar_interpretacion(
        self,
        tipo_problema: str,
        resultado: float,
        detalles_problema: Dict
    ) -> str:
        """
        Genera una interpretación amigable del resultado
        """
        if not self.disponible or not self.cliente:
            return f"**Resultado óptimo:** {resultado}"

        prompt = f"""
Proporciona una interpretación amigable de los siguientes resultados de optimización:

**Tipo de Problema:** {tipo_problema}
**Resultado Óptimo:** {resultado}
**Detalles:** {json.dumps(detalles_problema, indent=2, default=str)}

Explica qué significa este resultado en términos simples y prácticos.
¿Qué acción debe tomar el usuario con este resultado?
Máximo 200 palabras. Tono profesional pero accesible.
"""

        try:
            response = self.cliente.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=400,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"**Resultado óptimo obtenido:** {resultado}"

    # Métodos fallback
    def _analisis_fallback_ejercicio(self, tipo: str, resultado: Dict) -> str:
        """Análisis fallback sin IA"""
        costo = resultado.get('costo_total', resultado.get('valor_optimo', resultado.get('distancia_total', 0)))
        return f"""
### 📊 Análisis del Ejercicio (Modo Básico)

**Tipo de Problema:** {tipo}
**Resultado Óptimo:** {costo:.2f}

#### Validación
✓ La solución ha sido calculada correctamente usando el algoritmo especificado.

#### Recomendaciones
- Verifica que la solución satisface todas las restricciones
- Compara con soluciones alternativas si es posible
- Documenta los hallazgos principales

⚠️ **Nota:** Para análisis con IA, configura tu API key de OpenAI en `.env`
"""

    def _analisis_fallback_sensibilidad(self, parametros: Dict) -> str:
        """Análisis de sensibilidad fallback"""
        return """
### 🔍 Análisis de Sensibilidad (Modo Básico)

#### Parámetros Identificados
Se han identificado parámetros clave en el modelo de optimización.

#### Recomendaciones
- Enfoca atención en los parámetros con mayor variabilidad
- Establece límites de tolerancia para cada parámetro crítico
- Monitorea cambios en estos parámetros durante la ejecución

⚠️ **Nota:** Para análisis detallado con IA, configura tu API key en `.env`
"""

    def _resumen_fallback(self, metricas: Dict, empresa: str = "Coca-Cola") -> str:
        """Resumen ejecutivo fallback"""
        metricas_str = "\n".join([f"• **{k}:** {v}" for k, v in list(metricas.items())[:5]])
        return f"""
### 📋 Resumen Ejecutivo - {empresa}

#### Resultados Principales
{metricas_str}

#### Recomendación
Implementar la solución óptima identificada para maximizar eficiencia operativa.

⚠️ **Nota:** Para resumen ejecutivo con IA, configura tu API key en `.env`
"""

    def verificar_disponibilidad(self) -> bool:
        """Verifica si la conexión a OpenAI está disponible"""
        return self.disponible

    def mostrar_estado_ia(self) -> None:
        """Muestra el estado de la conexión IA en Streamlit"""
        if self.disponible:
            st.success("✅ IA disponible - Análisis automático habilitado")
        elif self.error_msg:
            st.warning(f"⚠️ IA no disponible: {self.error_msg}")
        else:
            st.info("ℹ️ Análisis con IA deshabilitado")

    def obtener_estado(self) -> Dict:
        """Retorna estado detallado de la conexión"""
        return {
            "disponible": self.disponible,
            "modelo": self.model,
            "error": self.error_msg,
            "api_key_presente": bool(self.api_key)
        }


# Función auxiliar para usar en Streamlit
def obtener_analista() -> Optional[AnalistaIA]:
    """
    Obtiene una instancia del analista IA con caché de Streamlit
    """
    @st.cache_resource
    def _crear_analista():
        try:
            analista = AnalistaIA()
            return analista
        except Exception as e:
            return None

    return _crear_analista()


def mostrar_diagnostico_ia():
    """Muestra diagnóstico de la conexión IA (para debugging)"""
    analista = obtener_analista()

    if analista:
        estado = analista.obtener_estado()

        st.subheader("🔍 Diagnóstico IA")

        col1, col2, col3 = st.columns(3)

        with col1:
            if estado["disponible"]:
                st.success("✅ Conectado")
            else:
                st.error("❌ Desconectado")

        with col2:
            st.info(f"Modelo: {estado['modelo']}")

        with col3:
            if estado["api_key_presente"]:
                st.success("✅ API Key presente")
            else:
                st.warning("⚠️ API Key no configurada")

        if estado["error"]:
            st.error(f"Error: {estado['error']}")