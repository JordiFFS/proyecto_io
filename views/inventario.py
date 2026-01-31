# views/inventario.py

"""
Vista para gestión de inventarios
Incluye análisis EOQ, punto de reorden, control de inventarios
"""

import streamlit as st
import pandas as pd
from models.inventarios.inventario_basico import (
    ModeloEOQ,
    PuntoReorden,
    ControlInventario,
    InventarioMateriaPrima
)
from empresa.datos_empresa import MATERIAS_PRIMAS, PARAMETROS_INVENTARIO


def show_inventarios():
    """Vista principal de gestión de inventarios"""

    st.markdown("<h1 class='main-header'>📦 Gestión de Inventarios</h1>", unsafe_allow_html=True)
    st.markdown("*EOQ, Punto de Reorden, Control de Materias Primas Perecederas*")

    # Inicializar session state
    if 'metodo_inv' not in st.session_state:
        st.session_state.metodo_inv = None

    # Selector de método
    st.markdown("<h2 class='section-header'>Selecciona un Método</h2>", unsafe_allow_html=True)

    col_metodos = st.columns(4)

    with col_metodos[0]:
        if st.button("📊 EOQ", use_container_width=True, key="btn_eoq_inv"):
            st.session_state.metodo_inv = 'eoq'
            st.rerun()

    with col_metodos[1]:
        if st.button("🎯 Punto Reorden", use_container_width=True, key="btn_rop_inv"):
            st.session_state.metodo_inv = 'rop'
            st.rerun()

    with col_metodos[2]:
        if st.button("⚠️ Control Inventario", use_container_width=True, key="btn_control_inv"):
            st.session_state.metodo_inv = 'control'
            st.rerun()

    with col_metodos[3]:
        if st.button("☠️ Mat. Perecederas", use_container_width=True, key="btn_perecederas_inv"):
            st.session_state.metodo_inv = 'perecederas'
            st.rerun()

    # Ejecutar según lo seleccionado
    metodo_actual = st.session_state.get('metodo_inv')

    if metodo_actual == 'eoq':
        _mostrar_eoq()
    elif metodo_actual == 'rop':
        _mostrar_punto_reorden()
    elif metodo_actual == 'control':
        _mostrar_control_inventario()
    elif metodo_actual == 'perecederas':
        _mostrar_perecederas()
    else:
        _mostrar_info_general()


def _mostrar_info_general():
    """Muestra información general de inventarios"""
    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Métodos de Gestión de Inventarios</h2>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📊 EOQ (Economic Order Quantity)
        - Cantidad óptima a ordenar
        - Minimiza costo total
        - Balancea costo orden vs. almacén

        ### 🎯 Punto de Reorden (ROP)
        - Cuándo colocar una orden
        - Consideralea lead time
        - Stock de seguridad incluido
        """)

    with col2:
        st.markdown("""
        ### ⚠️ Control de Inventario
        - Monitoreo continuo
        - Alertas de nivel bajo
        - Recomendaciones de acción

        ### ☠️ Materias Primas Perecederas
        - Consideralea vida útil
        - FIFO (First In, First Out)
        - Riesgo de vencimiento
        """)

    # Mostrar materias primas de la empresa
    st.write("---")
    st.markdown("<h2 class='section-header'>📦 Materias Primas Disponibles</h2>",
                unsafe_allow_html=True)

    materias_data = []
    for cod, mp in MATERIAS_PRIMAS.items():
        materias_data.append({
            'Código': cod,
            'Materia Prima': mp['nombre'],
            'Stock Actual': f"{mp['stock_actual']:,.0f}",
            'Stock Mínimo': f"{mp['stock_minimo']:,.0f}",
            'Costo Unitario': f"${mp['costo_unitario']:.3f}",
            'Perecedera': "Sí" if mp['perecedera'] else "No"
        })

    st.dataframe(pd.DataFrame(materias_data), use_container_width=True, hide_index=True)


def _mostrar_eoq():
    """Muestra cálculo de EOQ"""
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Cantidad Económica de Orden (EOQ)</h2>",
                unsafe_allow_html=True)

    st.info("""
    El EOQ es la cantidad que minimiza el costo total de inventario.
    Formula: Q* = √(2*D*S/H)
    - D: Demanda anual
    - S: Costo por orden
    - H: Costo mantener por unidad por año
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Parámetros de Entrada")

        demanda_anual = st.number_input("Demanda Anual", min_value=1, value=3650000)
        costo_orden = st.number_input("Costo por Orden (USD)", min_value=0.01, value=50.0)
        costo_mantener = st.number_input("Costo Mantener/Año (USD)", min_value=0.01, value=0.02)

    with col2:
        st.subheader("Producto Predeterminado")
        producto = st.selectbox("Selecciona una materia prima",
                                list(MATERIAS_PRIMAS.keys()))

        mp = MATERIAS_PRIMAS[producto]
        st.write(f"**{mp['nombre']}**")
        st.write(f"Costo unitario: ${mp['costo_unitario']:.3f}")

    if st.button("▶️ Calcular EOQ", key="btn_calc_eoq"):
        modelo = ModeloEOQ(demanda_anual, costo_orden, costo_mantener)
        resultado = modelo.resolver()

        st.success("✅ EOQ Calculado")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Q* (EOQ)", f"{resultado['Q_estrella']:.0f} unidades")
        with col2:
            st.metric("Órdenes/Año", f"{resultado['num_ordenes']:.2f}")
        with col3:
            st.metric("Días entre Órdenes", f"{resultado['dias_entre_ordenes']:.1f}")
        with col4:
            st.metric("Stock Promedio", f"{resultado['inventario_promedio']:.0f}")

        st.write("---")
        st.markdown("**Costos Anuales**")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Costo Órdenes", f"${resultado['costo_ordenes_anual']:.2f}")
        with col2:
            st.metric("Costo Almacén", f"${resultado['costo_almacen_anual']:.2f}")
        with col3:
            st.metric("Costo Total", f"${resultado['costo_total']:.2f}")


def _mostrar_punto_reorden():
    """Muestra cálculo de punto de reorden"""
    st.write("---")
    st.markdown("<h2 class='section-header'>🎯 Punto de Reorden (ROP)</h2>",
                unsafe_allow_html=True)

    st.info("""
    El ROP indica cuándo colocar una nueva orden.
    Fórmula Simple: ROP = Demanda Diaria × Lead Time
    Con Seguridad: ROP = (d × L) + (Z × σ × √L)
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Parámetros")

        demanda_diaria = st.number_input("Demanda Diaria", min_value=1, value=10000)
        lead_time = st.number_input("Lead Time (días)", min_value=1, value=3)
        nivel_servicio = st.selectbox("Nivel de Servicio (%)",
                                      [85, 90, 95, 99], index=2)
        desv_std = st.number_input("Desviación Estándar (opcional)",
                                   min_value=0, value=1000)

    with col2:
        st.subheader("Información")
        st.write(f"Demanda Lead Time: {demanda_diaria * lead_time:,.0f} unidades")
        st.write(f"Demanda Mensual (30 días): {demanda_diaria * 30:,.0f} unidades")
        st.write(f"Demanda Anual (365 días): {demanda_diaria * 365:,.0f} unidades")

    if st.button("▶️ Calcular ROP", key="btn_calc_rop"):
        modelo = PuntoReorden(demanda_diaria, lead_time, desv_std, nivel_servicio / 100)
        resultado = modelo.resolver()

        st.success("✅ ROP Calculado")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ROP Simple", f"{resultado['rop_simple']:.0f} unidades")
        with col2:
            st.metric("ROP con Seguridad", f"{resultado['rop_con_seguridad']:.0f} unidades")
        with col3:
            st.metric("Stock Seguridad", f"{resultado['stock_seguridad']:.0f} unidades")


def _mostrar_control_inventario():
    """Muestra control de inventario"""
    st.write("---")
    st.markdown("<h2 class='section-header'>⚠️ Control de Inventario</h2>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Parámetros Actuales")

        materia_prima = st.selectbox("Selecciona materia prima",
                                     list(MATERIAS_PRIMAS.keys()),
                                     key="mp_select_control")

        mp = MATERIAS_PRIMAS[materia_prima]

        stock_actual = st.number_input("Stock Actual",
                                       min_value=0,
                                       value=mp['stock_actual'])
        stock_min = st.number_input("Stock Mínimo",
                                    min_value=0,
                                    value=mp['stock_minimo'])
        stock_max = st.number_input("Stock Máximo",
                                    min_value=stock_min,
                                    value=mp['stock_maximo'])

    with col2:
        st.subheader("Información del Producto")
        st.write(f"**{mp['nombre']}**")
        st.write(f"Consumo diario: ~{mp.get('consumo_por_botella', 0)} unidades")
        st.write(f"Costo unitario: ${mp['costo_unitario']:.3f}")

    demanda_diaria = st.number_input("Demanda Diaria", min_value=1, value=10000)

    if st.button("▶️ Analizar Inventario", key="btn_anal_inv"):
        control = ControlInventario(
            stock_actual, stock_min, stock_max,
            demanda_diaria, 0.02, 0.50
        )

        estado = control.evaluar_estado()

        st.success("✅ Análisis Completado")

        # Estado actual
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Estado", estado['estado'])
        with col2:
            st.metric("Acción", estado['accion'])
        with col3:
            st.metric("Días con Stock", f"{estado['dias_con_stock']:.1f}")
        with col4:
            st.metric("Capacidad Usada", f"{estado['capacidad_utilizada']:.1f}%")

        # Recomendación
        st.write("---")
        st.subheader("Recomendación")

        if estado['urgencia'] == 3:
            st.error(f"🚨 {estado['accion']}")
        elif estado['urgencia'] == 2:
            st.warning(f"⚠️ {estado['accion']}")
        else:
            st.info(f"ℹ️ {estado['accion']}")


def _mostrar_perecederas():
    """Muestra análisis de materias primas perecederas"""
    st.write("---")
    st.markdown("<h2 class='section-header'>☠️ Control de Materias Primas Perecederas</h2>",
                unsafe_allow_html=True)

    st.info("""
    Las materias primas perecederas requieren especial atención.
    Se utilizarán políticas FIFO para minimizar pérdidas.
    """)

    # Seleccionar materia prima perecedera
    perecederas = {cod: mp for cod, mp in MATERIAS_PRIMAS.items() if mp['perecedera']}

    if not perecederas:
        st.warning("No hay materias primas perecederas configuradas")
        return

    materia_prima = st.selectbox("Selecciona materia prima perecedera",
                                 list(perecederas.keys()))

    mp = perecederas[materia_prima]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Información Actual")
        st.write(f"**{mp['nombre']}**")
        st.write(f"Stock actual: {mp['stock_actual']:,.0f} {mp['unidad']}")
        st.write(f"Vida útil: {mp['vida_util_dias']} días")
        st.write(f"Costo unitario: ${mp['costo_unitario']:.3f}")

    with col2:
        st.subheader("Parámetros de Análisis")

        dias_almacenados = st.slider("Días almacenados",
                                     min_value=0,
                                     max_value=mp['vida_util_dias'],
                                     value=mp['vida_util_dias'] // 2)

        demanda_diaria = st.number_input("Demanda diaria",
                                         min_value=1,
                                         value=1000)

    if st.button("▶️ Analizar Perecederas", key="btn_anal_perecederas"):
        inv = InventarioMateriaPrima(
            mp['nombre'],
            mp['stock_actual'],
            mp['stock_minimo'],
            mp['stock_maximo'],
            mp['vida_util_dias'],
            mp['costo_unitario'],
            0.02,
            demanda_diaria,
            es_perecedera=True
        )

        riesgo = inv.calcular_riesgo_vencimiento(dias_almacenados)
        recomendaciones = inv.recomendar_acciones()

        st.success("✅ Análisis Completado")

        # Información de riesgo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Días Restantes", f"{riesgo['dias_restantes']:.0f}")
        with col2:
            st.metric("Riesgo de Vencimiento", f"{riesgo['porcentaje_riesgo']:.1f}%")
        with col3:
            st.metric("Cantidad en Riesgo", f"{riesgo['cantidad_en_riesgo']:.0f}")

        # Recomendaciones
        st.write("---")
        st.subheader("Recomendaciones")

        for i, rec in enumerate(recomendaciones, 1):
            if "URGENTE" in rec or "Riesgo" in rec:
                st.error(f"{i}. {rec}")
            elif "FIFO" in rec or "Preparar" in rec:
                st.warning(f"{i}. {rec}")
            else:
                st.info(f"{i}. {rec}")