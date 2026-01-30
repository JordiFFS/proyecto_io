# views/resolucion_costo_minimo.py

import streamlit as st
import pandas as pd
from models.redes.red import Red
from models.redes.flujo_costo_minimo import FlujoCostoMinimo


def mostrar_resolucion_flujo_costo_minimo(resultado, origen, destino, flujo_requerido):
    """
    Muestra la resolución completa del algoritmo de flujo de costo mínimo
    usando rutas de menor costo sucesivas

    Args:
        resultado: Diccionario con resultado del flujo de costo mínimo
        origen: Nodo origen
        destino: Nodo destino
        flujo_requerido: Cantidad de flujo a transportar
    """

    st.success("✅ Flujo de Costo Mínimo Calculado Exitosamente")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Nodo Origen", origen)
    with col2:
        st.metric("🔴 Nodo Destino", destino)
    with col3:
        st.metric("🌊 Flujo Requerido", f"{flujo_requerido:.2f}")
    with col4:
        st.metric("🔍 Algoritmo", "Dijkstra Sucesivo")

    # INFORMACIÓN GENERAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 RESULTADO FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Costo Total", f"{resultado['costo_total']:.2f}")
    with col2:
        st.metric("🔄 Iteraciones", len(resultado['iteraciones']))
    with col3:
        st.metric("📊 Flujo Entregado", f"{flujo_requerido:.2f}")

    # ITERACIONES - RUTAS SUCESIVAS
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones - Rutas de Menor Costo Sucesivas</h2>",
                unsafe_allow_html=True)

    if resultado['iteraciones']:
        tab_list = [f"Ruta {i + 1}" for i in range(len(resultado['iteraciones']))]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter):
            with tab:
                iter_info = resultado['iteraciones'][iter_num]

                st.markdown(
                    f"<div class='iteration-header'><h3>Iteración {iter_num + 1} - Ruta de Menor Costo</h3></div>",
                    unsafe_allow_html=True)

                # Información de la ruta
                col1, col2, col3, col4 = st.columns(4)

                ruta_str = " → ".join(iter_info['ruta'])
                with col1:
                    st.markdown(
                        f"<div class='metric-box'><strong>Ruta:</strong><br>{ruta_str}</div>",
                        unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        f"<div class='metric-box'><strong>Costo/Unidad:</strong><br>${iter_info['costo_ruta']:.2f}</div>",
                        unsafe_allow_html=True)
                with col3:
                    st.markdown(
                        f"<div class='metric-box'><strong>Flujo Enviado:</strong><br>{iter_info['flujo_enviado']:.2f}</div>",
                        unsafe_allow_html=True)
                with col4:
                    st.markdown(
                        f"<div class='metric-box'><strong>Costo Ruta:</strong><br>${iter_info['flujo_enviado'] * iter_info['costo_ruta']:.2f}</div>",
                        unsafe_allow_html=True)

                # Información del flujo
                col_flujo1, col_flujo2 = st.columns(2)
                with col_flujo1:
                    st.write(f"**Flujo Acumulado:** {flujo_requerido - iter_info['flujo_restante']:.2f}")
                with col_flujo2:
                    st.write(f"**Flujo Restante:** {iter_info['flujo_restante']:.2f}")

    else:
        st.info("No se requirieron iteraciones (flujo inicial = 0).")

    # RESUMEN DE RUTAS
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen de Rutas y Costos</h2>", unsafe_allow_html=True)

    summary_data = []
    costo_acumulado = 0

    for i, iter_info in enumerate(resultado['iteraciones'], 1):
        costo_ruta = iter_info['flujo_enviado'] * iter_info['costo_ruta']
        costo_acumulado += costo_ruta

        summary_data.append({
            'Iteración': i,
            'Ruta': " → ".join(iter_info['ruta']),
            'Costo/Unidad': f"${iter_info['costo_ruta']:.2f}",
            'Flujo': f"{iter_info['flujo_enviado']:.2f}",
            'Costo Ruta': f"${costo_ruta:.2f}",
            'Acumulado': f"${costo_acumulado:.2f}"
        })

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # ANÁLISIS DE COSTOS
    st.subheader("💹 Análisis de Costos")

    col_costo1, col_costo2, col_costo3 = st.columns(3)

    with col_costo1:
        st.metric("Costo Total", f"${resultado['costo_total']:.2f}")

    with col_costo2:
        if len(resultado['iteraciones']) > 0:
            costo_promedio = resultado['costo_total'] / flujo_requerido
            st.metric("Costo Promedio/Unidad", f"${costo_promedio:.2f}")
        else:
            st.metric("Costo Promedio/Unidad", "$0.00")

    with col_costo3:
        st.metric("Rutas Utilizadas", len(resultado['iteraciones']))

    # DESGLOSE POR RUTA
    st.subheader("🔗 Desglose por Ruta")

    desglose_data = []
    for i, iter_info in enumerate(resultado['iteraciones'], 1):
        desglose_data.append({
            'Ruta #': i,
            'Camino': " → ".join(iter_info['ruta']),
            'Unidades': f"{iter_info['flujo_enviado']:.2f}",
            'Costo Unitario': f"${iter_info['costo_ruta']:.2f}",
            'Costo Total': f"${iter_info['flujo_enviado'] * iter_info['costo_ruta']:.2f}",
            'Porcentaje': f"{(iter_info['flujo_enviado'] / flujo_requerido) * 100:.1f}%"
        })

    desglose_df = pd.DataFrame(desglose_data)
    st.dataframe(desglose_df, use_container_width=True, hide_index=True)

    # VERIFICACIÓN
    st.subheader("✔️ Verificación")

    col_verif1, col_verif2, col_verif3 = st.columns(3)

    flujo_total_enviado = sum(iter['flujo_enviado'] for iter in resultado['iteraciones'])

    with col_verif1:
        st.metric("Flujo Requerido", f"{flujo_requerido:.2f}")

    with col_verif2:
        st.metric("Flujo Enviado", f"{flujo_total_enviado:.2f}")

    with col_verif3:
        coincide = abs(flujo_requerido - flujo_total_enviado) < 0.01
        st.metric("Coincide", "✓" if coincide else "✗")

    # PROPIEDADES
    st.subheader("⚙️ Propiedades del Algoritmo")
    st.write("""
    - **Algoritmo**: Rutas de Menor Costo Sucesivas (Dijkstra Iterativo)
    - **Método**: Encuentra iterativamente la ruta de menor costo
    - **Característica**: Óptima para flujos divisibles
    - **Propiedad**: Minimiza el costo total de transporte
    """)

    # RESUMEN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Algoritmo: Rutas de Menor Costo Sucesivas
        - Tipo: Flujo de Costo Mínimo
        - Origen: {origen}
        - Destino: {destino}
        - Flujo Requerido: {flujo_requerido:.2f}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Costo Total: ${resultado['costo_total']:.2f}
        - Rutas Utilizadas: {len(resultado['iteraciones'])}
        - Costo Promedio: ${resultado['costo_total'] / flujo_requerido:.2f}/unidad
        - Eficiencia: ✓ Óptima
        """)


def ejemplo_flujo_costo_minimo():
    """Ejemplo predefinido de flujo de costo mínimo"""
    st.subheader("Ejemplo: Transporte de Mercancía con Costo Mínimo")
    st.write("""
    **Problema:** Enviar 25 unidades de mercancía desde A hacia E
    minimizando el costo total de transporte.

    **Red de transporte:**
    - A → B: capacidad 15, costo $2/unidad
    - A → C: capacidad 20, costo $3/unidad
    - B → D: capacidad 10, costo $1/unidad
    - B → E: capacidad 15, costo $4/unidad
    - C → D: capacidad 20, costo $2/unidad
    - D → E: capacidad 25, costo $1/unidad
    """)

    if st.button("Ejecutar Ejemplo", key="ej_flujo_costo"):
        flujo_costo = FlujoCostoMinimo(['A', 'B', 'C', 'D', 'E'])

        flujo_costo.agregar_arco('A', 'B', 15, 2)
        flujo_costo.agregar_arco('A', 'C', 20, 3)
        flujo_costo.agregar_arco('B', 'D', 10, 1)
        flujo_costo.agregar_arco('B', 'E', 15, 4)
        flujo_costo.agregar_arco('C', 'D', 20, 2)
        flujo_costo.agregar_arco('D', 'E', 25, 1)

        resultado = flujo_costo.resolver('A', 'E', 25)

        mostrar_resolucion_flujo_costo_minimo(resultado, 'A', 'E', 25)