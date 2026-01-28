import streamlit as st
import pandas as pd
from models.programacion_lineal.gran_m import GranM


def mostrar_resolucion_gran_m(resultado, nombres, n_vars, n_rest, tipo_opt):
    """Muestra la resolución completa del Gran M"""

    if resultado['exito']:
        st.success("✅ Solución Óptima Encontrada")
    elif resultado['es_no_acotado']:
        st.warning("⚠️ Problema No Acotado")
    elif resultado['es_infactible']:
        st.error("❌ Problema Infactible")
    else:
        st.error("❌ Error en la resolución")

    # MOSTRAR CONFIGURACIÓN
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

    # TABLA INICIAL
    st.write("---")
    st.markdown("<h2 class='section-header'>📍 Tabla Inicial (Iteración 0)</h2>", unsafe_allow_html=True)

    if 'historial_tablas' in resultado and len(resultado['historial_tablas']) > 0:
        st.dataframe(resultado['historial_tablas'][0]['tabla'], use_container_width=True)

    # ITERACIONES
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

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Valor Óptimo (Z)", f"{resultado['valor_optimo']:.6f}")
    with col2:
        st.metric("🔄 Iteraciones", resultado['iteraciones'])
    with col3:
        st.metric("📍 Variables Básicas", len([x for x in resultado.get('base_final', []) if x.startswith('x')]))
    with col4:
        st.metric("📦 Estado", resultado.get('estado', 'N/A'))

    # VARIABLES DE DECISIÓN
    st.subheader("✅ Variables de Decisión Óptimas")
    var_data = []
    for var in nombres:
        valor = resultado['solucion_variables'].get(var, 0)
        var_data.append({
            'Variable': var,
            'Valor Óptimo': f"{valor:.6f}",
            'Tipo': 'Básica' if valor > 1e-6 else 'No Básica'
        })

    var_df = pd.DataFrame(var_data)
    st.dataframe(var_df, use_container_width=True, hide_index=True)

    # TABLA FINAL
    st.subheader("📊 Tabla Final del Gran M")
    tabla_final = pd.DataFrame(resultado['tabla_final'])
    st.dataframe(tabla_final, use_container_width=True)

    # RESUMEN
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
        - Valor Óptimo Z = {resultado['valor_optimo']:.6f}
        - Variables Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('x')])}
        - Estado: {resultado.get('estado', 'N/A')}
        """)