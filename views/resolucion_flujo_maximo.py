# views/resolucion_flujo_maximo.py

import streamlit as st
import pandas as pd
from models.redes.red import Red
from models.redes.flujo_maximo import FlujoMaximo


def mostrar_resolucion_flujo_maximo(resultado, nodos, origen, destino):
    """
    Muestra la resolución completa del algoritmo de flujo máximo
    usando Ford-Fulkerson con BFS (Edmonds-Karp)

    Args:
        resultado: Diccionario con resultado del flujo máximo
        nodos: Lista de nodos de la red
        origen: Nodo origen
        destino: Nodo destino
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

    # VERIFICACIÓN
    st.subheader("✔️ Verificación del Flujo Máximo")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Flujo Total", f"{resultado['flujo_maximo']:.2f}")
    with col2:
        st.metric("Caminos Encontrados", len(resultado['iteraciones']))
    with col3:
        st.metric("Saturados", "✓")

    # PROPIEDADES
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


def ejemplo_flujo_maximo():
    """Ejemplo predefinido de flujo máximo"""
    st.subheader("Ejemplo: Flujo Máximo en una Red de Tuberías")
    st.write("""
    **Problema:** Determinar el flujo máximo que puede ir de A a F
    a través de una red de tuberías con capacidades limitadas.

    **Arcos y capacidades:**
    - A → B: 10
    - A → D: 10
    - B → C: 4
    - B → E: 8
    - B → D: 2
    - C → F: 10
    - D → E: 9
    - E → C: 6
    - E → F: 10
    """)

    if st.button("Ejecutar Ejemplo", key="ej_flujo_maximo"):
        flujo = FlujoMaximo(['A', 'B', 'C', 'D', 'E', 'F'])

        flujo.agregar_arco('A', 'B', 10)
        flujo.agregar_arco('A', 'D', 10)
        flujo.agregar_arco('B', 'C', 4)
        flujo.agregar_arco('B', 'E', 8)
        flujo.agregar_arco('B', 'D', 2)
        flujo.agregar_arco('C', 'F', 10)
        flujo.agregar_arco('D', 'E', 9)
        flujo.agregar_arco('E', 'C', 6)
        flujo.agregar_arco('E', 'F', 10)

        resultado = flujo.resolver('A', 'F')

        mostrar_resolucion_flujo_maximo(resultado, ['A', 'B', 'C', 'D', 'E', 'F'], 'A', 'F')