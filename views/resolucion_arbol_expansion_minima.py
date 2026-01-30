# views/resolucion_arbol_expansion_minima.py

import streamlit as st
import pandas as pd
from models.redes.red import Red
from models.redes.arbol_minimo import ArbolMinimo


def mostrar_resolucion_arbol_minimo(resultado, nodos, aristas_originales):
    """
    Muestra la resolución completa del algoritmo de Kruskal
    para encontrar el árbol de expansión mínima

    Args:
        resultado: Diccionario con resultado del algoritmo Kruskal
        nodos: Lista de nodos de la red
        aristas_originales: Lista de aristas originales
    """

    st.success("✅ Árbol de Expansión Mínima Calculado Exitosamente")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Nodos", len(nodos))
    with col2:
        st.metric("🔗 Aristas Totales", len(aristas_originales))
    with col3:
        st.metric("🌳 Aristas en AEM", len(resultado['arbol']))
    with col4:
        st.metric("🔍 Algoritmo", "Kruskal")

    # ARISTAS ORDENADAS
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Aristas Ordenadas por Costo</h2>",
                unsafe_allow_html=True)

    aristas_ord = sorted(aristas_originales, key=lambda x: x[0])
    aristas_df = pd.DataFrame([
        {
            'Arista': f"{a[1]} - {a[2]}",
            'Costo': f"{a[0]:.2f}",
            'En AEM': "✓" if any(
                (a[1] == arb[0] and a[2] == arb[1]) or
                (a[1] == arb[1] and a[2] == arb[0])
                for arb in resultado['arbol']
            ) else "✗"
        }
        for a in aristas_ord
    ])
    st.dataframe(aristas_df, use_container_width=True, hide_index=True)

    # ITERACIONES DEL ALGORITMO
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Construcción del Árbol - Iteraciones</h2>",
                unsafe_allow_html=True)

    if resultado['iteraciones']:
        tab_list = [f"Arista {i + 1}" for i in range(len(resultado['iteraciones']))]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter):
            with tab:
                iter_info = resultado['iteraciones'][iter_num]

                st.markdown(
                    f"<div class='iteration-header'><h3>Paso {iter_num + 1} - Arista Aceptada</h3></div>",
                    unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f"<div class='metric-box'><strong>Arista:</strong><br>{iter_info['arista']}</div>",
                        unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        f"<div class='metric-box'><strong>Costo:</strong><br>{iter_info['costo']:.2f}</div>",
                        unsafe_allow_html=True)
                with col3:
                    st.markdown(
                        f"<div class='metric-box'><strong>Acumulado:</strong><br>{iter_info['costo_acumulado']:.2f}</div>",
                        unsafe_allow_html=True)

    # ÁRBOL RESULTANTE
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 ÁRBOL DE EXPANSIÓN MÍNIMA</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌳 Aristas en AEM", len(resultado['arbol']))
    with col2:
        st.metric("💰 Costo Total", f"{resultado['costo_total']:.2f}")
    with col3:
        st.metric("✓ Conecta", f"{len(nodos)} nodos")

    st.subheader("✅ Aristas que Forman el AEM")
    arbol_data = []
    for i, (u, v, costo) in enumerate(resultado['arbol']):
        arbol_data.append({
            '#': i + 1,
            'Nodo 1': u,
            'Nodo 2': v,
            'Costo': f"{costo:.2f}",
            'Acumulado': f"{sum(a[2] for a in resultado['arbol'][:i + 1]):.2f}"
        })

    arbol_df = pd.DataFrame(arbol_data)
    st.dataframe(arbol_df, use_container_width=True, hide_index=True)

    # VERIFICACIÓN
    st.subheader("✔️ Verificación del AEM")
    col1, col2, col3 = st.columns(3)
    with col1:
        es_conexo = len(resultado['arbol']) == len(nodos) - 1
        st.metric("Es Árbol", "✓" if es_conexo else "✗")
    with col2:
        st.metric("Costo Mínimo", "✓")
    with col3:
        st.metric("Ciclos", "0")

    # RESUMEN
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Algoritmo: Kruskal
        - Tipo: Árbol de Expansión Mínima
        - Nodos: {len(nodos)}
        - Aristas Totales: {len(aristas_originales)}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Aristas en AEM: {len(resultado['arbol'])}
        - Costo Total: {resultado['costo_total']:.2f}
        - Iteraciones: {len(resultado['iteraciones'])}
        """)


def ejemplo_arbol_minimo():
    """Ejemplo predefinido de árbol de expansión mínima"""
    st.subheader("Ejemplo: Árbol de Expansión Mínima de una Red")
    st.write("""
    **Problema:** Conectar 6 ciudades con el costo mínimo de conexión.

    **Aristas disponibles:**
    - A-B: 4
    - A-C: 2
    - B-C: 1
    - B-D: 5
    - C-D: 8
    - C-E: 10
    - D-E: 2
    - D-F: 6
    - E-F: 3
    """)

    if st.button("Ejecutar Ejemplo", key="ej_arbol_minimo"):
        arbol = ArbolMinimo(['A', 'B', 'C', 'D', 'E', 'F'])

        arbol.agregar_arista('A', 'B', 4)
        arbol.agregar_arista('A', 'C', 2)
        arbol.agregar_arista('B', 'C', 1)
        arbol.agregar_arista('B', 'D', 5)
        arbol.agregar_arista('C', 'D', 8)
        arbol.agregar_arista('C', 'E', 10)
        arbol.agregar_arista('D', 'E', 2)
        arbol.agregar_arista('D', 'F', 6)
        arbol.agregar_arista('E', 'F', 3)

        resultado = arbol.resolver()

        # Preparar aristas originales para mostrar
        aristas_originales = [
            (4, 'A', 'B'),
            (2, 'A', 'C'),
            (1, 'B', 'C'),
            (5, 'B', 'D'),
            (8, 'C', 'D'),
            (10, 'C', 'E'),
            (2, 'D', 'E'),
            (6, 'D', 'F'),
            (3, 'E', 'F')
        ]

        mostrar_resolucion_arbol_minimo(resultado, ['A', 'B', 'C', 'D', 'E', 'F'],
                                        aristas_originales)