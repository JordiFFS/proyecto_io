import streamlit as st
import pandas as pd
from models.programacion_lineal.dos_fases import DosFases


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

    # MOSTRAR CONFIGURACIÓN
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

    # FASE 1
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

    # FASE 2
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

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Valor Óptimo (Z)", f"{resultado['valor_optimo']:.6f}" if resultado['valor_optimo'] else "N/A")
    with col2:
        st.metric("📊 Total Iteraciones", resultado['iteraciones'])
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
        - Iteraciones Fase 1: {resultado['iteraciones_fase1']}
        - Iteraciones Fase 2: {resultado['iteraciones_fase2']}
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Valor Óptimo Z = {resultado['valor_optimo']:.6f} si resultado['valor_optimo'] else 'No encontrado'
        - Variables Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('x')])}
        - Estado: {resultado.get('estado', 'N/A')}
        """)