# views/resolucion_dual.py
import streamlit as st
import pandas as pd
from models.programacion_lineal.dual import Dual
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible


def ejemplo_dual_coca_cola():
    """Ejemplo real de Coca-Cola - Análisis Primal-Dual"""
    st.subheader("📊 Ejemplo: Análisis Primal-Dual - Coca-Cola")

    st.write("""
    **Problema PRIMAL:** Minimizar costos de distribución

    **Variables Primal:**
    - x₁ = Botellas Quito→Quito
    - x₂ = Botellas Quito→Guayaquil
    - x₃ = Botellas Guayaquil→Cuenca

    **Función Objetivo Primal:**
    Minimizar: 0.05x₁ + 0.15x₂ + 0.12x₃

    **Restricciones Primal:**
    - x₁ + x₂ ≤ 1,500,000 (Capacidad Planta Quito)
    - x₃ ≥ 0 (No negatividad)
    - x₁ ≥ 300,000 (Demanda mínima Quito)
    - x₂ ≥ 200,000 (Demanda mínima Guayaquil)
    - x₃ ≤ 500,000 (Capacidad máxima Cuenca)

    **Solución Óptima:**
    - x₁ = 300,000, x₂ = 200,000, x₃ = 0
    - Z = $45,000

    **Variables Dual (Precios Sombra):**
    - y₁ = Precio sombra capacidad Quito
    - y₂ = Precio sombra x₃ ≥ 0
    - y₃ = Precio sombra demanda Quito
    - y₄ = Precio sombra demanda Guayaquil
    - y₅ = Precio sombra capacidad Cuenca
    """)

    if st.button("Ejecutar Análisis Primal-Dual (Coca-Cola)", key="ej_dual_coca"):
        c = [0.05, 0.15, 0.12]
        A = [
            [1, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]

        b = [1500000, 0, 300000, 200000, 500000]
        signos = ["<=", ">=", ">=", ">=", "<="]

        dual = Dual(
            c, A, b, signos,
            tipo="min",
            nombres_vars=["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"]
        )

        resultado = dual.resolver()

        if resultado['primal']['exito'] and resultado['dual']['exito']:
            st.success("✅ Análisis Primal-Dual completado exitosamente")

            st.write("---")
            st.subheader("📊 Comparación Primal vs Dual")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔵 Problema PRIMAL")
                st.metric("Tipo", "Minimización")
                st.metric("Z Primal", f"${resultado['primal']['valor_optimo']:,.2f}")
                st.metric("Variables", 3)
                st.metric("Restricciones", 5)

                st.write("**Solución Óptima:**")
                primal_data = []
                for var, val in resultado['primal']['solucion'].items():
                    if var.startswith('Quito') or var.startswith('Guayaquil'):
                        primal_data.append({
                            'Variable': var,
                            'Valor': f"{val:,.0f}",
                            'Tipo': 'Básica' if val > 1e-6 else 'No Básica'
                        })
                if primal_data:
                    primal_df = pd.DataFrame(primal_data)
                    st.dataframe(primal_df, use_container_width=True, hide_index=True)

            with col2:
                st.markdown("### 🔴 Problema DUAL")
                st.metric("Tipo", "Maximización")
                st.metric("Z Dual", f"${resultado['dual']['valor_optimo']:,.2f}")
                st.metric("Variables", 5)
                st.metric("Restricciones", 3)

                st.write("**Precios Sombra (Solución Dual):**")
                dual_data = []
                for var, val in resultado['dual']['solucion'].items():
                    dual_data.append({
                        'Variable': var,
                        'Precio Sombra': f"{val:,.6f}",
                        'Tipo': 'Activa' if val > 1e-6 else 'Inactiva'
                    })
                if dual_data:
                    dual_df = pd.DataFrame(dual_data)
                    st.dataframe(dual_df, use_container_width=True, hide_index=True)

            st.write("---")
            mostrar_resolucion_dual(resultado)

        else:
            if not resultado['primal']['exito']:
                st.error("❌ Error al resolver el problema PRIMAL")
            if not resultado['dual']['exito']:
                st.error("❌ Error al resolver el problema DUAL")


def mostrar_resolucion_dual(resultado):
    """Muestra la resolución completa del análisis de dualidad"""

    st.write("---")
    st.markdown("<h2 class='section-header'>📋 Comparación Primal - Dual</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 Problema PRIMAL")
        st.write(f"""
        **Tipo:** {resultado['tipo_primal_original'].upper()}

        **Variables:** {len(resultado['nombres_vars_primal'])}
        - {', '.join(resultado['nombres_vars_primal'])}

        **Restricciones:** {len(resultado['primal']['solucion'])} (aproximado)
        """)

    with col2:
        st.subheader("🔴 Problema DUAL")
        st.write(f"""
        **Tipo:** {resultado['tipo_dual'].upper()}

        **Variables:** {len(resultado['nombres_vars_dual'])}
        - {', '.join(resultado['nombres_vars_dual'])}

        **Restricciones:** {len(resultado['dual']['solucion'])} (aproximado)
        """)

    st.write("---")

    st.markdown("<h2 class='section-header'>✅ Soluciones</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 Solución PRIMAL")
        if resultado['primal']['exito']:
            st.success(f"✓ Solución Óptima")

            valor_primal = resultado['primal']['valor_optimo']
            if valor_primal is not None:
                st.metric("Z Primal", f"${valor_primal:,.2f}")
            else:
                st.metric("Z Primal", "N/A")

            st.metric("Iteraciones", resultado['primal']['iteraciones'])

            primal_data = []
            for var, val in resultado['primal']['solucion'].items():
                primal_data.append({
                    'Variable': var,
                    'Valor': f"{val:,.0f}",
                    'Estado': 'Básica' if val > 1e-6 else 'No Básica'
                })

            if primal_data:
                primal_df = pd.DataFrame(primal_data)
                st.dataframe(primal_df, use_container_width=True, hide_index=True)
        else:
            st.error("❌ No se encontró solución primal")
            if resultado['primal'].get('es_no_acotado', False):
                st.write("Problema NO ACOTADO")
            if resultado['primal'].get('es_infactible', False):
                st.write("Problema INFACTIBLE")

    with col2:
        st.subheader("🔴 Solución DUAL")
        if resultado['dual']['exito']:
            st.success(f"✓ Solución Óptima")

            valor_dual = resultado['dual']['valor_optimo']
            if valor_dual is not None:
                st.metric("Z Dual", f"${valor_dual:,.2f}")
            else:
                st.metric("Z Dual", "N/A")

            st.metric("Iteraciones", resultado['dual']['iteraciones'])

            dual_data = []
            for var, val in resultado['dual']['solucion'].items():
                dual_data.append({
                    'Variable': var,
                    'Valor': f"{val:,.6f}",
                    'Estado': 'Básica' if val > 1e-6 else 'No Básica'
                })

            if dual_data:
                dual_df = pd.DataFrame(dual_data)
                st.dataframe(dual_df, use_container_width=True, hide_index=True)
        else:
            st.error("❌ No se encontró solución dual")
            if resultado['dual'].get('es_no_acotado', False):
                st.write("Problema NO ACOTADO")
            if resultado['dual'].get('es_infactible', False):
                st.write("Problema INFACTIBLE")

    st.write("---")

    st.markdown("<h2 class='section-header'>🔍 Verificación de Dualidad Fuerte</h2>", unsafe_allow_html=True)

    if resultado['dualidad_fuerte']:
        st.markdown("""
        <div class='success-box'>
        <h4>✓ DUALIDAD FUERTE VERIFICADA</h4>
        <p>Los valores óptimos del problema primal y dual son iguales (dentro de tolerancia numérica).</p>
        <p>Esto confirma que ambos problemas tienen soluciones óptimas equivalentes.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            valor_primal = resultado['primal']['valor_optimo']
            valor_primal_str = f"${valor_primal:,.2f}" if valor_primal is not None else "N/A"
            st.metric("Z Primal", valor_primal_str)
        with col2:
            valor_dual = resultado['dual']['valor_optimo']
            valor_dual_str = f"${valor_dual:,.2f}" if valor_dual is not None else "N/A"
            st.metric("Z Dual", valor_dual_str)
        with col3:
            diferencia = resultado['diferencia_valores_optimos']
            diferencia_str = f"{diferencia:.2e}" if diferencia is not None else "N/A"
            st.metric("Diferencia", diferencia_str)
    else:
        st.markdown("""
        <div class='warning-box'>
        <h4>⚠️ Verificación incompleta</h4>
        <p>La dualidad fuerte no se verificó completamente. Esto puede indicar:</p>
        <ul>
        <li>Uno de los problemas es infactible</li>
        <li>Uno de los problemas es no acotado</li>
        <li>Errores numéricos en la resolución</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    st.markdown("<h2 class='section-header'>📚 Información de Dualidad</h2>", unsafe_allow_html=True)

    st.write("""
    **Teorema de Dualidad Fuerte:**

    Si el problema PRIMAL tiene una solución óptima finita, entonces el problema DUAL también tiene 
    una solución óptima finita, y los valores óptimos de ambos son iguales:

    **Z_primal = Z_dual**

    **Relaciones de Complementariedad:**
    - Si una variable primal es positiva en la solución óptima, su restricción dual correspondiente 
      debe ser activa (satisfecha con igualdad)
    - Si una restricción primal es inactiva (variable de holgura > 0), la variable dual correspondiente 
      debe ser cero

    **Interpretación Económica:**
    - Las variables del dual (y_i) representan los precios sombra de los recursos
    - El valor de y_i indica cuánto cambiaría el valor óptimo si el RHS de la restricción i cambia en 1 unidad
    """)

    st.write("---")

    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Análisis Realizado:**
        - Tipo Primal: {resultado['tipo_primal_original'].upper()}
        - Tipo Dual: {resultado['tipo_dual'].upper()}
        - Variables Primal: {len(resultado['nombres_vars_primal'])}
        - Variables Dual: {len(resultado['nombres_vars_dual'])}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Primal Óptimo: {'✓ Sí' if resultado['primal']['exito'] else '✗ No'}
        - Dual Óptimo: {'✓ Sí' if resultado['dual']['exito'] else '✗ No'}
        - Dualidad Fuerte: {'✓ Verificada' if resultado['dualidad_fuerte'] else '✗ No verificada'}
        - Iteraciones Primal: {resultado['primal']['iteraciones']}
        - Iteraciones Dual: {resultado['dual']['iteraciones']}
        """)

    # ==================================================
    # 🤖 ANÁLISIS CON MÚLTIPLES IAS - AL FINAL
    # ==================================================
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Análisis Comparativo con IA</h2>", unsafe_allow_html=True)
    st.info("⏳ Generando análisis con Gemini, Hugging Face y Ollama para comparación...")

    analisis_container = st.container()
    analisis_data = {}

    with st.spinner("🤖 Generando análisis con Gemini..."):
        try:
            analisis_data['gemini'] = generar_analisis_gemini(
                origen="Dualidad",
                rutas=[{"destino": f"Var_{i}", "distancia": resultado['primal']['valor_optimo'], "ruta": f"Var_{i}"} for
                       i in range(3)],
                iteraciones=resultado['primal']['iteraciones'] + resultado['dual']['iteraciones'],
                total_nodos=len(resultado['nombres_vars_primal']) + len(resultado['nombres_vars_dual'])
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen="Dualidad",
                rutas=[{"destino": f"Var_{i}", "distancia": resultado['primal']['valor_optimo'], "ruta": f"Var_{i}"} for
                       i in range(3)],
                iteraciones=resultado['primal']['iteraciones'] + resultado['dual']['iteraciones'],
                total_nodos=len(resultado['nombres_vars_primal']) + len(resultado['nombres_vars_dual'])
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen="Dualidad",
                rutas=[{"destino": f"Var_{i}", "distancia": resultado['primal']['valor_optimo'], "ruta": f"Var_{i}"} for
                       i in range(3)],
                iteraciones=resultado['primal']['iteraciones'] + resultado['dual']['iteraciones'],
                total_nodos=len(resultado['nombres_vars_primal']) + len(resultado['nombres_vars_dual'])
            )
        except Exception as e:
            analisis_data['ollama'] = f"❌ Error: {str(e)}"

    with analisis_container:
        st.success("✅ Análisis Completados")

        tab1, tab2, tab3 = st.tabs([
            "🤖 Gemini",
            "🧠 Hugging Face",
            "💻 Ollama"
        ])

        with tab1:
            st.markdown("### 🤖 Análisis Gemini")
            st.write(analisis_data.get('gemini', 'Sin análisis disponible'))

        with tab2:
            st.markdown("### 🧠 Análisis Hugging Face")
            st.write(analisis_data.get('huggingface', 'Sin análisis disponible'))

        with tab3:
            st.markdown("### 💻 Análisis Ollama")
            st.write(analisis_data.get('ollama', 'Sin análisis disponible'))