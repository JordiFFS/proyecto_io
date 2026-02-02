# views/resolucion_esquina_noroeste.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from models.transporte.esquina_noroeste import EsquinaNoreste
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible
from empresa.datos_empresa import (
    PLANTAS, CENTROS_DISTRIBUCION, COSTOS_TRANSPORTE_DISTRIBUCION,
    PUNTOS_VENTA, COSTOS_TRANSPORTE_VENTA
)


def crear_grafo_transporte_esquina(orígenes, destinos, asignacion, costos, nombres_origenes, nombres_destinos):
    """
    Crea un gráfico interactivo del transporte para Esquina Noroeste
    """
    fig = go.Figure()

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
                        line=dict(width=3, color="#4ECDC4"),
                        hovertemplate=f"<b>{origen} → {destino}</b><br>Cantidad: {cantidad}<br>Costo: ${costo_total:.2f}<extra></extra>",
                        showlegend=False
                    ))

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
        ("Ruta Asignada", "#4ECDC4")
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


def mostrar_resolucion_esquina_noroeste(costos, oferta, demanda, orígenes, destinos):
    """
    Muestra la resolución del método de Esquina Noroeste paso a paso
    """

    st.success("✅ Solución Inicial por Esquina Noroeste Calculada")

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

    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Método Esquina Noroeste</h2>", unsafe_allow_html=True)
    st.info("""
    **Algoritmo:**
    - Inicia en la esquina superior izquierda (Noroeste)
    - Asigna el máximo posible a cada celda
    - Se mueve hacia la derecha o abajo según si se agota oferta o demanda
    - No considera costos, solo posiciones
    - Genera una solución inicial factible rápidamente
    """)

    st.write("---")
    st.markdown("<h2 class='section-header'>💰 Matriz de Costos Unitarios</h2>",
                unsafe_allow_html=True)

    costos_df = pd.DataFrame(
        costos,
        index=orígenes,
        columns=destinos
    )
    st.dataframe(costos_df, use_container_width=True)

    en = EsquinaNoreste(costos, oferta, demanda)
    resultado = en.resolver()
    pasos = en.obtener_pasos()

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
                    f"<div class='iteration-header'><h3>Paso {paso['iteracion']}: Asignación {orígenes[paso['celda'][0]]} → {destinos[paso['celda'][1]]}</h3></div>",
                    unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(
                        f"<div class='metric-box'><strong>Ruta:</strong><br>{orígenes[paso['celda'][0]]} → {destinos[paso['celda'][1]]}</div>",
                        unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        f"<div class='metric-box'><strong>Costo Unitario:</strong><br>${paso['costo_unitario']:.4f}</div>",
                        unsafe_allow_html=True)
                with col3:
                    st.markdown(
                        f"<div class='metric-box'><strong>Cantidad:</strong><br>{paso['cantidad']} botellas</div>",
                        unsafe_allow_html=True)
                with col4:
                    st.markdown(
                        f"<div class='metric-box'><strong>Costo Parcial:</strong><br>${paso['costo_celda']:.2f}</div>",
                        unsafe_allow_html=True)

                st.write("")

                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Oferta restante {orígenes[paso['celda'][0]]}:** {paso['oferta_restante']}")
                with col_info2:
                    st.write(f"**Demanda restante {destinos[paso['celda'][1]]}:** {paso['demanda_restante']}")

                st.subheader("📊 Matriz de Asignación Actual")
                matriz_df = pd.DataFrame(
                    paso['matriz'],
                    index=orígenes,
                    columns=destinos
                )
                st.dataframe(matriz_df, use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN INICIAL FINAL</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Costo Total", f"${resultado['costo_total']:.2f}")
    with col2:
        st.metric("📦 Asignaciones", sum(1 for fila in resultado['asignacion'] for val in fila if val > 0))
    with col3:
        st.metric("🔍 Método", "Esquina Noroeste")

    st.subheader("✅ Matriz Final de Asignación")
    matriz_final_df = pd.DataFrame(
        resultado['asignacion'],
        index=orígenes,
        columns=destinos
    )
    st.dataframe(matriz_final_df, use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🗺️ VISUALIZACIÓN GRÁFICA DEL TRANSPORTE</h2>",
                unsafe_allow_html=True)

    fig_transporte = crear_grafo_transporte_esquina(orígenes, destinos, resultado['asignacion'], costos, orígenes, destinos)
    st.plotly_chart(fig_transporte, use_container_width=True)

    st.write("---")
    st.subheader("💹 Desglose de Costos por Ruta")
    desglose_data = []

    for i in range(len(orígenes)):
        for j in range(len(destinos)):
            if resultado['asignacion'][i][j] > 0:
                cant = resultado['asignacion'][i][j]
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

    st.write("---")
    st.subheader("✔️ Verificación de Oferta y Demanda")

    verif_data = []
    for i in range(len(orígenes)):
        suma_fila = sum(resultado['asignacion'][i])
        verif_data.append({
            'Origen': orígenes[i],
            'Oferta': oferta[i],
            'Asignado': int(suma_fila),
            'Cumple': "✓" if suma_fila == oferta[i] else "✗"
        })

    for j in range(len(destinos)):
        suma_col = sum(resultado['asignacion'][i][j] for i in range(len(orígenes)))
        verif_data.append({
            'Origen': destinos[j],
            'Demanda': demanda[j],
            'Recibido': int(suma_col),
            'Cumple': "✓" if suma_col == demanda[j] else "✗"
        })

    verif_df = pd.DataFrame(verif_data)
    st.dataframe(verif_df, use_container_width=True, hide_index=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Método: Esquina Noroeste
        - Orígenes: {len(orígenes)}
        - Destinos: {len(destinos)}
        - Oferta Total: {sum(oferta)} botellas
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Costo Total: ${resultado['costo_total']:.2f}
        - Asignaciones: {sum(1 for fila in resultado['asignacion'] for val in fila if val > 0)}
        - Variables Básicas: {len(orígenes) + len(destinos) - 1} (esperadas)
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
                origen="Esquina Noroeste",
                rutas=[{"destino": f"{orígenes[i]}→{destinos[j]}", "distancia": resultado['asignacion'][i][j], "ruta": f"{orígenes[i]}-{destinos[j]}"}
                       for i in range(len(orígenes)) for j in range(len(destinos)) if resultado['asignacion'][i][j] > 0],
                iteraciones=len(pasos),
                total_nodos=len(orígenes) + len(destinos)
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen="Esquina Noroeste",
                rutas=[{"destino": f"{orígenes[i]}→{destinos[j]}", "distancia": resultado['asignacion'][i][j], "ruta": f"{orígenes[i]}-{destinos[j]}"}
                       for i in range(len(orígenes)) for j in range(len(destinos)) if resultado['asignacion'][i][j] > 0],
                iteraciones=len(pasos),
                total_nodos=len(orígenes) + len(destinos)
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen="Esquina Noroeste",
                rutas=[{"destino": f"{orígenes[i]}→{destinos[j]}", "distancia": resultado['asignacion'][i][j], "ruta": f"{orígenes[i]}-{destinos[j]}"}
                       for i in range(len(orígenes)) for j in range(len(destinos)) if resultado['asignacion'][i][j] > 0],
                iteraciones=len(pasos),
                total_nodos=len(orígenes) + len(destinos)
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

    return resultado


def ejemplo_esquina_noroeste():
    """Ejemplo de Esquina Noroeste con datos de Coca-Cola"""
    st.subheader("📦 Ejemplo: Método Esquina Noroeste - Coca-Cola")
    st.write("""
    **Problema:** Distribuir botellas de Coca-Cola desde plantas a centros de distribución 
    usando el método Esquina Noroeste.
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_esquina_coca_cola"):
        plantas = list(PLANTAS.keys())
        centros = list(CENTROS_DISTRIBUCION.keys())

        oferta = [1500, 1350, 900]
        demanda = [500, 450, 250]
        costos = [
            [0.05, 0.15, 0.08],
            [0.15, 0.05, 0.12],
            [0.08, 0.12, 0.04]
        ]

        mostrar_resolucion_esquina_noroeste(costos, oferta, demanda, plantas, centros)