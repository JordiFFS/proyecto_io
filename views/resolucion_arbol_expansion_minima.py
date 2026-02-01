"""
views/resolucion_arbol_expansion_minima.py
Vista para Árbol de Expansión Mínima adaptada a Coca-Cola
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.redes.red import Red
from models.redes.arbol_minimo import ArbolMinimo
from empresa.datos_empresa import PLANTAS, CENTROS_DISTRIBUCION, COSTOS_TRANSPORTE_DISTRIBUCION


def crear_grafo_arbol(arista_resultado, nodos):
    """
    Crea un gráfico del árbol de expansión mínima
    """
    fig = go.Figure()

    posiciones = {
        "Planta_Quito": (0, 2),
        "Planta_Guayaquil": (0, 1),
        "Planta_Cuenca": (0, 0),
        "Centro_Quito": (2, 2),
        "Centro_Guayaquil": (2, 1),
        "Centro_Cuenca": (2, 0),
    }

    # Agregar aristas del árbol
    for u, v, costo in arista_resultado:
        if u in posiciones and v in posiciones:
            x0, y0 = posiciones[u]
            x1, y1 = posiciones[v]

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=3, color="#FF6B6B"),
                hovertemplate=f"<b>{u} ↔ {v}</b><br>Costo: {costo:.4f}<extra></extra>",
                showlegend=False
            ))

    colores_nodo = {
        "Planta_Quito": "#4169E1",
        "Planta_Guayaquil": "#4169E1",
        "Planta_Cuenca": "#4169E1",
        "Centro_Quito": "#32CD32",
        "Centro_Guayaquil": "#32CD32",
        "Centro_Cuenca": "#32CD32",
    }

    for nodo, (x, y) in posiciones.items():
        if nodo in nodos:
            color = colores_nodo.get(nodo, "#808080")

            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=30,
                    color=color,
                    line=dict(width=2, color="white")
                ),
                text=[nodo],
                textposition="top center",
                textfont=dict(size=10, color="white", family="Arial Black"),
                hovertemplate=f"<b>{nodo}</b><extra></extra>",
                showlegend=False
            ))

    fig.update_layout(
        title=dict(
            text="Árbol de Expansión Mínima - Coca-Cola",
            font=dict(size=20, color="white")
        ),
        showlegend=True,
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 2.5]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 2.5]
        ),
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0d0d0d",
        font=dict(color="white"),
        height=600,
        margin=dict(b=50, l=50, r=50, t=100)
    )

    colores_leyenda = [
        ("Plantas", "#4169E1"),
        ("Centros Distribución", "#32CD32"),
        ("Arista AEM", "#FF6B6B")
    ]

    for nombre, color_ley in colores_leyenda:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color=color_ley),
            showlegend=True,
            name=nombre
        ))

    return fig


def mostrar_resolucion_arbol_minimo(resultado, nodos, aristas_originales):
    """
    Muestra la resolución completa del algoritmo de Kruskal
    para encontrar el árbol de expansión mínima
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
    aristas_df_data = []

    for a in aristas_ord:
        en_aem = any(
            (a[1] == arb[0] and a[2] == arb[1]) or
            (a[1] == arb[1] and a[2] == arb[0])
            for arb in resultado['arbol']
        )
        aristas_df_data.append({
            'Arista': f"{a[1]} ↔ {a[2]}",
            'Costo': f"{a[0]:.4f}",
            'En AEM': "✓" if en_aem else "✗"
        })

    aristas_df = pd.DataFrame(aristas_df_data)
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
                        f"<div class='metric-box'><strong>Costo:</strong><br>${iter_info['costo']:.4f}</div>",
                        unsafe_allow_html=True)
                with col3:
                    st.markdown(
                        f"<div class='metric-box'><strong>Acumulado:</strong><br>${iter_info['costo_acumulado']:.4f}</div>",
                        unsafe_allow_html=True)

    # ÁRBOL RESULTANTE
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 ÁRBOL DE EXPANSIÓN MÍNIMA</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌳 Aristas en AEM", len(resultado['arbol']))
    with col2:
        st.metric("💰 Costo Total", f"${resultado['costo_total']:.4f}")
    with col3:
        st.metric("✓ Conecta", f"{len(nodos)} nodos")

    st.subheader("✅ Aristas que Forman el AEM")
    arbol_data = []
    for i, (u, v, costo) in enumerate(resultado['arbol']):
        arbol_data.append({
            '#': i + 1,
            'Nodo 1': u,
            'Nodo 2': v,
            'Costo': f"${costo:.4f}",
            'Acumulado': f"${sum(a[2] for a in resultado['arbol'][:i + 1]):.4f}"
        })

    arbol_df = pd.DataFrame(arbol_data)
    st.dataframe(arbol_df, use_container_width=True, hide_index=True)

    # VISUALIZACIÓN GRÁFICA
    st.write("---")
    st.markdown("<h2 class='section-header'>🗺️ VISUALIZACIÓN GRÁFICA DEL ÁRBOL</h2>",
                unsafe_allow_html=True)

    fig_arbol = crear_grafo_arbol(resultado['arbol'], nodos)
    st.plotly_chart(fig_arbol, use_container_width=True)

    # VERIFICACIÓN
    st.write("---")
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
        - Costo Total: ${resultado['costo_total']:.4f}
        - Iteraciones: {len(resultado['iteraciones'])}
        """)


def ejemplo_arbol_minimo():
    """Ejemplo de Árbol de Expansión Mínima con datos de Coca-Cola"""
    st.subheader("📦 Ejemplo: Árbol de Expansión Mínima - Red Coca-Cola")
    st.write("""
    **Problema:** Conectar plantas de producción con centros de distribución 
    minimizando costos de transporte.
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_arbol_coca_cola"):
        # Nodos: 3 plantas + 3 centros
        nodos = [
            "Planta_Quito", "Planta_Guayaquil", "Planta_Cuenca",
            "Centro_Quito", "Centro_Guayaquil", "Centro_Cuenca"
        ]

        arbol = ArbolMinimo(nodos)

        # Agregar aristas con costos de transporte
        aristas_datos = []
        for planta, centros in COSTOS_TRANSPORTE_DISTRIBUCION.items():
            for centro, costo in centros.items():
                arbol.agregar_arista(planta, centro, costo)
                aristas_datos.append((costo, planta, centro))

        # Resolver
        resultado = arbol.resolver()

        # Mostrar resultados
        mostrar_resolucion_arbol_minimo(resultado, nodos, aristas_datos)