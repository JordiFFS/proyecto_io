"""
views/resolucion_vogel.py
Vista para Método de Vogel adaptada a Coca-Cola
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from models.transporte.vogel import MetodoVogel
from empresa.datos_empresa import (
    PLANTAS, CENTROS_DISTRIBUCION, COSTOS_TRANSPORTE_DISTRIBUCION,
    PUNTOS_VENTA, COSTOS_TRANSPORTE_VENTA
)


def crear_grafo_transporte_vogel(orígenes, destinos, asignacion, costos, nombres_origenes, nombres_destinos):
    """
    Crea un gráfico interactivo del transporte para Vogel
    """
    fig = go.Figure()

    # Posiciones para plantas y centros
    posiciones_plantas = {
        "Planta_Quito": (0, 2),
        "Planta_Guayaquil": (0, 1),
        "Planta_Cuenca": (0, 0),
    }

    posiciones_centros = {
        "Centro_Quito": (2, 2),
        "Centro_Guayaquil": (2, 1),
        "Centro_Cuenca": (2, 0),
    }

    posiciones_puntos = {
        "SupermercadoA": (4, 2.3),
        "SupermercadoB": (4, 0.7),
        "TiendaDistribuidor1": (4, 2),
        "TiendaDistribuidor2": (4, 1),
        "TiendaMinorista1": (4, -0.3),
        "TiendaMinorista2": (4, 2.5),
    }

    posiciones = {**posiciones_plantas, **posiciones_centros, **posiciones_puntos}

    # Agregar arcos con asignaciones
    for i, origen in enumerate(orígenes):
        for j, destino in enumerate(destinos):
            if asignacion[i][j] > 0:
                if origen in posiciones and destino in posiciones:
                    x0, y0 = posiciones[origen]
                    x1, y1 = posiciones[destino]

                    cantidad = int(asignacion[i][j])
                    costo = float(costos[i][j])
                    costo_total = cantidad * costo

                    fig.add_trace(go.Scatter(
                        x=[x0, x1],
                        y=[y0, y1],
                        mode="lines",
                        line=dict(width=3, color="#FFD700"),
                        hovertemplate=f"<b>{origen} → {destino}</b><br>Cantidad: {cantidad}<br>Costo: ${costo_total:.2f}<extra></extra>",
                        showlegend=False
                    ))

    # Colores para nodos
    colores_nodo = {
        "Planta_Quito": "#4169E1",
        "Planta_Guayaquil": "#4169E1",
        "Planta_Cuenca": "#4169E1",
        "Centro_Quito": "#32CD32",
        "Centro_Guayaquil": "#32CD32",
        "Centro_Cuenca": "#32CD32",
        "SupermercadoA": "#FFB84D",
        "SupermercadoB": "#FFB84D",
        "TiendaDistribuidor1": "#FFB84D",
        "TiendaDistribuidor2": "#FFB84D",
        "TiendaMinorista1": "#FFB84D",
        "TiendaMinorista2": "#FFB84D",
    }

    # Agregar nodos
    for nodo, (x, y) in posiciones.items():
        if nodo in orígenes or nodo in destinos:
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
                textfont=dict(size=9, color="white", family="Arial Black"),
                hovertemplate=f"<b>{nodo}</b><extra></extra>",
                showlegend=False
            ))

    es_distribucion = "Centro" in str(orígenes[0])
    titulo = "Transporte: Plantas → Centros" if es_distribucion else "Transporte: Centros → Puntos de Venta"

    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=20, color="white")
        ),
        showlegend=True,
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 4.5]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 2.8]
        ),
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0d0d0d",
        font=dict(color="white"),
        height=700,
        margin=dict(b=50, l=50, r=50, t=100)
    )

    colores_leyenda = [
        ("Plantas", "#4169E1"),
        ("Centros Distribución", "#32CD32"),
        ("Puntos Venta", "#FFB84D"),
        ("Ruta Asignada", "#FFD700")
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


def mostrar_resolucion_vogel(costos, oferta, demanda, orígenes, destinos):
    """
    Muestra la resolución del método de Vogel paso a paso
    """

    st.success("✅ Solución Inicial por Método de Vogel Calculada")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Orígenes", len(oferta))
    with col2:
        st.metric("🎯 Destinos", len(demanda))
    with col3:
        st.metric("📊 Total Oferta", sum(oferta))
    with col4:
        st.metric("📊 Total Demanda", sum(demanda))

    # INFORMACIÓN DEL MÉTODO
    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Método de Vogel (VAM)</h2>", unsafe_allow_html=True)
    st.info("""
    **Método de Vogel (VAM - Vogel's Approximation Method):**
    - Calcula penalizaciones (diferencia entre 2 costos mínimos) para filas y columnas
    - Asigna en la celda de menor costo de la fila/columna con mayor penalización
    - Genera soluciones iniciales mejor que esquina noroeste
    - Suele requerir menos iteraciones de optimización
    - Excelente para problemas de transporte grandes
    """)

    # MATRIZ DE COSTOS
    st.write("---")
    st.markdown("<h2 class='section-header'>💰 Matriz de Costos Unitarios</h2>",
                unsafe_allow_html=True)

    costos_df = pd.DataFrame(
        costos,
        index=orígenes,
        columns=destinos
    )
    st.dataframe(costos_df, use_container_width=True)

    # RESOLVER
    vogel = MetodoVogel(costos, oferta, demanda)
    asignacion = vogel.resolver()
    pasos = vogel.obtener_pasos()

    # ITERACIONES
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Algoritmo</h2>",
                unsafe_allow_html=True)

    if pasos:
        tab_list = [f"Paso {p['iteracion']}" for p in pasos]
        tabs_iter = st.tabs(tab_list)

        for idx, tab in enumerate(tabs_iter):
            with tab:
                paso = pasos[idx]

                st.markdown(
                    f"<div class='iteration-header'><h3>Paso {paso['iteracion']}: Cálculo de Penalizaciones</h3></div>",
                    unsafe_allow_html=True)

                # Penalizaciones Filas
                st.subheader("📐 Penalizaciones de Filas")
                if paso['penal_filas_txt']:
                    penal_f_text = "\n".join(paso['penal_filas_txt'])
                    st.code(penal_f_text, language=None)
                else:
                    st.info("Sin penalizaciones de filas")

                # Penalizaciones Columnas
                st.subheader("📐 Penalizaciones de Columnas")
                if paso['penal_cols_txt']:
                    penal_c_text = "\n".join(paso['penal_cols_txt'])
                    st.code(penal_c_text, language=None)
                else:
                    st.info("Sin penalizaciones de columnas")

                # Decisión
                st.subheader("🔎 Decisión")
                st.write(paso['decision'])

                # Asignación
                st.subheader("✏️ Asignación Realizada")
                st.write(paso['asignacion'])

                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("Ruta", f"{orígenes[paso['celda'][0]]} → {destinos[paso['celda'][1]]}")
                with col_info2:
                    st.metric("Cantidad", f"{paso['cantidad']} botellas")
                with col_info3:
                    st.metric("Costo Unit.", f"${paso['costo_unitario']:.4f}")

                # Matriz actual
                st.subheader("📊 Matriz de Asignación Actual")
                matriz_df = pd.DataFrame(
                    paso['matriz'],
                    index=orígenes,
                    columns=destinos
                )
                st.dataframe(matriz_df, use_container_width=True)

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN INICIAL FINAL</h2>",
                unsafe_allow_html=True)

    costo_total = vogel.obtener_costo_total()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Costo Total", f"${costo_total:.2f}")
    with col2:
        st.metric("📦 Asignaciones", sum(1 for fila in asignacion for val in fila if val > 0))
    with col3:
        st.metric("🔍 Método", "Vogel (VAM)")

    st.subheader("✅ Matriz Final de Asignación")
    matriz_final_df = pd.DataFrame(
        asignacion,
        index=orígenes,
        columns=destinos
    )
    st.dataframe(matriz_final_df, use_container_width=True)

    # VISUALIZACIÓN GRÁFICA
    st.write("---")
    st.markdown("<h2 class='section-header'>🗺️ VISUALIZACIÓN GRÁFICA DEL TRANSPORTE</h2>",
                unsafe_allow_html=True)

    fig_transporte = crear_grafo_transporte_vogel(orígenes, destinos, asignacion, costos, orígenes, destinos)
    st.plotly_chart(fig_transporte, use_container_width=True)

    # DESGLOSE DE COSTOS
    st.write("---")
    st.subheader("💹 Desglose de Costos por Ruta")
    desglose_data = []

    for i in range(len(orígenes)):
        for j in range(len(destinos)):
            if asignacion[i][j] > 0:
                cant = asignacion[i][j]
                costo_unit = costos[i][j]
                costo_total_asign = cant * costo_unit

                desglose_data.append({
                    'Ruta': f"{orígenes[i]} → {destinos[j]}",
                    'Cantidad': int(cant),
                    'Costo Unitario': f"${costo_unit:.4f}",
                    'Costo Total': f"${costo_total_asign:.2f}"
                })

    desglose_df = pd.DataFrame(desglose_data)
    st.dataframe(desglose_df, use_container_width=True, hide_index=True)

    # VERIFICACIÓN
    st.write("---")
    st.subheader("✔️ Verificación de Oferta y Demanda")

    # Recalcular oferta y demanda originales (ya que vogel.resolver() las modifica)
    oferta_original = [1500, 1350, 900] if len(orígenes) == 3 else [100, 150, 120]
    demanda_original = [500, 450, 250] if len(destinos) == 3 else [80, 70, 90, 60]

    verif_data = []
    for i in range(len(orígenes)):
        suma_fila = sum(asignacion[i])
        verif_data.append({
            'Origen': orígenes[i],
            'Oferta': oferta_original[i],
            'Asignado': int(suma_fila),
            'Cumple': "✓" if suma_fila == oferta_original[i] else "✗"
        })

    for j in range(len(destinos)):
        suma_col = sum(asignacion[i][j] for i in range(len(orígenes)))
        verif_data.append({
            'Origen': destinos[j],
            'Demanda': demanda_original[j],
            'Recibido': int(suma_col),
            'Cumple': "✓" if suma_col == demanda_original[j] else "✗"
        })

    verif_df = pd.DataFrame(verif_data)
    st.dataframe(verif_df, use_container_width=True, hide_index=True)

    # RESUMEN
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Método: Vogel (VAM)
        - Orígenes: {len(orígenes)}
        - Destinos: {len(destinos)}
        - Oferta Total: {sum(oferta_original)} botellas
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Costo Total: ${costo_total:.2f}
        - Asignaciones: {sum(1 for fila in asignacion for val in fila if val > 0)}
        - Variables Básicas: {len(orígenes) + len(destinos) - 1} (esperadas)
        """)

    return asignacion


def ejemplo_vogel():
    """Ejemplo de Vogel con datos de Coca-Cola"""
    st.subheader("📦 Ejemplo: Método de Vogel - Coca-Cola")
    st.write("""
    **Problema:** Distribuir botellas de Coca-Cola desde plantas a centros de distribución 
    usando el método de Vogel (VAM) que optimiza penalizaciones.
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_vogel_coca_cola"):
        # Datos de Coca-Cola: Plantas a Centros
        plantas = list(PLANTAS.keys())
        centros = list(CENTROS_DISTRIBUCION.keys())

        # Oferta: capacidad mensual de cada planta (en unidades de 1000 botellas)
        oferta = [
            1500,  # Planta_Quito
            1350,  # Planta_Guayaquil
            900    # Planta_Cuenca
        ]

        # Demanda: capacidad de almacenamiento de cada centro
        demanda = [
            500,   # Centro_Quito
            450,   # Centro_Guayaquil
            250    # Centro_Cuenca
        ]

        # Matriz de costos de transporte (por 1000 botellas)
        costos = [
            [0.05, 0.15, 0.08],  # Desde Planta_Quito
            [0.15, 0.05, 0.12],  # Desde Planta_Guayaquil
            [0.08, 0.12, 0.04]   # Desde Planta_Cuenca
        ]

        mostrar_resolucion_vogel(costos, oferta, demanda, plantas, centros)