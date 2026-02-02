# resolucion_ruta_mas_corta.py - ACTUALIZADO
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.redes.red import Red
from models.redes.ruta_corta import RutaMasCorta
from models.redes.adaptadores import red_a_matriz_distancias
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible


def crear_grafo_red(red, resultado, origen):
    """
    Crea un gráfico interactivo de la red de distribución
    mostrando las rutas más cortas desde el origen
    """
    fig = go.Figure()

    posiciones = {
        "Planta_Quito": (0, 2),
        "Planta_Guayaquil": (0, 1),
        "Planta_Cuenca": (0, 0),
        "Centro_Quito": (1.5, 2),
        "Centro_Guayaquil": (1.5, 1),
        "Centro_Cuenca": (1.5, 0),
        "SupermercadoA": (3, 2.2),
        "SupermercadoB": (3, 0.8),
        "TiendaDistribuidor1": (3, 2),
        "TiendaDistribuidor2": (3, 1),
        "TiendaMinorista1": (3, -0.2),
        "TiendaMinorista2": (3, 2.4),
    }

    for arco in red.arcos:
        origen_arco = arco["origen"]
        destino_arco = arco["destino"]

        if origen_arco in posiciones and destino_arco in posiciones:
            x0, y0 = posiciones[origen_arco]
            x1, y1 = posiciones[destino_arco]

            color = "#444444"
            ancho = 1.5

            for ruta in resultado["rutas"]:
                if ruta["distancia"] != "∞":
                    ruta_nodos = ruta["ruta"].split(" → ")
                    for i in range(len(ruta_nodos) - 1):
                        if ruta_nodos[i] == origen_arco and ruta_nodos[i + 1] == destino_arco:
                            color = "#FF6B6B"
                            ancho = 3
                            break

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=ancho, color=color),
                hovertemplate=f"<b>{origen_arco} → {destino_arco}</b><br>Distancia: {arco.get('distancia', 'N/A'):.2f} km<extra></extra>",
                showlegend=False
            ))

    colores_nodo = {
        "planta": "#4169E1",
        "distribucion": "#32CD32",
        "venta": "#FFB84D"
    }

    for nodo, (x, y) in posiciones.items():
        tipo = red.tipos_nodo.get(nodo, "desconocido")
        color = colores_nodo.get(tipo, "#808080")

        tamano = 35 if nodo == origen else 25
        if nodo == origen:
            borde_ancho = 3
            borde_color = "#FF0000"
        else:
            borde_ancho = 1
            borde_color = "white"

        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            marker=dict(
                size=tamano,
                color=color,
                line=dict(width=borde_ancho, color=borde_color)
            ),
            text=[nodo],
            textposition="top center",
            textfont=dict(size=10, color="white", family="Arial Black"),
            hovertemplate=f"<b>{nodo}</b><extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title=dict(
            text=f"Red de Distribución Coca-Cola - Rutas desde {origen}",
            font=dict(size=20, color="white")
        ),
        showlegend=True,
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 3.5]
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
        ("Planta", "#4169E1"),
        ("Distribución", "#32CD32"),
        ("Venta", "#FFB84D"),
        ("Ruta Óptima", "#FF6B6B")
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


def mostrar_resolucion_ruta_corta(resultado, iteraciones, nodos, matriz, origen, red):
    """
    Muestra la resolución completa del algoritmo de Dijkstra
    con visualización paso a paso y gráficos
    """

    st.success("✅ Ruta Más Corta Calculada Exitosamente")

    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Nodos en la Red", len(nodos))
    with col2:
        st.metric("🔗 Arcos", len(red.arcos))
    with col3:
        st.metric("🟢 Nodo Origen", origen)
    with col4:
        st.metric("🔍 Algoritmo", "Dijkstra")

    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Matriz de Distancias</h2>", unsafe_allow_html=True)

    matriz_df = pd.DataFrame(
        [[float('inf') if matriz[i][j] == float('inf') else f"{matriz[i][j]:.2f}"
          for j in range(len(nodos))] for i in range(len(nodos))],
        index=nodos,
        columns=nodos
    )
    st.dataframe(matriz_df, use_container_width=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Algoritmo Dijkstra</h2>",
                unsafe_allow_html=True)

    if iteraciones:
        tab_list = [f"Iter. {i}" for i in range(len(iteraciones))]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter):
            with tab:
                iter_info = iteraciones[iter_num]

                if iter_info['nodo_fijado']:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        st.markdown(
                            f"<div class='metric-box'><strong>Nodo Fijado:</strong><br>{iter_info['nodo_fijado']}</div>",
                            unsafe_allow_html=True)

                st.subheader("📏 Distancias Acumuladas")
                dist_data = []
                for nodo in nodos:
                    dist_val = iter_info['distancias'][nodo]
                    dist_str = f"{dist_val:.2f}" if isinstance(dist_val, (int, float)) and dist_val != float(
                        'inf') else str(dist_val)

                    dist_data.append({
                        'Nodo': nodo,
                        'Distancia': dist_str,
                        'Predecesor': iter_info['predecesores'][nodo] or '-'
                    })

                dist_df = pd.DataFrame(dist_data)
                st.dataframe(dist_df, use_container_width=True, hide_index=True)

                if iter_info['relajaciones']:
                    st.subheader("🔗 Relajaciones Realizadas")
                    relaj_data = []
                    for relaj in iter_info['relajaciones']:
                        relaj_data.append({
                            'Desde': relaj['desde'],
                            'Hacia': relaj['hacia'],
                            'Dist(u)': f"{relaj['dist_u']:.2f}",
                            'Costo Arco': f"{relaj['costo']:.2f}",
                            'Nueva Distancia': f"{relaj['nueva']:.2f}",
                            'Anterior': f"{relaj['antes']:.2f}" if isinstance(relaj['antes'], (int, float)) and relaj[
                                'antes'] != float('inf') else "∞",
                            'Mejoró': "✓" if relaj['mejora'] else "✗"
                        })
                    relaj_df = pd.DataFrame(relaj_data)
                    st.dataframe(relaj_df, use_container_width=True, hide_index=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN FINAL - RUTAS MÁS CORTAS</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 Origen", resultado['origen'])
    with col2:
        nodos_alcanzables = sum(1 for ruta in resultado['rutas']
                                if ruta['distancia'] != float('inf') and ruta['distancia'] != "∞")
        st.metric("📍 Nodos Alcanzables", nodos_alcanzables)
    with col3:
        st.metric("🔀 Total de Nodos", len(nodos))

    st.subheader("✅ Rutas Óptimas desde el Origen")
    rutas_data = []
    for ruta in resultado['rutas']:
        distancia = ruta['distancia']
        if isinstance(distancia, float) and distancia == float('inf'):
            distancia_str = "No Alcanzable"
        else:
            try:
                distancia_str = f"{float(distancia):.2f}"
            except:
                distancia_str = str(distancia)

        rutas_data.append({
            'Destino': ruta['destino'],
            'Distancia': distancia_str,
            'Ruta Óptima': ruta['ruta']
        })

    rutas_df = pd.DataFrame(rutas_data)
    st.dataframe(rutas_df, use_container_width=True, hide_index=True)

    # ÁRBOL DE PREDECESORES
    st.write("---")
    st.markdown("<h2 class='section-header'>🌳 Árbol de Predecesores</h2>", unsafe_allow_html=True)

    pred_data = []
    for nodo in nodos:
        predecesor = resultado['predecesores'][nodo]
        pred_data.append({
            'Nodo': nodo,
            'Predecesor': predecesor if predecesor else '-'
        })

    pred_df = pd.DataFrame(pred_data)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

    # RESUMEN EJECUTIVO
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Algoritmo: Dijkstra
        - Tipo: Ruta Más Corta
        - Origen: {resultado['origen']}
        - Total de Nodos: {len(nodos)}
        - Total de Arcos: {len(red.arcos)}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Nodos Alcanzables: {nodos_alcanzables} de {len(nodos)}
        - Iteraciones: {len(iteraciones)}
        - Distancia Máxima: {max([float(r['distancia']) for r in resultado['rutas'] if r['distancia'] != "∞" and isinstance(r['distancia'], (int, float))] + [0]):.2f} km
        """)

    # GRÁFICO DE LA RED
    st.write("---")
    st.markdown("<h2 class='section-header'>🕸️ Visualización de la Red</h2>", unsafe_allow_html=True)
    fig_red = crear_grafo_red(red, resultado, origen)
    st.plotly_chart(fig_red, use_container_width=True)

    # ==================================================
    # 🤖 ANÁLISIS CON MÚLTIPLES IAS - AL FINAL
    # ==================================================
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Análisis Comparativo con IA</h2>", unsafe_allow_html=True)
    st.info("⏳ Generando análisis con Gemini, Hugging Face y Ollama para comparación...")

    # Contenedor para los análisis
    analisis_container = st.container()

    # Generar análisis con las tres IAs
    analisis_data = {}

    # GEMINI
    with st.spinner("🤖 Generando análisis con Gemini..."):
        try:
            analisis_data['gemini'] = generar_analisis_gemini(
                origen=origen,
                rutas=resultado['rutas'],
                iteraciones=len(iteraciones),
                total_nodos=len(nodos)
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    # HUGGING FACE
    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen=origen,
                rutas=resultado['rutas'],
                iteraciones=len(iteraciones),
                total_nodos=len(nodos)
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    # OLLAMA
    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen=origen,
                rutas=resultado['rutas'],
                iteraciones=len(iteraciones),
                total_nodos=len(nodos)
            )
        except Exception as e:
            analisis_data['ollama'] = f"❌ Error: {str(e)}"

    # Mostrar análisis en pestañas
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


def ejemplo_ruta_corta_coca_cola():
    """Ejemplo de ruta más corta en red Coca-Cola"""
    st.subheader("📦 Ejemplo: Ruta Más Corta en Red Coca-Cola")
    st.write("""
    **Problema:** Encontrar las rutas más cortas desde la Planta Quito 
    a todos los centros de distribución y puntos de venta.

    **Red de Distribución:**
    - 3 Plantas de Producción
    - 3 Centros de Distribución
    - 6 Puntos de Venta
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_ruta_corta_coca"):
        nodos = [
            "Planta_Quito", "Planta_Guayaquil", "Planta_Cuenca",
            "Centro_Quito", "Centro_Guayaquil", "Centro_Cuenca",
            "SupermercadoA", "SupermercadoB",
            "TiendaDistribuidor1", "TiendaDistribuidor2",
            "TiendaMinorista1", "TiendaMinorista2"
        ]

        red = Red(nodos)

        for nodo in ["Planta_Quito", "Planta_Guayaquil", "Planta_Cuenca"]:
            red.set_tipo_nodo(nodo, "planta")

        for nodo in ["Centro_Quito", "Centro_Guayaquil", "Centro_Cuenca"]:
            red.set_tipo_nodo(nodo, "distribucion")

        for nodo in ["SupermercadoA", "SupermercadoB", "TiendaDistribuidor1",
                     "TiendaDistribuidor2", "TiendaMinorista1", "TiendaMinorista2"]:
            red.set_tipo_nodo(nodo, "venta")

        arcos_datos = [
            ("Planta_Quito", "Centro_Quito", 0.05),
            ("Planta_Quito", "Centro_Guayaquil", 0.15),
            ("Planta_Quito", "Centro_Cuenca", 0.08),
            ("Centro_Quito", "SupermercadoA", 0.03),
            ("Centro_Quito", "TiendaDistribuidor1", 0.02),
            ("Centro_Quito", "TiendaMinorista2", 0.03),
            ("Centro_Guayaquil", "SupermercadoB", 0.03),
            ("Centro_Guayaquil", "TiendaDistribuidor2", 0.02),
            ("Centro_Cuenca", "TiendaMinorista1", 0.03),
            ("Centro_Quito", "Centro_Guayaquil", 0.10),
            ("Centro_Guayaquil", "Centro_Cuenca", 0.12),
            ("Centro_Quito", "Centro_Cuenca", 0.15),
        ]

        for origen_arco, destino, distancia in arcos_datos:
            red.agregar_arco(origen_arco, destino, costo=distancia, distancia=distancia)

        matriz, nodos_matriz = red_a_matriz_distancias(red)
        dijkstra = RutaMasCorta(matriz, nodos_matriz)
        resultado = dijkstra.resolver(0)

        mostrar_resolucion_ruta_corta(resultado, dijkstra.iteraciones, nodos_matriz, matriz, 'Planta_Quito', red)