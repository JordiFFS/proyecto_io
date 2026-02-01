"""
views/transporte.py
Vista principal para Problemas de Transporte adaptada a Coca-Cola
"""

import streamlit as st
from views.resolucion_esquina_noroeste import mostrar_resolucion_esquina_noroeste, ejemplo_esquina_noroeste
from views.resolucion_costo_minimo_transporte import mostrar_resolucion_costo_minimo_transporte, \
    ejemplo_costo_minimo_transporte
from views.resolucion_vogel import mostrar_resolucion_vogel, ejemplo_vogel
from views.resolucion_optimalidad import mostrar_resolucion_optimalidad, ejemplo_optimalidad_transporte

from models.transporte.esquina_noroeste import EsquinaNoreste
from models.transporte.costo_minimo import CostoMinimo
from models.transporte.vogel import MetodoVogel
from empresa.datos_empresa import (
    PLANTAS, CENTROS_DISTRIBUCION, COSTOS_TRANSPORTE_DISTRIBUCION,
    PUNTOS_VENTA, COSTOS_TRANSPORTE_VENTA
)


def show_transporte():
    """Vista principal para problemas de transporte"""

    st.markdown("<h1 class='main-header'>🚚 Problema de Transporte</h1>", unsafe_allow_html=True)
    st.markdown("*Métodos de Solución Inicial y Optimización - Esquina Noroeste, Costo Mínimo, Vogel, MODI*")

    # Inicializar metodo_transp si no existe
    if 'metodo_transp' not in st.session_state:
        st.session_state.metodo_transp = None

    # Selector de método
    st.markdown("<h2 class='section-header'>Selecciona un Método</h2>", unsafe_allow_html=True)

    col_metodos = st.columns(4)

    with col_metodos[0]:
        if st.button("📍 Esquina Noroeste", use_container_width=True, key="btn_esquina_noroeste_main"):
            st.session_state.metodo_transp = 'esquina'
            st.rerun()

    with col_metodos[1]:
        if st.button("💰 Costo Mínimo", use_container_width=True, key="btn_costo_minimo_transp_main"):
            st.session_state.metodo_transp = 'costo'
            st.rerun()

    with col_metodos[2]:
        if st.button("🎯 Vogel (VAM)", use_container_width=True, key="btn_vogel_transp_main"):
            st.session_state.metodo_transp = 'vogel'
            st.rerun()

    with col_metodos[3]:
        if st.button("✨ Optimizar (MODI)", use_container_width=True, key="btn_optimizar_transp_main"):
            st.session_state.metodo_transp = 'optimizar'
            st.rerun()

    # Ejecutar según lo seleccionado
    metodo_actual = st.session_state.get('metodo_transp')

    if metodo_actual == 'esquina':
        _mostrar_esquina_noroeste()

    elif metodo_actual == 'costo':
        _mostrar_costo_minimo()

    elif metodo_actual == 'vogel':
        _mostrar_vogel()

    elif metodo_actual == 'optimizar':
        _mostrar_optimizar()

    else:
        # Mostrar información general
        st.write("---")
        st.markdown("<h2 class='section-header'>📚 Métodos Disponibles</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 📍 Esquina Noroeste
            - **Algoritmo:** Inicia en esquina superior izquierda
            - **Ventaja:** Simple de aplicar
            - **Desventaja:** No considera costos
            - **Uso:** Solución inicial rápida

            ### 💰 Costo Mínimo
            - **Algoritmo:** Asigna al costo más bajo disponible
            - **Ventaja:** Mejor que esquina noroeste
            - **Desventaja:** Más lenta que esquina noroeste
            - **Uso:** Solución inicial mejorada
            """)

        with col2:
            st.markdown("""
            ### 🎯 Vogel (VAM)
            - **Algoritmo:** Usa penalizaciones entre costos
            - **Ventaja:** Generalmente da mejor solución
            - **Desventaja:** Más complejo de aplicar
            - **Uso:** Solución inicial de alta calidad

            ### ✨ Optimización (MODI)
            - **Algoritmo:** MODI + Stepping Stone
            - **Función:** Mejora solución inicial
            - **Criterio:** Hasta alcanzar optimidad
            - **Uso:** Solución óptima final
            """)


def _mostrar_esquina_noroeste():
    """Sección de Esquina Noroeste"""
    st.write("---")
    st.markdown("<h2 class='section-header'>📍 Esquina Noroeste</h2>", unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Problema")

        st.write("**Oferta (una por línea)**")
        oferta_input = st.text_area("Oferta", value="100\n150\n120", height=100,
                                    label_visibility="collapsed", key="esquina_oferta_area")

        st.write("**Demanda (una por línea)**")
        demanda_input = st.text_area("Demanda", value="80\n70\n90\n60", height=100,
                                     label_visibility="collapsed", key="esquina_demanda_area")

    with col_input2:
        st.subheader("💰 Costos Unitarios")
        st.write("**Fila por fila, separados por espacios/comas**")

        costos_input = st.text_area(
            "Costos",
            value="4 6 8 6\n5 4 7 5\n6 5 4 6",
            height=150,
            label_visibility="collapsed",
            key="esquina_costos_area"
        )

    # Procesar datos
    try:
        oferta = [int(x.strip()) for x in oferta_input.strip().split('\n') if x.strip()]
        demanda = [int(x.strip()) for x in demanda_input.strip().split('\n') if x.strip()]

        costos = []
        for linea in costos_input.strip().split('\n'):
            if linea.strip():
                fila = [float(x.strip()) for x in linea.replace(',', ' ').split()]
                costos.append(fila)

        if len(oferta) != len(costos) or len(demanda) != len(costos[0]):
            st.error("❌ Dimensiones inconsistentes")
            return

    except Exception as e:
        st.error(f"❌ Error al procesar datos: {str(e)}")
        return

    # Botón ejecutar
    if st.button("▶️ Resolver Esquina Noroeste", key="btn_exec_esquina_metodo"):
        # Generar nombres de orígenes y destinos
        orígenes = [f"O{i+1}" for i in range(len(oferta))]
        destinos = [f"D{j+1}" for j in range(len(demanda))]
        mostrar_resolucion_esquina_noroeste(costos, oferta, demanda, orígenes, destinos)

    # Ejemplo
    st.write("---")
    ejemplo_esquina_noroeste()


def _mostrar_costo_minimo():
    """Sección de Costo Mínimo"""
    st.write("---")
    st.markdown("<h2 class='section-header'>💰 Costo Mínimo</h2>", unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Problema")

        st.write("**Oferta (una por línea)**")
        oferta_input = st.text_area("Oferta", value="100\n150\n120", height=100,
                                    label_visibility="collapsed", key="costo_oferta_area")

        st.write("**Demanda (una por línea)**")
        demanda_input = st.text_area("Demanda", value="80\n70\n90\n60", height=100,
                                     label_visibility="collapsed", key="costo_demanda_area")

    with col_input2:
        st.subheader("💰 Costos Unitarios")
        st.write("**Fila por fila, separados por espacios/comas**")

        costos_input = st.text_area(
            "Costos",
            value="4 6 8 6\n5 4 7 5\n6 5 4 6",
            height=150,
            label_visibility="collapsed",
            key="costo_costos_area"
        )

    try:
        oferta = [int(x.strip()) for x in oferta_input.strip().split('\n') if x.strip()]
        demanda = [int(x.strip()) for x in demanda_input.strip().split('\n') if x.strip()]

        costos = []
        for linea in costos_input.strip().split('\n'):
            if linea.strip():
                fila = [float(x.strip()) for x in linea.replace(',', ' ').split()]
                costos.append(fila)

    except Exception as e:
        st.error(f"❌ Error al procesar datos: {str(e)}")
        return

    if st.button("▶️ Resolver Costo Mínimo", key="btn_exec_costo_minimo_metodo"):
        # Generar nombres de orígenes y destinos
        orígenes = [f"O{i+1}" for i in range(len(oferta))]
        destinos = [f"D{j+1}" for j in range(len(demanda))]
        mostrar_resolucion_costo_minimo_transporte(costos, oferta, demanda, orígenes, destinos)

    st.write("---")
    ejemplo_costo_minimo_transporte()


def _mostrar_vogel():
    """Sección de Vogel"""
    st.write("---")
    st.markdown("<h2 class='section-header'>🎯 Método de Vogel (VAM)</h2>", unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Problema")

        st.write("**Oferta (una por línea)**")
        oferta_input = st.text_area("Oferta", value="100\n150\n120", height=100,
                                    label_visibility="collapsed", key="vogel_oferta_area")

        st.write("**Demanda (una por línea)**")
        demanda_input = st.text_area("Demanda", value="80\n70\n90\n60", height=100,
                                     label_visibility="collapsed", key="vogel_demanda_area")

    with col_input2:
        st.subheader("💰 Costos Unitarios")
        st.write("**Fila por fila, separados por espacios/comas**")

        costos_input = st.text_area(
            "Costos",
            value="4 6 8 6\n5 4 7 5\n6 5 4 6",
            height=150,
            label_visibility="collapsed",
            key="vogel_costos_area"
        )

    try:
        oferta = [int(x.strip()) for x in oferta_input.strip().split('\n') if x.strip()]
        demanda = [int(x.strip()) for x in demanda_input.strip().split('\n') if x.strip()]

        costos = []
        for linea in costos_input.strip().split('\n'):
            if linea.strip():
                fila = [float(x.strip()) for x in linea.replace(',', ' ').split()]
                costos.append(fila)

    except Exception as e:
        st.error(f"❌ Error al procesar datos: {str(e)}")
        return

    if st.button("▶️ Resolver Vogel", key="btn_exec_vogel_metodo"):
        # Generar nombres de orígenes y destinos
        orígenes = [f"O{i+1}" for i in range(len(oferta))]
        destinos = [f"D{j+1}" for j in range(len(demanda))]
        mostrar_resolucion_vogel(costos, oferta, demanda, orígenes, destinos)

    st.write("---")
    ejemplo_vogel()


def _mostrar_optimizar():
    """Sección de Optimización MODI"""
    st.write("---")
    st.markdown("<h2 class='section-header'>✨ Optimización (MODI + Stepping Stone)</h2>",
                unsafe_allow_html=True)

    st.info("""
    Este módulo optimiza una solución inicial usando el método MODI.
    Primero genera la solución inicial con un método elegido, luego la optimiza.
    """)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("📝 Definir Problema")

        st.write("**Oferta (una por línea)**")
        oferta_input = st.text_area("Oferta", value="100\n150\n120", height=100,
                                    label_visibility="collapsed", key="opt_oferta_area")

        st.write("**Demanda (una por línea)**")
        demanda_input = st.text_area("Demanda", value="80\n70\n90\n60", height=100,
                                     label_visibility="collapsed", key="opt_demanda_area")

    with col_input2:
        st.subheader("⚙️ Configuración")

        st.write("**Costos Unitarios**")
        costos_input = st.text_area(
            "Costos",
            value="4 6 8 6\n5 4 7 5\n6 5 4 6",
            height=130,
            label_visibility="collapsed",
            key="opt_costos_area"
        )

        metodo_inicial = st.selectbox(
            "Método para solución inicial",
            ["Esquina Noroeste", "Costo Mínimo", "Vogel"],
            key="opt_metodo_selectbox"
        )

    try:
        oferta = [int(x.strip()) for x in oferta_input.strip().split('\n') if x.strip()]
        demanda = [int(x.strip()) for x in demanda_input.strip().split('\n') if x.strip()]

        costos = []
        for linea in costos_input.strip().split('\n'):
            if linea.strip():
                fila = [float(x.strip()) for x in linea.replace(',', ' ').split()]
                costos.append(fila)

    except Exception as e:
        st.error(f"❌ Error al procesar datos: {str(e)}")
        return

    if st.button("▶️ Resolver y Optimizar", key="btn_exec_optimizar_metodo_final"):
        # Generar nombres de orígenes y destinos
        orígenes = [f"O{i+1}" for i in range(len(oferta))]
        destinos = [f"D{j+1}" for j in range(len(demanda))]

        # Generar solución inicial según método seleccionado
        if metodo_inicial == "Esquina Noroeste":
            metodo = EsquinaNoreste(costos, oferta, demanda)
            nombre = "Esquina Noroeste"
            resultado = metodo.resolver()
            solucion_inicial = resultado['asignacion']

        elif metodo_inicial == "Costo Mínimo":
            metodo = CostoMinimo(costos, oferta, demanda)
            nombre = "Costo Mínimo"
            resultado = metodo.resolver()
            solucion_inicial = resultado['asignacion']

        else:  # Vogel
            metodo = MetodoVogel(costos, oferta, demanda)
            nombre = "Vogel (VAM)"
            solucion_inicial = metodo.resolver()

        # Optimizar
        mostrar_resolucion_optimalidad(costos, oferta, demanda, solucion_inicial, nombre, orígenes, destinos)

    st.write("---")
    ejemplo_optimalidad_transporte()