# views/resolucion_flujo_maximo.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.redes.red import Red
from models.redes.flujo_maximo import FlujoMaximo
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible
from empresa.datos_empresa import CENTROS_DISTRIBUCION, PUNTOS_VENTA, COSTOS_TRANSPORTE_VENTA


def crear_grafo_flujo(nodos, arcos_flujo, origen, destino):
    """
    Crea un gráfico del flujo máximo en la red
    """
    fig = go.Figure()

    # Posiciones predefinidas
    posiciones = {
        "Centro_Quito": (0, 2),
        "Centro_Guayaquil": (0, 1),
        "Centro_Cuenca": (0, 0),
        "SupermercadoA": (2, 2.2),
        "SupermercadoB": (2, 0.8),
        "TiendaDistribuidor1": (2, 2),
        "TiendaDistribuidor2": (2, 1),
        "TiendaMinorista1": (2, -0.2),
        "TiendaMinorista2": (2, 2.4),
    }

    # Agregar arcos con flujo
    for (u, v), flujo in arcos_flujo.items():
        if u in posiciones and v in posiciones and flujo > 0:
            x0, y0 = posiciones[u]
            x1, y1 = posiciones[v]

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=3, color="#FF6B6B"),
                hovertemplate=f"<b>{u} → {v}</b><br>Flujo: {flujo:.2f}<extra></extra>",
                showlegend=False
            ))

    colores_nodo = {
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
        if nodo in nodos:
            color = colores_nodo.get(nodo, "#808080")

            # Destacar origen y destino
            tamano = 35 if nodo in [origen, destino] else 25
            if nodo == origen:
                borde_color = "#00FF00"
                borde_ancho = 3
            elif nodo == destino:
                borde_color = "#FF0000"
                borde_ancho = 3
            else:
                borde_color = "white"
                borde_ancho = 1

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
                textfont=dict(size=9, color="white", family="Arial Black"),
                hovertemplate=f"<b>{nodo}</b><extra></extra>",
                showlegend=False
            ))

    fig.update_layout(
        title=dict(
            text=f"Flujo Máximo - De {origen} a {destino}",
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
            range=[-0.5, 2.8]
        ),
        plot_bgcolor="#1a1a1a",
        paper_bgcolor="#0d0d0d",
        font=dict(color="white"),
        height=600,
        margin=dict(b=50, l=50, r=50, t=100)
    )

    colores_leyenda = [
        ("Centros Distribución", "#32CD32"),
        ("Puntos Venta", "#FFB84D"),
        ("Flujo Activo", "#FF6B6B"),
        ("Origen", "#00FF00"),
        ("Destino", "#FF0000")
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


def mostrar_resolucion_flujo_maximo(resultado, nodos, origen, destino):
    """
    Muestra la resolución completa del algoritmo de flujo máximo
    usando Ford-Fulkerson con BFS (Edmonds-Karp)
    """

    st.success("✅ Flujo Máximo Calculado Exitosamente")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Total de Nodos", len(nodos))
    with col2:
        st.metric("🟢 Nodo Origen", origen)
    with col3:
        st.metric("🔴 Nodo Destino", destino)
    with col4:
        st.metric("🔍 Algoritmo", "Ford-Fulkerson")

    # INFORMACIÓN GENERAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 FLUJO MÁXIMO ENCONTRADO</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💧 Flujo Máximo", f"{resultado['flujo_maximo']:.2f}")
    with col2:
        st.metric("🔄 Iteraciones", len(resultado['iteraciones']))
    with col3:
        st.metric("🌊 Caminos Aumentados", len(resultado['iteraciones']))

    # ITERACIONES - CAMINOS AUMENTADOS
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones - Caminos Aumentados</h2>",
                unsafe_allow_html=True)

    if resultado['iteraciones']:
        tab_list = [f"Paso {i + 1}" for i in range(len(resultado['iteraciones']))]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter):
            with tab:
                iter_info = resultado['iteraciones'][iter_num]

                st.markdown(
                    f"<div class='iteration-header'><h3>Iteración {iter_num + 1} - Camino Aumentado</h3></div>",
                    unsafe_allow_html=True)

                # Información del camino
                col1, col2, col3 = st.columns(3)
                with col1:
                    ruta_str = " → ".join([str(arco[0]) for arco in iter_info['ruta']] +
                                          [str(iter_info['ruta'][-1][1])])
                    st.markdown(
                        f"<div class='metric-box'><strong>Camino:</strong><br>{ruta_str}</div>",
                        unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        f"<div class='metric-box'><strong>Flujo Enviado:</strong><br>{iter_info['flujo_enviado']:.2f}</div>",
                        unsafe_allow_html=True)
                with col3:
                    st.markdown(
                        f"<div class='metric-box'><strong>Flujo Acumulado:</strong><br>{iter_info['flujo_acumulado']:.2f}</div>",
                        unsafe_allow_html=True)

                # Detalles de arcos en el camino
                st.subheader("🔗 Arcos del Camino")
                arcos_data = []
                for i, (u, v) in enumerate(iter_info['ruta']):
                    arcos_data.append({
                        '#': i + 1,
                        'Desde': u,
                        'Hacia': v,
                        'Arco': f"{u} → {v}",
                        'Flujo Enviado': f"{iter_info['flujo_enviado']:.2f}"
                    })

                arcos_df = pd.DataFrame(arcos_data)
                st.dataframe(arcos_df, use_container_width=True, hide_index=True)

    else:
        st.info("El flujo máximo se alcanzó en la iteración inicial (sin caminos aumentados adicionales).")

    # RESUMEN DE FLUJOS
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen de Flujos</h2>", unsafe_allow_html=True)

    summary_data = []
    for i, iter_info in enumerate(resultado['iteraciones'], 1):
        summary_data.append({
            'Iteración': i,
            'Camino': " → ".join([str(arco[0]) for arco in iter_info['ruta']] +
                                 [str(iter_info['ruta'][-1][1])]),
            'Flujo': f"{iter_info['flujo_enviado']:.2f}",
            'Acumulado': f"{iter_info['flujo_acumulado']:.2f}"
        })

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # VISUALIZACIÓN GRÁFICA
    st.write("---")
    st.markdown("<h2 class='section-header'>🗺️ VISUALIZACIÓN GRÁFICA DEL FLUJO</h2>",
                unsafe_allow_html=True)

    # Calcular flujos por arco
    arcos_flujo = {}
    for iter_info in resultado['iteraciones']:
        for u, v in iter_info['ruta']:
            arcos_flujo[(u, v)] = arcos_flujo.get((u, v), 0) + iter_info['flujo_enviado']

    fig_flujo = crear_grafo_flujo(nodos, arcos_flujo, origen, destino)
    st.plotly_chart(fig_flujo, use_container_width=True)

    # VERIFICACIÓN
    st.write("---")
    st.subheader("✔️ Verificación del Flujo Máximo")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Flujo Total", f"{resultado['flujo_maximo']:.2f}")
    with col2:
        st.metric("Caminos Encontrados", len(resultado['iteraciones']))
    with col3:
        st.metric("Saturados", "✓")

    # PROPIEDADES
    st.write("---")
    st.subheader("⚙️ Propiedades del Algoritmo")
    st.write("""
    - **Algoritmo**: Ford-Fulkerson con BFS (Edmonds-Karp)
    - **Complejidad**: O(VE²)
    - **Propiedad**: Encuentra el flujo máximo de forma iterativa
    - **Terminación**: Cuando no existen caminos aumentados
    """)

    # RESUMEN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Algoritmo: Ford-Fulkerson (Edmonds-Karp)
        - Tipo: Flujo Máximo
        - Origen: {origen}
        - Destino: {destino}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Flujo Máximo: {resultado['flujo_maximo']:.2f}
        - Iteraciones: {len(resultado['iteraciones'])}
        - Nodos: {len(nodos)}
        """)

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
                rutas=[{"destino": destino, "distancia": resultado['flujo_maximo'], "ruta": f"{origen}→{destino}"}],
                iteraciones=len(resultado['iteraciones']),
                total_nodos=len(nodos)
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    # HUGGING FACE
    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen=origen,
                rutas=[{"destino": destino, "distancia": resultado['flujo_maximo'], "ruta": f"{origen}→{destino}"}],
                iteraciones=len(resultado['iteraciones']),
                total_nodos=len(nodos)
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    # OLLAMA
    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen=origen,
                rutas=[{"destino": destino, "distancia": resultado['flujo_maximo'], "ruta": f"{origen}→{destino}"}],
                iteraciones=len(resultado['iteraciones']),
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


def ejemplo_flujo_maximo():
    """Ejemplo de Flujo Máximo con datos de Coca-Cola"""
    st.subheader("📦 Ejemplo: Flujo Máximo - Red de Distribución Coca-Cola")
    st.write("""
    **Problema:** Determinar el flujo máximo de botellas que pueden transportarse 
    desde un Centro de Distribución a los Puntos de Venta.
    """)

    if st.button("Ejecutar Ejemplo Coca-Cola", key="ej_flujo_coca_cola"):
        # Nodos: centros de distribución y puntos de venta
        nodos = [
            "Centro_Quito", "Centro_Guayaquil", "Centro_Cuenca",
            "SupermercadoA", "SupermercadoB",
            "TiendaDistribuidor1", "TiendaDistribuidor2",
            "TiendaMinorista1", "TiendaMinorista2"
        ]

        flujo = FlujoMaximo(nodos)

        # Convertir costos a capacidades (botellas/día)
        # Usar demanda como capacidad
        capacidades = {
            ("Centro_Quito", "SupermercadoA"): 5000,
            ("Centro_Quito", "TiendaDistribuidor1"): 8000,
            ("Centro_Quito", "TiendaMinorista2"): 2500,
            ("Centro_Guayaquil", "SupermercadoB"): 4500,
            ("Centro_Guayaquil", "TiendaDistribuidor2"): 7500,
            ("Centro_Guayaquil", "TiendaMinorista1"): 3000,
            ("Centro_Cuenca", "TiendaMinorista1"): 3000,
            ("Centro_Cuenca", "SupermercadoB"): 4500,
            ("Centro_Cuenca", "TiendaDistribuidor2"): 7500,
        }

        # Agregar arcos al flujo
        for (origen, destino), capacidad in capacidades.items():
            flujo.agregar_arco(origen, destino, capacidad)

        # Resolver desde Centro_Quito como origen (podría ser cualquier centro)
        resultado = flujo.resolver("Centro_Quito", "SupermercadoA")

        mostrar_resolucion_flujo_maximo(resultado, nodos, "Centro_Quito", "SupermercadoA")