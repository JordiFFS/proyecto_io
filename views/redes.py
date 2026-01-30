# views/redes.py

import streamlit as st
from views.resolucion_ruta_mas_corta import mostrar_resolucion_ruta_mas_corta, ejemplo_ruta_corta
from views.resolucion_arbol_expansion_minima import mostrar_resolucion_arbol_minimo, ejemplo_arbol_minimo
from views.resolucion_flujo_maximo import mostrar_resolucion_flujo_maximo, ejemplo_flujo_maximo
from views.resolucion_costo_minimo import mostrar_resolucion_flujo_costo_minimo, ejemplo_flujo_costo_minimo

from models.redes.red import Red
from models.redes.ruta_corta import RutaMasCorta
from models.redes.adaptadores import red_a_matriz_distancias
from models.redes.arbol_minimo import ArbolMinimo
from models.redes.flujo_maximo import FlujoMaximo
from models.redes.flujo_costo_minimo import FlujoCostoMinimo


def show_redes():
    """Vista principal para problemas de redes"""

    st.markdown("<h1 class='main-header'>🌐 Problemas de Redes</h1>", unsafe_allow_html=True)
    st.markdown("*Algoritmos de Optimización en Redes - Análisis de Caminos, Flujos y Árboles*")

    # Selector de método
    st.markdown("<h2 class='section-header'>Selecciona un Problema</h2>", unsafe_allow_html=True)

    col_metodos = st.columns(4)

    with col_metodos[0]:
        btn_ruta = st.button("🛣️ Ruta Más Corta", use_container_width=True,
                             key="btn_ruta_corta")
    with col_metodos[1]:
        btn_arbol = st.button("🌳 Árbol Expansión Mínima", use_container_width=True,
                              key="btn_arbol_minimo")
    with col_metodos[2]:
        btn_flujo_max = st.button("💧 Flujo Máximo", use_container_width=True,
                                  key="btn_flujo_maximo")
    with col_metodos[3]:
        btn_flujo_costo = st.button("💰 Flujo Costo Mínimo", use_container_width=True,
                                    key="btn_flujo_costo")

    # Mostrar contenido según el botón seleccionado
    if btn_ruta or st.session_state.get('metodo_redes') == 'ruta_corta':
        st.session_state.metodo_redes = 'ruta_corta'
        _mostrar_ruta_mas_corta()

    elif btn_arbol or st.session_state.get('metodo_redes') == 'arbol':
        st.session_state.metodo_redes = 'arbol'
        _mostrar_arbol_minimo()

    elif btn_flujo_max or st.session_state.get('metodo_redes') == 'flujo_maximo':
        st.session_state.metodo_redes = 'flujo_maximo'
        _mostrar_flujo_maximo()

    elif btn_flujo_costo or st.session_state.get('metodo_redes') == 'flujo_costo':
        st.session_state.metodo_redes = 'flujo_costo'
        _mostrar_flujo_costo_minimo()

    else:
        # Mostrar información general
        st.write("---")
        st.markdown("<h2 class='section-header'>📚 Problemas Disponibles</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🛣️ Ruta Más Corta (Dijkstra)
            - **Objetivo:** Encontrar el camino más corto entre dos nodos
            - **Algoritmo:** Dijkstra
            - **Aplicaciones:** Navegación GPS, enrutamiento de redes

            ### 🌳 Árbol de Expansión Mínima (Kruskal)
            - **Objetivo:** Conectar todos los nodos con costo mínimo
            - **Algoritmo:** Kruskal (Union-Find)
            - **Aplicaciones:** Diseño de redes, telecomunicaciones
            """)

        with col2:
            st.markdown("""
            ### 💧 Flujo Máximo (Ford-Fulkerson)
            - **Objetivo:** Maximizar el flujo entre origen y destino
            - **Algoritmo:** Ford-Fulkerson (Edmonds-Karp)
            - **Aplicaciones:** Redes de tuberías, transporte de mercancías

            ### 💰 Flujo de Costo Mínimo
            - **Objetivo:** Enviar flujo minimizando costo total
            - **Algoritmo:** Rutas de Menor Costo Sucesivas
            - **Aplicaciones:** Logística, distribución de productos
            """)


def _mostrar_ruta_mas_corta():
    """Sección de ruta más corta"""
    st.write("---")
    st.markdown("<h2 class='section-header'>🛣️ Ruta Más Corta (Dijkstra)</h2>",
                unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Red")

        # Entrada de nodos
        nodos_input = st.text_input(
            "Nodos (separados por coma)",
            value="A,B,C,D,E",
            help="Ej: A,B,C,D,E"
        )
        nodos = [n.strip() for n in nodos_input.split(',')]

        # Entrada de arcos
        st.write("**Arcos (uno por línea: origen-destino costo)**")
        arcos_input = st.text_area(
            "Arcos",
            value="A-B 3\nA-C 8\nB-C 1\nB-D 7\nC-D 2\nC-E 4\nD-E 1",
            height=200,
            label_visibility="collapsed"
        )

    with col_input2:
        st.subheader("⚙️ Parámetros")

        origen = st.selectbox(
            "Nodo Origen",
            nodos,
            key="ruta_origen"
        )

    # Procesar arcos
    arcos_list = []
    try:
        for linea in arcos_input.strip().split('\n'):
            if linea.strip():
                partes = linea.strip().split()
                if len(partes) >= 2:
                    nodo_arc = partes[0].split('-')
                    if len(nodo_arc) == 2:
                        arcos_list.append((nodo_arc[0], nodo_arc[1], float(partes[1])))
    except:
        st.error("❌ Error al procesar los arcos. Formato: origen-destino costo")
        return

    # Botón ejecutar
    if st.button("▶️ Resolver", key="btn_exec_ruta"):
        try:
            # Crear red
            red = Red(nodos)
            for orig, dest, costo in arcos_list:
                red.agregar_arco(orig, dest, costo=costo)

            # Resolver
            matriz, nodos_ord = red_a_matriz_distancias(red)
            dijkstra = RutaMasCorta(matriz, nodos_ord)
            origen_idx = nodos_ord.index(origen)
            resultado = dijkstra.resolver(origen_idx)

            # Mostrar resultados
            mostrar_resolucion_ruta_mas_corta(resultado, dijkstra.iteraciones,
                                              nodos_ord, matriz, origen)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Ejemplo
    st.write("---")
    ejemplo_ruta_corta()


def _mostrar_arbol_minimo():
    """Sección de árbol de expansión mínima"""
    st.write("---")
    st.markdown("<h2 class='section-header'>🌳 Árbol de Expansión Mínima (Kruskal)</h2>",
                unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Red")

        # Entrada de nodos
        nodos_input = st.text_input(
            "Nodos (separados por coma)",
            value="A,B,C,D,E,F",
            help="Ej: A,B,C,D,E,F",
            key="arbol_nodos"
        )
        nodos = [n.strip() for n in nodos_input.split(',')]

        # Entrada de aristas
        st.write("**Aristas (uno por línea: nodo1-nodo2 costo)**")
        aristas_input = st.text_area(
            "Aristas",
            value="A-B 4\nA-C 2\nB-C 1\nB-D 5\nC-D 8\nC-E 10\nD-E 2\nD-F 6\nE-F 3",
            height=200,
            label_visibility="collapsed",
            key="arbol_aristas"
        )

    with col_input2:
        st.subheader("ℹ️ Información")
        st.info("""
        **Algoritmo Kruskal:**
        1. Ordena aristas por costo ascendente
        2. Selecciona arista si no forma ciclo (Union-Find)
        3. Continúa hasta conectar todos los nodos
        """)

    # Procesar aristas
    aristas_list = []
    try:
        for linea in aristas_input.strip().split('\n'):
            if linea.strip():
                partes = linea.strip().split()
                if len(partes) >= 2:
                    nodo_arc = partes[0].split('-')
                    if len(nodo_arc) == 2:
                        aristas_list.append((nodo_arc[0], nodo_arc[1], float(partes[1])))
    except:
        st.error("❌ Error al procesar las aristas. Formato: nodo1-nodo2 costo")
        return

    # Botón ejecutar
    if st.button("▶️ Resolver", key="btn_exec_arbol"):
        try:
            # Crear árbol
            arbol = ArbolMinimo(nodos)
            aristas_orig = []
            for n1, n2, costo in aristas_list:
                arbol.agregar_arista(n1, n2, costo)
                aristas_orig.append((costo, n1, n2))

            # Resolver
            resultado = arbol.resolver()
            mostrar_resolucion_arbol_minimo(resultado, nodos, aristas_orig)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Ejemplo
    st.write("---")
    ejemplo_arbol_minimo()


def _mostrar_flujo_maximo():
    """Sección de flujo máximo"""
    st.write("---")
    st.markdown("<h2 class='section-header'>💧 Flujo Máximo (Ford-Fulkerson)</h2>",
                unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Red")

        # Entrada de nodos
        nodos_input = st.text_input(
            "Nodos (separados por coma)",
            value="A,B,C,D,E,F",
            help="Ej: A,B,C,D,E,F",
            key="flujo_max_nodos"
        )
        nodos = [n.strip() for n in nodos_input.split(',')]

        # Entrada de arcos
        st.write("**Arcos (uno por línea: origen-destino capacidad)**")
        arcos_input = st.text_area(
            "Arcos",
            value="A-B 10\nA-D 10\nB-C 4\nB-E 8\nB-D 2\nC-F 10\nD-E 9\nE-C 6\nE-F 10",
            height=200,
            label_visibility="collapsed",
            key="flujo_max_arcos"
        )

    with col_input2:
        st.subheader("⚙️ Parámetros")

        origen = st.selectbox(
            "Nodo Origen (Fuente)",
            nodos,
            key="flujo_max_origen"
        )

        destino = st.selectbox(
            "Nodo Destino (Sumidero)",
            nodos,
            key="flujo_max_destino"
        )

    # Procesar arcos
    arcos_list = []
    try:
        for linea in arcos_input.strip().split('\n'):
            if linea.strip():
                partes = linea.strip().split()
                if len(partes) >= 2:
                    nodo_arc = partes[0].split('-')
                    if len(nodo_arc) == 2:
                        arcos_list.append((nodo_arc[0], nodo_arc[1], float(partes[1])))
    except:
        st.error("❌ Error al procesar los arcos. Formato: origen-destino capacidad")
        return

    # Botón ejecutar
    if st.button("▶️ Resolver", key="btn_exec_flujo_max"):
        try:
            # Crear red de flujo
            flujo = FlujoMaximo(nodos)
            for orig, dest, cap in arcos_list:
                flujo.agregar_arco(orig, dest, cap)

            # Resolver
            resultado = flujo.resolver(origen, destino)
            mostrar_resolucion_flujo_maximo(resultado, nodos, origen, destino)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Ejemplo
    st.write("---")
    ejemplo_flujo_maximo()


def _mostrar_flujo_costo_minimo():
    """Sección de flujo de costo mínimo"""
    st.write("---")
    st.markdown("<h2 class='section-header'>💰 Flujo de Costo Mínimo</h2>",
                unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Red")

        # Entrada de nodos
        nodos_input = st.text_input(
            "Nodos (separados por coma)",
            value="A,B,C,D,E",
            help="Ej: A,B,C,D,E",
            key="flujo_costo_nodos"
        )
        nodos = [n.strip() for n in nodos_input.split(',')]

        # Entrada de arcos
        st.write("**Arcos (uno por línea: origen-destino capacidad costo)**")
        arcos_input = st.text_area(
            "Arcos",
            value="A-B 15 2\nA-C 20 3\nB-D 10 1\nB-E 15 4\nC-D 20 2\nD-E 25 1",
            height=200,
            label_visibility="collapsed",
            key="flujo_costo_arcos"
        )

    with col_input2:
        st.subheader("⚙️ Parámetros")

        origen = st.selectbox(
            "Nodo Origen",
            nodos,
            key="flujo_costo_origen"
        )

        destino = st.selectbox(
            "Nodo Destino",
            nodos,
            key="flujo_costo_destino"
        )

        flujo_requerido = st.number_input(
            "Flujo a Transportar",
            min_value=1.0,
            value=25.0,
            step=1.0,
            key="flujo_costo_cantidad"
        )

    # Procesar arcos
    arcos_list = []
    try:
        for linea in arcos_input.strip().split('\n'):
            if linea.strip():
                partes = linea.strip().split()
                if len(partes) >= 3:
                    nodo_arc = partes[0].split('-')
                    if len(nodo_arc) == 2:
                        arcos_list.append((nodo_arc[0], nodo_arc[1],
                                           float(partes[1]), float(partes[2])))
    except:
        st.error("❌ Error al procesar los arcos. Formato: origen-destino capacidad costo")
        return

    # Botón ejecutar
    if st.button("▶️ Resolver", key="btn_exec_flujo_costo"):
        try:
            # Crear red de flujo
            flujo_costo = FlujoCostoMinimo(nodos)
            for orig, dest, cap, costo in arcos_list:
                flujo_costo.agregar_arco(orig, dest, cap, costo)

            # Resolver
            resultado = flujo_costo.resolver(origen, destino, flujo_requerido)
            mostrar_resolucion_flujo_costo_minimo(resultado, origen, destino, flujo_requerido)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # Ejemplo
    st.write("---")
    ejemplo_flujo_costo_minimo()