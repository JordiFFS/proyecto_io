# views/resolucion_ruta_mas_corta.py

import streamlit as st
import pandas as pd
from models.redes.red import Red
from models.redes.ruta_corta import RutaMasCorta
from models.redes.adaptadores import red_a_matriz_distancias


def mostrar_resolucion_ruta_mas_corta(resultado, iteraciones, nodos, matriz, origen):
    """
    Muestra la resolución completa del algoritmo de Dijkstra
    con visualización paso a paso

    Args:
        resultado: Diccionario con resultado final del Dijkstra
        iteraciones: Lista de iteraciones del algoritmo
        nodos: Lista de nodos de la red
        matriz: Matriz de distancias
        origen: Nodo origen
    """

    st.success("✅ Ruta Más Corta Calculada Exitosamente")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📍 Nodos en la Red", len(nodos))
    with col2:
        st.metric("🔗 Arcos", sum(1 for i in range(len(nodos)) for j in range(len(nodos))
                                 if matriz[i][j] != float('inf') and i != j))
    with col3:
        st.metric("🟢 Nodo Origen", origen)
    with col4:
        st.metric("🔍 Algoritmo", "Dijkstra")

    # MATRIZ DE DISTANCIAS
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Matriz de Distancias</h2>", unsafe_allow_html=True)

    matriz_df = pd.DataFrame(
        [[float('inf') if matriz[i][j] == float('inf') else matriz[i][j]
          for j in range(len(nodos))] for i in range(len(nodos))],
        index=nodos,
        columns=nodos
    )
    st.dataframe(matriz_df, use_container_width=True)

    # ITERACIONES DEL ALGORITMO
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Algoritmo Dijkstra</h2>",
                unsafe_allow_html=True)

    if iteraciones:
        tab_list = [f"Iter. {i}" for i in range(len(iteraciones))]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter):
            with tab:
                iter_info = iteraciones[iter_num]

                st.markdown(
                    f"<div class='iteration-header'><h3>Iteración {iter_num}</h3></div>",
                    unsafe_allow_html=True)

                if iter_info['nodo_fijado']:
                    st.markdown(
                        f"<div class='metric-box'><strong>Nodo Fijado:</strong><br>{iter_info['nodo_fijado']}</div>",
                        unsafe_allow_html=True)

                # Mostrar distancias actuales
                st.subheader("📏 Distancias Acumuladas")
                dist_df = pd.DataFrame([
                    {
                        'Nodo': nodo,
                        'Distancia': iter_info['distancias'][nodo],
                        'Predecesor': iter_info['predecesores'][nodo] or '-'
                    }
                    for nodo in nodos
                ])
                st.dataframe(dist_df, use_container_width=True, hide_index=True)

                # Relajaciones en esta iteración
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
                            'Anterior': f"{relaj['antes']:.2f}" if relaj['antes'] != float('inf') else "∞",
                            'Mejoró': "✓" if relaj['mejora'] else "✗"
                        })
                    relaj_df = pd.DataFrame(relaj_data)
                    st.dataframe(relaj_df, use_container_width=True, hide_index=True)

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN FINAL - RUTAS MÁS CORTAS</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 Origen", resultado['origen'])
    with col2:
        nodos_alcanzables = sum(1 for ruta in resultado['rutas']
                                if ruta['distancia'] != float('inf'))
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
            distancia_str = f"{distancia:.2f}"

        rutas_data.append({
            'Destino': ruta['destino'],
            'Distancia': distancia_str,
            'Ruta Óptima': ruta['ruta']
        })

    rutas_df = pd.DataFrame(rutas_data)
    st.dataframe(rutas_df, use_container_width=True, hide_index=True)

    # ÁRBOL DE PREDECESORES
    st.subheader("🌳 Árbol de Predecesores")
    pred_data = []
    for nodo in nodos:
        predecesor = resultado['predecesores'][nodo]
        pred_data.append({
            'Nodo': nodo,
            'Predecesor': predecesor if predecesor else '-'
        })

    pred_df = pd.DataFrame(pred_data)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

    # RESUMEN
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
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Nodos Alcanzables: {nodos_alcanzables} de {len(nodos)}
        - Iteraciones: {len(iteraciones)}
        """)


def ejemplo_ruta_corta():
    """Ejemplo predefinido de ruta más corta"""
    st.subheader("Ejemplo: Ruta Más Corta entre Ciudades")
    st.write("""
    **Problema:** Encontrar la ruta más corta desde la ciudad A a todas las demás ciudades.

    **Red:**
    - A → B (3)
    - A → C (8)
    - B → C (1)
    - B → D (7)
    - C → D (2)
    - C → E (4)
    - D → E (1)
    """)

    if st.button("Ejecutar Ejemplo", key="ej_ruta_corta"):
        red = Red(['A', 'B', 'C', 'D', 'E'])
        red.agregar_arco('A', 'B', costo=3)
        red.agregar_arco('A', 'C', costo=8)
        red.agregar_arco('B', 'C', costo=1)
        red.agregar_arco('B', 'D', costo=7)
        red.agregar_arco('C', 'D', costo=2)
        red.agregar_arco('C', 'E', costo=4)
        red.agregar_arco('D', 'E', costo=1)

        matriz, nodos = red_a_matriz_distancias(red)
        dijkstra = RutaMasCorta(matriz, nodos)
        resultado = dijkstra.resolver(0)

        mostrar_resolucion_ruta_mas_corta(resultado, dijkstra.iteraciones, nodos, matriz, 'A')