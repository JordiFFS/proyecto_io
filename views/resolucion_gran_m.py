import streamlit as st
import pandas as pd
from models.programacion_lineal.gran_m import GranM


def mostrar_resolucion_gran_m(resultado, nombres, n_vars, n_rest, tipo_opt):
    """Muestra la resolución completa del Gran M con diagnóstico extendido."""

    if resultado['es_infactible']:
        st.error("❌ Problema Infactible - Violación en restricciones:")
        if 'violaciones' in resultado:
            for violacion in resultado['violaciones']:
                st.markdown(f"- {violacion}")
        return

    if resultado['es_no_acotado']:
        st.warning("⚠️ Problema No Acotado - La solución puede crecer indefinidamente.")
        return

    if resultado['exito']:
        st.success("✅ Solución Óptima Encontrada")
    else:
        st.error("❌ Error en la resolución del problema")
        return

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

    st.info("""
    La tabla inicial del Gran M incluye:
    - Variables de decisión originales
    - Variables de holgura (para restricciones ≤)
    - Variables de exceso (para restricciones ≥)
    - Variables artificiales (penalizadas con -M)
    """)

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
        st.metric("🎯 Valor Óptimo (Z)", f"${resultado['valor_optimo']:.2f}")
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
            'Valor Óptimo': f"{valor:,.0f}",
            'Tipo': 'Básica (Activa)' if valor > 1e-6 else 'No Básica (Inactiva)'
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
        - Valor Óptimo Z = ${resultado['valor_optimo']:.2f}
        - Variables Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('x')])}
        - Estado: {resultado.get('estado', 'N/A')}
        """)

def ejemplo_gran_m_coca_cola():
    """Ejemplo real de Coca-Cola - Minimización de Costos de Distribución"""
    st.subheader("📊 Ejemplo: Minimización de Costos - Coca-Cola")

    st.write("""
    **Problema:** Minimizar costos de distribución desde plantas a centros de distribución

    **Variables:**
    - x₁ = Botellas desde Planta Quito a Centro Quito
    - x₂ = Botellas desde Planta Quito a Centro Guayaquil
    - x₃ = Botellas desde Planta Guayaquil a Centro Cuenca

    **Función Objetivo:**
    Minimizar: 0.05x₁ + 0.15x₂ + 0.12x₃ (costos en USD por botella)

    **Restricciones:**
    - Capacidad Planta Quito: x₁ + x₂ ≤ 1,500,000
    - Capacidad Planta Guayaquil: x₃ ≥ 400,000 (demanda mínima)
    - Demanda Centro Quito: x₁ ≥ 300,000 (demanda mínima)
    - Demanda Centro Guayaquil: x₂ ≥ 200,000 (demanda mínima)
    - Demanda Centro Cuenca: x₃ ≤ 500,000 (capacidad máxima)
    """)

    if st.button("Ejecutar Ejemplo Gran M", key="ej_granm_coca"):
        c = [0.05, 0.15, 0.12]
        A = [
            [1, 1, 0],  # Capacidad Planta Quito: ≤ 1,500,000
            [0, 0, 1],  # Capacidad Planta Guayaquil: ≥ 400,000
            [1, 0, 0],  # Demanda Centro Quito: ≥ 300,000
            [0, 1, 0],  # Demanda Centro Guayaquil: ≥ 200,000
            [0, 0, 1],  # Demanda Centro Cuenca: ≤ 500,000
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
            st.error("❌ Problema Infactible - No existe solución que satisfaga todas las restricciones")
        elif resultado['es_no_acotado']:
            st.warning("⚠️ Problema No Acotado - La solución puede mejorar indefinidamente")
        else:
            st.error("❌ Error en la resolución")