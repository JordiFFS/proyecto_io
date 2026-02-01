"""
views/resolucion_optimalidad.py
Vista para Método de Optimalidad (MODI + Stepping Stone) adaptada a Coca-Cola
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from models.transporte.optimalidad import OptimizadorTransporte
from empresa.datos_empresa import (
    PLANTAS, CENTROS_DISTRIBUCION, COSTOS_TRANSPORTE_DISTRIBUCION,
    PUNTOS_VENTA, COSTOS_TRANSPORTE_VENTA
)


def crear_grafo_transporte_optimalidad(orígenes, destinos, asignacion, costos):
    """
    Crea un gráfico interactivo del transporte para la solución óptima
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
                        line=dict(width=3, color="#00FF7F"),
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
    titulo = "Solución Óptima: Plantas → Centros" if es_distribucion else "Solución Óptima: Centros → Puntos de Venta"

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
        ("Ruta Óptima", "#00FF7F")
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


def mostrar_resolucion_optimalidad(costos, oferta, demanda, solucion_inicial, nombre_metodo, orígenes, destinos):
    """
    Muestra la optimización de la solución inicial usando MODI + Stepping Stone
    """

    st.success("✅ Optimización de Solución Iniciada (MODI + Stepping Stone)")

    # INFORMACIÓN DEL MÉTODO
    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Información del Método MODI</h2>",
                unsafe_allow_html=True)

    st.info("""
    **Método MODI (Modified Distribution Method):**
    1. Calcula potenciales u_i (filas) y v_j (columnas)
    2. Evalúa costos marginales de celdas no básicas (Δ_ij = c_ij - u_i - v_j)
    3. Si existe Δ_ij < 0, la solución puede mejorarse
    4. Usa Stepping Stone para encontrar el ciclo cerrado y ajustar asignaciones
    5. Repite hasta que todos los Δ_ij ≥ 0 (solución óptima)
    """)

    # SOLUCIÓN INICIAL
    st.write("---")
    st.markdown(f"<h2 class='section-header'>🔍 Solución Inicial (Método: {nombre_metodo})</h2>",
                unsafe_allow_html=True)

    solucion_inicial_df = pd.DataFrame(
        solucion_inicial,
        index=orígenes,
        columns=destinos
    )
    st.dataframe(solucion_inicial_df, use_container_width=True)

    # Costo inicial
    costo_inicial = 0
    for i in range(len(orígenes)):
        for j in range(len(destinos)):
            costo_inicial += solucion_inicial[i][j] * costos[i][j]

    st.metric("💰 Costo Inicial", f"${costo_inicial:.2f}")

    # RESOLVER
    try:
        optimizador = OptimizadorTransporte(costos, solucion_inicial)
        resultado = optimizador.resolver()
        pasos = optimizador.pasos
    except Exception as e:
        st.error(f"Error durante la optimización: {str(e)}")
        return

    # ITERACIONES DE OPTIMIZACIÓN
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Proceso de Optimización (MODI)</h2>",
                unsafe_allow_html=True)

    if pasos:
        # Filtrar pasos (excluir el final de óptimo)
        pasos_iteracion = [p for p in pasos if p.get('status') != 'optimo' and p.get('status') != 'error']

        if pasos_iteracion:
            tab_list = [f"Iteración {p['iteracion']}" for p in pasos_iteracion]
            tabs_iter = st.tabs(tab_list)

            for idx, tab in enumerate(tabs_iter):
                with tab:
                    paso = pasos_iteracion[idx]

                    st.markdown(
                        f"<div class='iteration-header'><h3>Iteración {paso['iteracion']}: Búsqueda de Mejora</h3></div>",
                        unsafe_allow_html=True)

                    # Potenciales
                    st.subheader("1️⃣ Cálculo de Potenciales (u, v)")

                    col_pot1, col_pot2 = st.columns(2)
                    with col_pot1:
                        st.write("**Potenciales de Filas (u):**")
                        st.code(", ".join(paso['u']))
                    with col_pot2:
                        st.write("**Potenciales de Columnas (v):**")
                        st.code(", ".join(paso['v']))

                    with st.expander("📖 Ver proceso de cálculo"):
                        st.markdown(paso['explicacion_potenciales'])

                    # Costos marginales
                    st.subheader("2️⃣ Evaluación de Costos Marginales")
                    st.markdown(paso['seleccion'])

                    with st.expander("📖 Ver todos los costos marginales"):
                        for exp in paso['marginales']:
                            st.text(exp)

                    # Ciclo y Theta
                    if paso.get('ciclo'):
                        st.subheader("3️⃣ Ciclo Cerrado (Stepping Stone)")
                        st.write(f"**Ciclo encontrado:** {paso['ciclo']}")

                        st.subheader("4️⃣ Cálculo de Theta (θ)")
                        st.markdown(paso['explicacion_theta'])

                        st.subheader("5️⃣ Ajuste de la Solución")
                        st.markdown(paso['explicacion_ajuste'])

                    # Matriz después de la iteración
                    st.subheader("📊 Matriz Después de Ajuste")
                    matriz_df = pd.DataFrame(
                        paso['matriz'],
                        index=orígenes,
                        columns=destinos
                    )
                    st.dataframe(matriz_df, use_container_width=True)

    # SOLUCIÓN ÓPTIMA
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA ENCONTRADA</h2>",
                unsafe_allow_html=True)

    # Buscar paso óptimo
    paso_optimo = None
    for p in pasos:
        if p.get('status') == 'optimo':
            paso_optimo = p
            break

    if paso_optimo:
        st.success(paso_optimo['mensaje'])

        costo_optimo = optimizador.obtener_costo_total()
        mejora = costo_inicial - costo_optimo
        porcentaje_mejora = (mejora / costo_inicial) * 100 if costo_inicial > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Costo Óptimo", f"${costo_optimo:.2f}")
        with col2:
            st.metric("📉 Mejora", f"${mejora:.2f}")
        with col3:
            st.metric("📊 % Mejora", f"{porcentaje_mejora:.2f}%")
        with col4:
            st.metric("🔄 Iteraciones", paso_optimo['iteracion'])

        # Matriz óptima
        st.subheader("✅ Matriz Óptima Final")
        matriz_optima_df = pd.DataFrame(
            resultado,
            index=orígenes,
            columns=destinos
        )
        st.dataframe(matriz_optima_df, use_container_width=True)

        # VISUALIZACIÓN GRÁFICA
        st.write("---")
        st.markdown("<h2 class='section-header'>🗺️ VISUALIZACIÓN GRÁFICA DE LA SOLUCIÓN ÓPTIMA</h2>",
                    unsafe_allow_html=True)

        fig_transporte = crear_grafo_transporte_optimalidad(orígenes, destinos, resultado, costos)
        st.plotly_chart(fig_transporte, use_container_width=True)

        # Desglose de costos
        st.write("---")
        st.subheader("💹 Desglose de Costos Óptimos")
        desglose_data = []

        for i in range(len(orígenes)):
            for j in range(len(destinos)):
                if resultado[i][j] > 0:
                    cant = resultado[i][j]
                    costo_unit = costos[i][j]
                    costo_total_asign = cant * costo_unit

                    desglose_data.append({
                        'Ruta': f"{orígenes[i]} → {destinos[j]}",
                        'Cantidad': int(cant),
                        'Costo Unitario': f"${costo_unit:.4f}",
                        'Costo Total': f"${costo_total_asign:.2f}"
                    })

        if desglose_data:
            desglose_df = pd.DataFrame(desglose_data)
            st.dataframe(desglose_df, use_container_width=True, hide_index=True)

        # Verificación
        st.write("---")
        st.subheader("✔️ Verificación de Oferta y Demanda")

        # Recalcular oferta y demanda originales
        oferta_original = [1500, 1350, 900] if len(orígenes) == 3 else oferta
        demanda_original = [500, 450, 250] if len(destinos) == 3 else demanda

        verif_data = []
        for i in range(len(orígenes)):
            suma_fila = sum(resultado[i])
            verif_data.append({
                'Origen': orígenes[i],
                'Oferta': oferta_original[i],
                'Asignado': int(suma_fila),
                'Cumple': "✓" if suma_fila == oferta_original[i] else "✗"
            })

        for j in range(len(destinos)):
            suma_col = sum(resultado[i][j] for i in range(len(orígenes)))
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

    costo_optimo = optimizador.obtener_costo_total()
    mejora = costo_inicial - costo_optimo
    porcentaje_mejora = (mejora / costo_inicial) * 100 if costo_inicial > 0 else 0
    iteraciones = paso_optimo['iteracion'] if paso_optimo else 0

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.write("**Proceso:**")
        st.write(f"- Método Inicial: {nombre_metodo}")
        st.write("- Optimización: MODI")
        st.write("- Algoritmo: Stepping Stone")

    with summary_col2:
        st.write("**Mejoras:**")
        st.write(f"- Costo Inicial: ${costo_inicial:.2f}")
        st.write(f"- Costo Final: ${costo_optimo:.2f}")
        st.write(f"- Ahorro Total: ${mejora:.2f}")

    with summary_col3:
        st.write("**Resultados:**")
        st.write(f"- Iteraciones: {iteraciones}")
        st.write(f"- % Mejora: {porcentaje_mejora:.2f}%")
        st.write("- Status: ✅ Óptimo")

    return resultado


def ejemplo_optimalidad_transporte():
    """Ejemplo de Optimalidad con datos de Coca-Cola"""
    st.subheader("📦 Ejemplo: Optimización (MODI) - Coca-Cola")
    st.write("""
    **Problema:** Mejorar la solución inicial del transporte de Coca-Cola 
    desde plantas a centros de distribución usando MODI + Stepping Stone.
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_optimalidad_coca_cola"):
        # Datos de Coca-Cola: Plantas a Centros
        plantas = list(PLANTAS.keys())
        centros = list(CENTROS_DISTRIBUCION.keys())

        # Oferta: capacidad mensual
        oferta = [1500, 1350, 900]

        # Demanda: capacidad de almacenamiento
        demanda = [500, 450, 250]

        # Matriz de costos
        costos = [
            [0.05, 0.15, 0.08],
            [0.15, 0.05, 0.12],
            [0.08, 0.12, 0.04]
        ]

        # Generar solución inicial usando Vogel
        from models.transporte.vogel import MetodoVogel
        vogel = MetodoVogel(costos, oferta, demanda)
        solucion_inicial = vogel.resolver()

        mostrar_resolucion_optimalidad(costos, oferta, demanda, solucion_inicial, "Vogel", plantas, centros)