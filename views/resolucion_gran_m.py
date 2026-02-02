# views/resolucion_gran_m.py
import streamlit as st
import pandas as pd
from models.programacion_lineal.gran_m import GranM
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible


def mostrar_resolucion_gran_m(resultado, nombres, n_vars, n_rest, tipo_opt):
    """Muestra la resolución completa del Gran M con debug"""

    if 'debug_log' in resultado and resultado['debug_log']:
        with st.expander("🔍 Ver LOG DE DEBUG (Detalle completo de la resolución)", expanded=False):
            debug_text = "\n".join(resultado['debug_log'])
            st.code(debug_text, language="text")

    if resultado['es_infactible']:
        st.error("❌ Problema Infactible - No se pudo encontrar una solución factible.")
        return

    if resultado['es_no_acotado']:
        st.warning("⚠️ Problema No Acotado - La solución puede crecer indefinidamente.")
        return

    if resultado['exito']:
        st.success("✅ Solución Óptima Encontrada")
    else:
        st.error("❌ Error en la resolución del problema")
        return

    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Variables de Decisión", n_vars)
    with col2:
        st.metric("📏 Restricciones", n_rest)
    with col3:
        st.metric("📝 Variables Artificiales", str(resultado['solucion']).count('a'))
    with col4:
        st.metric("🔄 Iteraciones", resultado['iteraciones'])

    st.write("---")
    st.markdown("<h2 class='section-header'>📍 Tabla Inicial (Iteración 0)</h2>", unsafe_allow_html=True)

    st.info("""
    La tabla inicial del Gran M incluye:
    - Variables de decisión originales
    - Variables de holgura (para restricciones ≤)
    - Variables de exceso (para restricciones ≥)
    - Variables artificiales (penalizadas con -M)
    """)

    if 'historial_tablas' in resultado and len(resultado['historial_tablas']) > 0:
        st.dataframe(resultado['historial_tablas'][0]['tabla'], use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Método Gran M</h2>", unsafe_allow_html=True)

    if resultado['iteraciones'] > 0 and 'historial_tablas' in resultado:
        tab_list = [f"Iter. {i + 1}" for i in range(resultado['iteraciones'])]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter, 1):
            with tab:
                if iter_num <= len(resultado['historial_tablas']) - 1:
                    iter_info = resultado['historial_tablas'][iter_num]

                    st.markdown(f"<div class='iteration-header'><h3>Iteración {iter_num}</h3></div>",
                                unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(
                            f"<div class='metric-box'><strong>Variable Entra:</strong><br>{iter_info.get('variable_entra', 'N/A')}</div>",
                            unsafe_allow_html=True)
                    with col2:
                        st.markdown(
                            f"<div class='metric-box'><strong>Variable Sale:</strong><br>{iter_info.get('variable_sale', 'N/A')}</div>",
                            unsafe_allow_html=True)
                    with col3:
                        st.markdown(
                            f"<div class='metric-box'><strong>Pivote:</strong><br>{iter_info.get('elemento_pivote', 'N/A'):.6f}</div>",
                            unsafe_allow_html=True)

                    st.write("")
                    st.subheader("📊 Tabla de la Iteración")
                    st.dataframe(iter_info['tabla'], use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Valor Óptimo (Z)", f"${resultado['valor_optimo']:.2f}")
    with col2:
        st.metric("🔄 Iteraciones", resultado['iteraciones'])
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

    st.subheader("📊 Tabla Final del Gran M")
    tabla_final = pd.DataFrame(resultado['tabla_final'])
    st.dataframe(tabla_final, use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema Resuelto:**
        - Tipo: {tipo_opt}
        - Variables: {n_vars}
        - Restricciones: {n_rest}
        - Iteraciones: {resultado['iteraciones']}
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Valor Óptimo Z = ${resultado['valor_optimo']:.2f}
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
                origen=f"Gran M {tipo_opt}",
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
                origen=f"Gran M {tipo_opt}",
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
                origen=f"Gran M {tipo_opt}",
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


def ejemplo_gran_m_coca_cola():
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
    - x₃ ≥ 400,000 (Demanda mínima Centro Cuenca)
    - x₁ ≥ 300,000 (Demanda mínima Centro Quito)
    - x₂ ≥ 200,000 (Demanda mínima Centro Guayaquil)
    - x₃ ≤ 500,000 (Capacidad máxima Centro Cuenca)
    """)

    if st.button("Ejecutar Ejemplo Gran M", key="ej_granm_coca"):
        c = [0.05, 0.15, 0.12]
        A = [
            [1, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]

        b = [1500000, 400000, 300000, 200000, 500000]
        signos = ["<=", ">=", ">=", ">=", "<="]

        gran_m = GranM(
            c, A, b, signos,
            tipo="min",
            nombres_vars=["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"]
        )

        resultado = gran_m.resolver(verbose=False)

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
            st.dataframe(gran_m.obtener_tabla_pandas(), use_container_width=True)

            st.write("---")
            mostrar_resolucion_gran_m(
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