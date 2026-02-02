# views/resolucion_dos_fases.py
import streamlit as st
import pandas as pd
from models.programacion_lineal.dos_fases import DosFases
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible


def ejemplo_dos_fases_coca_cola():
    """Ejemplo real de Coca-Cola - Minimización de Costos de Distribución"""
    st.subheader("📊 Ejemplo: Minimización de Costos - Coca-Cola")

    st.write("""
    **Problema:** Minimizar costos de distribución desde plantas a centros

    **Variables:**
    - x₁ = Botellas desde Planta Quito a Centro Quito
    - x₂ = Botellas desde Planta Quito a Centro Guayaquil
    - x₃ = Botellas desde Planta Guayaquil a Centro Cuenca

    **Función Objetivo:**
    Minimizar: 0.05x₁ + 0.15x₂ + 0.12x₃

    **Restricciones:**
    - x₁ + x₂ ≤ 1,500,000 (Capacidad Planta Quito)
    - x₃ ≥ 0 (No negatividad)
    - x₁ ≥ 300,000 (Demanda mínima Centro Quito)
    - x₂ ≥ 200,000 (Demanda mínima Centro Guayaquil)
    - x₃ ≤ 500,000 (Capacidad máxima Centro Cuenca)

    """)

    if st.button("Ejecutar Ejemplo Dos Fases (Coca-Cola)", key="ej_dos_fases_coca"):
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

        dos_fases = DosFases(
            c, A, b, signos,
            tipo="min",
            nombres_vars=["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"]
        )

        resultado = dos_fases.resolver(verbose=False)

        if resultado['exito']:
            st.success("✅ Solución óptima encontrada")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quito→Quito",
                          f"{resultado['solucion_variables']['Quito→Quito']:,.0f} botellas")
            with col2:
                st.metric("Quito→Guayaquil",
                          f"{resultado['solucion_variables']['Quito→Guayaquil']:,.0f} botellas")
            with col3:
                st.metric("Guayaquil→Cuenca",
                          f"{resultado['solucion_variables']['Guayaquil→Cuenca']:,.0f} botellas")

            st.metric("💰 Costo Total Mínimo",
                      f"${resultado['valor_optimo']:,.2f}")

            st.write("---")
            st.dataframe(dos_fases.obtener_tabla_fase2_pandas(), use_container_width=True)

            st.write("---")
            mostrar_resolucion_dos_fases(
                resultado,
                ["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"],
                3, 5, "Minimización"
            )
        elif resultado['es_infactible']:
            st.error("❌ Problema Infactible")
        elif resultado['es_no_acotado']:
            st.warning("⚠️ Problema No Acotado")
        else:
            st.error("❌ Error en la resolución")


def mostrar_resolucion_dos_fases(resultado, nombres, n_vars, n_rest, tipo_opt):
    """Muestra la resolución completa del método Dos Fases"""

    if resultado['exito']:
        st.success("✅ Solución Óptima Encontrada")
    elif resultado['es_no_acotado']:
        st.warning("⚠️ Problema No Acotado")
    elif resultado['es_infactible']:
        st.error("❌ Problema Infactible")
    else:
        st.error("❌ Error en la resolución")

    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Variables de Decisión", n_vars)
    with col2:
        st.metric("📏 Restricciones", n_rest)
    with col3:
        st.metric("🔄 Iteraciones Fase 1", resultado['iteraciones_fase1'])
    with col4:
        st.metric("🔄 Iteraciones Fase 2", resultado['iteraciones_fase2'])

    st.write("---")
    st.markdown("<h2 class='section-header'>📍 FASE 1: Encontrar Solución Básica Factible</h2>", unsafe_allow_html=True)

    st.info("En la Fase 1, se minimiza la suma de variables artificiales para encontrar una solución básica factible.")

    if 'historial_tablas_fase1' in resultado and len(resultado['historial_tablas_fase1']) > 0:
        st.subheader("📊 Tabla Inicial Fase 1 (Iteración 0)")
        st.dataframe(resultado['historial_tablas_fase1'][0]['tabla'], use_container_width=True)

        if len(resultado['historial_tablas_fase1']) > 1:
            st.subheader("🔄 Iteraciones Fase 1")

            tab_list = [f"Iter. {i + 1}" for i in range(resultado['iteraciones_fase1'])]
            if len(tab_list) > 0:
                tabs_iter = st.tabs(tab_list)

                for iter_num, tab in enumerate(tabs_iter, 1):
                    with tab:
                        if iter_num < len(resultado['historial_tablas_fase1']):
                            iter_info = resultado['historial_tablas_fase1'][iter_num]

                            st.markdown(f"<div class='iteration-header'><h4>Iteración {iter_num} - Fase 1</h4></div>",
                                        unsafe_allow_html=True)

                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(
                                    f"<div class='metric-box'><strong>Variable Entra:</strong><br>{iter_info.get('variable_entra', 'N/A')}</div>",
                                    unsafe_allow_html=True)
                            with col2:
                                st.markdown(
                                    f"<div class='metric-box'><strong>Variable Sale:</strong><br>{iter_info.get('variable_sale', 'N/A')}</div>",
                                    unsafe_allow_html=True)

                            st.write("")
                            st.subheader("📊 Tabla Actualizada")
                            st.dataframe(iter_info['tabla'], use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>📈 FASE 2: Optimizar Función Objetivo Original</h2>", unsafe_allow_html=True)

    st.info("En la Fase 2, se optimiza la función objetivo original sin variables artificiales.")

    if 'historial_tablas_fase2' in resultado and len(resultado['historial_tablas_fase2']) > 0:
        st.subheader("📊 Tabla Inicial Fase 2 (Iteración 0)")
        st.dataframe(resultado['historial_tablas_fase2'][0]['tabla'], use_container_width=True)

        if len(resultado['historial_tablas_fase2']) > 1:
            st.subheader("🔄 Iteraciones Fase 2")

            tab_list = [f"Iter. {i + 1}" for i in range(resultado['iteraciones_fase2'])]
            if len(tab_list) > 0:
                tabs_iter = st.tabs(tab_list)

                for iter_num, tab in enumerate(tabs_iter, 1):
                    with tab:
                        if iter_num < len(resultado['historial_tablas_fase2']):
                            iter_info = resultado['historial_tablas_fase2'][iter_num]

                            st.markdown(f"<div class='iteration-header'><h4>Iteración {iter_num} - Fase 2</h4></div>",
                                        unsafe_allow_html=True)

                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(
                                    f"<div class='metric-box'><strong>Variable Entra:</strong><br>{iter_info.get('variable_entra', 'N/A')}</div>",
                                    unsafe_allow_html=True)
                            with col2:
                                st.markdown(
                                    f"<div class='metric-box'><strong>Variable Sale:</strong><br>{iter_info.get('variable_sale', 'N/A')}</div>",
                                    unsafe_allow_html=True)

                            st.write("")
                            st.subheader("📊 Tabla Actualizada")
                            st.dataframe(iter_info['tabla'], use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        valor_display = f"${resultado['valor_optimo']:,.2f}" if resultado['valor_optimo'] is not None else "N/A"
        st.metric("🎯 Valor Óptimo (Z)", valor_display)
    with col2:
        st.metric("📊 Total Iteraciones", resultado['iteraciones'])
    with col3:
        st.metric("📍 Variables Básicas", len([x for x in resultado.get('base_final', []) if x.startswith('x')]))
    with col4:
        st.metric("📦 Estado", resultado.get('estado', 'N/A'))

    st.subheader("✅ Variables de Decisión Óptimas")
    var_data = []
    for var in nombres:
        valor = resultado['solucion_variables'].get(var, 0)
        var_data.append({
            'Variable': var,
            'Valor Óptimo': f"{valor:,.0f}",
            'Tipo': 'Básica (Activa)' if valor > 1e-6 else 'No Básica (Inactiva)'
        })

    var_df = pd.DataFrame(var_data)
    st.dataframe(var_df, use_container_width=True, hide_index=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema Resuelto:**
        - Tipo: {tipo_opt}
        - Variables: {n_vars}
        - Restricciones: {n_rest}
        - Iteraciones Fase 1: {resultado['iteraciones_fase1']}
        - Iteraciones Fase 2: {resultado['iteraciones_fase2']}
        """)

    with summary_col2:
        valor_display = f"${resultado['valor_optimo']:,.2f}" if resultado[
                                                                    'valor_optimo'] is not None else "No encontrado"
        st.write(f"""
        **Solución:**
        - Valor Óptimo Z = {valor_display}
        - Variables Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('x')])}
        - Estado: {resultado.get('estado', 'N/A')}
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
                origen=f"Dos Fases {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(len(nombres))],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen=f"Dos Fases {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(len(nombres))],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen=f"Dos Fases {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(len(nombres))],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
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