# views/resolucion_simplex.py
import streamlit as st
import pandas as pd
from models.programacion_lineal.simplex import Simplex
from models.programacion_lineal.gran_m import GranM
from models.programacion_lineal.dos_fases import DosFases
from models.programacion_lineal.dual import Dual
from gemini import generar_analisis_gemini
from huggingface_analisis_pl import generar_analisis_huggingface
from ollama_analisis_pl import generar_analisis_ollama, verificar_ollama_disponible
from views.resolucion_gran_m import mostrar_resolucion_gran_m


def mostrar_resolucion_simplex(resultado, tabla_final, nombres, A, b, signos, n_vars, n_rest, tipo_opt, metodo_usado):
    """
    Muestra la resolución completa del Simplex con todos los pasos detallados
    """

    estado = resultado.get('estado', 'Desconocido')
    es_no_acotado = resultado.get('es_no_acotado', False)
    es_infactible = resultado.get('es_infactible', False)

    if resultado['exito']:
        st.success("✅ Solución Óptima Encontrada")
    elif es_no_acotado:
        st.warning("⚠️ Problema No Acotado")
    elif es_infactible:
        st.error("❌ Problema Infactible")
    else:
        st.error("❌ Error en la resolución")

    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Variables de Decisión", n_vars)
    with col2:
        st.metric("📏 Restricciones", n_rest)
    with col3:
        st.metric("📝 Variables de Holgura", n_rest)
    with col4:
        st.metric("🔄 Total de Variables", n_vars + n_rest)

    # TABLA INICIAL
    st.write("---")
    st.markdown("<h2 class='section-header'>📍 Tabla Inicial (Iteración 0)</h2>", unsafe_allow_html=True)

    st.info(
        "Esta es la tabla inicial del método Simplex. Las variables en la base inicial son las variables de holgura.")
    if 'historial_tablas' in resultado and len(resultado['historial_tablas']) > 0:
        tabla_inicial = resultado['historial_tablas'][0]['tabla']
        st.dataframe(tabla_inicial, use_container_width=True)

    # INFORMACIÓN DEL MÉTODO
    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Información del Método Simplex</h2>", unsafe_allow_html=True)
    st.info("""
    **Algoritmo del Método Simplex:**
    1. Construir tabla inicial con variables de holgura
    2. Verificar optimalidad: si todos los costos reducidos ≥ 0, solución óptima
    3. Si no es óptima, seleccionar variable que entra (coeficiente más negativo)
    4. Seleccionar variable que sale (razón mínima)
    5. Pivotear: operaciones de fila para cambiar base
    6. Repetir hasta optimalidad
    """)

    # ITERACIONES DETALLADAS
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Método Simplex</h2>", unsafe_allow_html=True)

    if resultado['iteraciones'] > 0 and 'historial_tablas' in resultado:
        tab_list = [f"Iter. {i + 1}" for i in range(resultado['iteraciones'])]
        tabs_iter = st.tabs(tab_list)

        for iter_num, tab in enumerate(tabs_iter, 1):
            with tab:
                if iter_num <= len(resultado['historial_tablas']) - 1:
                    iter_info = resultado['historial_tablas'][iter_num]

                    st.markdown(
                        f"<div class='iteration-header'><h3>Iteración {iter_num} - Detalles Completos</h3></div>",
                        unsafe_allow_html=True)

                    # Información del pivoteo
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(
                            f"<div class='metric-box'><strong>Variable que ENTRA:</strong><br>{iter_info.get('variable_entra', 'N/A')}</div>",
                            unsafe_allow_html=True)
                    with col2:
                        st.markdown(
                            f"<div class='metric-box'><strong>Variable que SALE:</strong><br>{iter_info.get('variable_sale', 'N/A')}</div>",
                            unsafe_allow_html=True)
                    with col3:
                        st.markdown(
                            f"<div class='metric-box'><strong>Elemento Pivote:</strong><br>{iter_info.get('elemento_pivote', 'N/A'):.6f}</div>",
                            unsafe_allow_html=True)

                    st.write("")

                    # PASO 1: ANÁLISIS DE OPTIMALIDAD Y SELECCIÓN DE VARIABLE QUE ENTRA
                    st.subheader("1️⃣ Selección de Variable que Entra (Regla de Dantzig)")

                    # Obtener detalles de selección de pivote del historial de pasos
                    pasos_relevantes = [p for p in resultado['historial_pasos']
                                        if p.get('iteracion') == iter_num and p.get('tipo') == 'seleccion_pivote']

                    if pasos_relevantes:
                        paso = pasos_relevantes[0]
                        contenido = paso.get('contenido', {})

                        st.write("**Fila de Costos Reducidos (última fila de la tabla anterior):**")
                        fila_costo = contenido.get('fila_costo', {})

                        costos_df_data = []
                        for var_name, valor in fila_costo.items():
                            costos_df_data.append({
                                'Variable': var_name,
                                'Costo Reducido': f"{valor:.6f}",
                                'Estado': '❌ Negativo (entra)' if valor < -1e-10 else '✓ No negativo'
                            })

                        costos_df = pd.DataFrame(costos_df_data)
                        st.dataframe(costos_df, use_container_width=True, hide_index=True)

                        st.write(f"**Variable Seleccionada:** {contenido.get('variable_entra', 'N/A')}")
                        st.write(f"**Razón:** Coeficiente más negativo = {contenido.get('coeficiente_costo', 0):.6f}")

                    # PASO 2: CÁLCULO DE RAZONES MÍNIMAS
                    st.subheader("2️⃣ Cálculo de Razones Mínimas (Método de Razones)")

                    pasos_razon = [p for p in resultado['historial_pasos']
                                   if p.get('iteracion') == iter_num and p.get('tipo') == 'seleccion_pivote']

                    if pasos_razon:
                        paso = pasos_razon[0]
                        razones = paso.get('contenido', {}).get('razones_minimas', [])

                        if razones:
                            st.write("**Cálculo de razones para cada fila:**")
                            razones_df_data = []
                            for raz in razones:
                                razones_df_data.append({
                                    'Fila': raz.get('fila', 0) + 1,
                                    'Var. Básica': raz.get('variable_basica', 'N/A'),
                                    'b_i': f"{raz.get('b_i', 0):.6f}",
                                    'a_ij': f"{raz.get('a_ij', 0):.6f}",
                                    'Razón (b_i/a_ij)': f"{raz.get('razon', 0):.6f}",
                                    'Mínima': '🔴 SÍ' if raz.get('es_minima', False) else ''
                                })

                            razones_df = pd.DataFrame(razones_df_data)
                            st.dataframe(razones_df, use_container_width=True, hide_index=True)

                            st.write(f"**Variable que Sale:** {paso.get('contenido', {}).get('variable_sale', 'N/A')}")
                            st.write(f"**Razón:** Razón mínima entre todas las filas")

                    # TABLA ANTES DEL PIVOTEO
                    st.write("")
                    st.subheader("3️⃣ Tabla ANTES del Pivoteo")
                    if iter_num > 1:
                        tabla_anterior = resultado['historial_tablas'][iter_num - 1]['tabla']
                    else:
                        tabla_anterior = resultado['historial_tablas'][0]['tabla']
                    st.dataframe(tabla_anterior, use_container_width=True)

                    # OPERACIONES DE PIVOTEO
                    st.write("")
                    st.subheader("4️⃣ Operaciones de Pivoteo (Eliminación Gaussiana)")

                    pasos_pivoteo = [p for p in resultado['historial_pasos']
                                     if p.get('numero') == iter_num and p.get('tipo') == 'pivoteo']

                    if pasos_pivoteo:
                        paso = pasos_pivoteo[0]
                        contenido = paso.get('contenido', {})

                        st.write(f"**Posición del Pivote:** {contenido.get('posicion_pivote', 'N/A')}")
                        st.write(f"**Elemento Pivote:** {contenido.get('elemento_pivote', 'N/A'):.6f}")

                        pasos_calculo = contenido.get('pasos_calculo', [])

                        if pasos_calculo:
                            with st.expander("📖 Ver detalles de cálculos de pivoteo", expanded=False):
                                for i, paso_calc in enumerate(pasos_calculo, 1):
                                    st.markdown(f"**Paso {i}: {paso_calc.get('paso', 'N/A')}**")
                                    st.write(f"Descripción: {paso_calc.get('descripcion', 'N/A')}")

                                    tabla_estado = paso_calc.get('tabla_estado')
                                    if tabla_estado is not None:
                                        tabla_df = pd.DataFrame(tabla_estado)
                                        st.write("Tabla después de este paso:")
                                        st.dataframe(tabla_df, use_container_width=True)

                    # TABLA DESPUÉS DEL PIVOTEO
                    st.write("")
                    st.subheader("5️⃣ Tabla DESPUÉS del Pivoteo")
                    st.dataframe(iter_info['tabla'], use_container_width=True)

                    # INFORMACIÓN DE LA ITERACIÓN
                    st.write("")
                    st.subheader("📈 Resumen de la Iteración")

                    pasos_pivoteo = [p for p in resultado['historial_pasos']
                                     if p.get('numero') == iter_num and p.get('tipo') == 'pivoteo']

                    if pasos_pivoteo:
                        paso = pasos_pivoteo[0]
                        contenido = paso.get('contenido', {})

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Variable Entra:** {contenido.get('variable_entra', 'N/A')}")
                            st.write(f"**Variable Sale:** {contenido.get('variable_sale', 'N/A')}")
                            st.write(f"**Posición Pivote:** {contenido.get('posicion_pivote', 'N/A')}")

                        with col2:
                            valor_z = contenido.get('valor_z_actual', 0)
                            st.metric("Valor Z Actual", f"{valor_z:.6f}")
                            st.write(f"**Base Actualizada:** {', '.join([str(b) for b in iter_info.get('base', [])])}")

    else:
        st.success("✅ La solución óptima se encontró en la iteración inicial (tabla ya es óptima).")

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA FINAL</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Valor Óptimo (Z)", f"${resultado['valor_optimo']:.2f}")
    with col2:
        st.metric("🔄 Iteraciones", resultado['iteraciones'])
    with col3:
        st.metric("📍 Variables Básicas", len([x for x in resultado.get('base_final', []) if x.startswith('x')]))
    with col4:
        st.metric("📦 Variables de Holgura", len([x for x in resultado.get('base_final', []) if x.startswith('s')]))

    st.subheader("✅ Variables de Decisión Óptimas")
    var_data = []
    for var in nombres:
        valor = resultado['solucion_variables'].get(var, 0)
        var_data.append({
            'Variable': var,
            'Valor Óptimo': f"{valor:.6f}",
            'Tipo': 'Básica' if valor > 1e-6 else 'No Básica'
        })

    var_df = pd.DataFrame(var_data)
    st.dataframe(var_df, use_container_width=True, hide_index=True)

    if 'solucion_holguras' in resultado:
        st.subheader("📦 Variables de Holgura")
        holgura_data = []
        for s, valor in resultado['solucion_holguras'].items():
            holgura_data.append({
                'Variable de Holgura': s,
                'Valor': f"{valor:.6f}",
                'Restricción': 'Activa' if valor < 1e-6 else 'Inactiva'
            })

        holgura_df = pd.DataFrame(holgura_data)
        st.dataframe(holgura_df, use_container_width=True, hide_index=True)

    st.subheader("📊 Tabla Final del Simplex")
    st.dataframe(tabla_final, use_container_width=True)

    st.subheader("✔️ Verificación de Restricciones")
    st.write("Se verifica que la solución satisface todas las restricciones:")

    verif = []
    for i in range(len(A)):
        suma = sum(A[i][j] * resultado['solucion_variables'][nombres[j]] for j in range(n_vars))
        op = signos[i]
        rhs = b[i]

        if op == "<=":
            cumple = suma <= rhs + 1e-4
        elif op == ">=":
            cumple = suma >= rhs - 1e-4
        else:
            cumple = abs(suma - rhs) <= 1e-4

        verif.append({
            'Restricción': f'R{i + 1}',
            'LHS (izquierda)': f"{suma:.6f}",
            'Operador': op,
            'RHS (derecha)': f"{rhs:.6f}",
            'Cumple': "✓" if cumple else "✗"
        })

    verif_df = pd.DataFrame(verif)
    st.dataframe(verif_df, use_container_width=True, hide_index=True)

    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema Resuelto:**
        - Tipo: {tipo_opt}
        - Variables: {n_vars}
        - Restricciones: {n_rest}
        - Iteraciones: {resultado['iteraciones']}
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Valor Óptimo Z = {resultado['valor_optimo']:.6f}
        - Variables Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('x')])}
        - Variables No Básicas: {', '.join([x for x in resultado.get('base_final', []) if x.startswith('s')])}
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
                origen=f"Simplex {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(n_vars)],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
            )
        except Exception as e:
            analisis_data['gemini'] = f"❌ Error: {str(e)}"

    with st.spinner("🧠 Generando análisis con Hugging Face..."):
        try:
            analisis_data['huggingface'] = generar_analisis_huggingface(
                origen=f"Simplex {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(n_vars)],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
            )
        except Exception as e:
            analisis_data['huggingface'] = f"❌ Error: {str(e)}"

    with st.spinner("💻 Generando análisis con Ollama..."):
        try:
            analisis_data['ollama'] = generar_analisis_ollama(
                origen=f"Simplex {tipo_opt}",
                rutas=[{"destino": nombres[i], "distancia": resultado['solucion_variables'].get(nombres[i], 0),
                        "ruta": nombres[i]} for i in range(n_vars)],
                iteraciones=resultado['iteraciones'],
                total_nodos=n_vars + n_rest
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


def mostrar_ejemplos(metodo):
    """
    Muestra ejemplos según el método seleccionado
    """

    if metodo == "simplex":
        st.subheader("Ejemplo Simplex - Planificación de Producción Coca-Cola")
        st.write("""
        **Problema:** Maximizar ganancias de producción respetando capacidades de plantas y demanda

        **Variables:**
        - x₁ = Botellas Coca-Cola a producir
        - x₂ = Botellas Sprite a producir
        - x₃ = Botellas Fanta a producir

        **Función Objetivo:**
        Maximizar: 0.65x₁ + 0.60x₂ + 0.60x₃ (ganancias en $)

        **Restricciones:**
        - Capacidad Planta Quito: x₁ + x₂ + x₃ ≤ 1,500,000
        - Capacidad Planta Guayaquil: x₁ + x₂ + x₃ ≤ 1,350,000
        - Capacidad Planta Cuenca: x₁ + x₂ + x₃ ≤ 900,000
        - Demanda Coca-Cola: x₁ ≤ 450,000
        - Demanda Sprite: x₂ ≤ 300,000
        - Demanda Fanta: x₃ ≤ 360,000
        """)

        if st.button("Ejecutar", key="ej_simplex"):
            c = [0.65, 0.60, 0.60]
            A = [
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
            b = [1500000, 1350000, 900000, 450000, 300000, 360000]
            signos = ["<=", "<=", "<=", ">=", ">=", ">="]

            simplex = Simplex(c, A, b, tipo="max",
                              nombres_vars=["Coca-Cola", "Sprite", "Fanta"])
            resultado = simplex.resolver(verbose=False)

            if resultado['exito']:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Coca-Cola", f"{resultado['solucion_variables']['Coca-Cola']:,.0f} botellas")
                with col2:
                    st.metric("Sprite", f"{resultado['solucion_variables']['Sprite']:,.0f} botellas")
                with col3:
                    st.metric("Fanta", f"{resultado['solucion_variables']['Fanta']:,.0f} botellas")

                st.metric("💰 Ganancia Máxima", f"${resultado['valor_optimo']:,.2f}")

                st.dataframe(simplex.obtener_tabla_pandas(), use_container_width=True)

                st.write("---")
                mostrar_resolucion_simplex(
                    resultado,
                    simplex.obtener_tabla_pandas(),
                    ["Coca-Cola", "Sprite", "Fanta"],
                    A,
                    b,
                    signos,
                    3,
                    6,
                    "Maximización",
                    "Simplex"
                )

    elif metodo == "gran_m":
        st.subheader("📊 Ejemplo: Minimización de Costos - Método Gran M")
        st.write("""
        **Problema:** Minimizar costos de distribución desde plantas a centros de distribución.

        **Variables:**
        - x₁ = Botellas desde Planta Quito a Centro Quito
        - x₂ = Botellas desde Planta Quito a Centro Guayaquil
        - x₃ = Botellas desde Planta Guayaquil a Centro Cuenca

        **Función Objetivo:**
        Minimizar: 0.05x₁ + 0.15x₂ + 0.12x₃

        **Restricciones:**
        - Capacidad Planta Quito: x₁ + x₂ ≤ 1,500,000
        - Capacidad Planta Guayaquil: x₃ ≥ 0
        - Demanda Centro Quito: x₁ ≥ 300,000
        - Demanda Centro Guayaquil: x₂ ≥ 200,000
        - Demanda Centro Cuenca: x₃ ≤ 500,000
        """)
        if st.button("Ejecutar Ejemplo Gran M", key="ej_granm"):
            c = [0.05, 0.15, 0.12]
            A = [
                [1, 1, 0],
                [0, 0, 1],
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
            b = [1500000, 0, 300000, 200000, 500000]
            signos = ["<=", ">=", ">=", ">=", "<="]
            gran_m = GranM(
                c, A, b, signos,
                tipo="min",
                nombres_vars=["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"]
            )

            resultado = gran_m.resolver(verbose=False)

            if resultado['exito']:
                st.success("✅ Solución óptima encontrada")
                mostrar_resolucion_gran_m(
                    resultado,
                    ["Quito→Quito", "Quito→Guayaquil", "Guayaquil→Cuenca"],
                    3, 5, "Minimización"
                )
            elif resultado['es_infactible']:
                st.error("❌ Problema Infactible - No existe solución que satisfaga todas las restricciones")
            elif resultado['es_no_acotado']:
                st.warning("⚠️ Problema No Acotado - La solución puede mejorar indefinidamente")
            else:
                st.error("❌ Error en la resolución")

    elif metodo == "dos_fases":
        st.subheader("Ejemplo Dos Fases")
        st.write("min: 2x₁ + 3x₂")
        st.write("s.a: x₁ + x₂ ≥ 5")
        st.write("     x₁ ≥ 2")
        st.write("     x₂ ≥ 1")

        if st.button("Ejecutar", key="ej_dosfases"):
            dos_fases = DosFases([2, 3], [[1, 1], [1, 0], [0, 1]], [5, 2, 1], [">=", ">=", ">="], tipo="min",
                                 nombres_vars=["x1", "x2"])
            resultado = dos_fases.resolver(verbose=False)

            st.metric("Z", f"{resultado['valor_optimo']:.4f}")
            st.metric("x₁", f"{resultado['solucion_variables']['x1']:.4f}")
            st.metric("x₂", f"{resultado['solucion_variables']['x2']:.4f}")

            st.dataframe(dos_fases.obtener_tabla_fase2_pandas(), use_container_width=True)

    elif metodo == "dual":
        st.subheader("Ejemplo Dualidad")
        st.write("**PRIMAL:**")
        st.write("max: 3x₁ + 2x₂")
        st.write("s.a: x₁ + x₂ ≤ 10")
        st.write("     2x₁ + x₂ ≤ 15")

        st.write("**DUAL:**")
        st.write("min: 10y₁ + 15y₂")
        st.write("s.a: y₁ + 2y₂ ≥ 3")
        st.write("     y₁ + y₂ ≥ 2")

        if st.button("Ejecutar", key="ej_dual"):
            dual = Dual([3, 2], [[1, 1], [2, 1]], [10, 15], signos=["<=", "<="], tipo="max",
                        nombres_vars=["x1", "x2"])
            resultado = dual.resolver(verbose=False)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Solución Primal**")
                st.metric("Z Primal", f"{resultado['primal']['valor_optimo']:.4f}")
                st.metric("x₁", f"{resultado['primal']['solucion']['x1']:.4f}")
                st.metric("x₂", f"{resultado['primal']['solucion']['x2']:.4f}")

            with col2:
                st.markdown("**Solución Dual**")
                st.metric("Z Dual", f"{resultado['dual']['valor_optimo']:.4f}")
                st.metric("y₁", f"{resultado['dual']['solucion']['y1']:.4f}")
                st.metric("y₂", f"{resultado['dual']['solucion']['y2']:.4f}")

            st.write("---")
            if resultado['dualidad_fuerte']:
                st.markdown("<div class='success-box'><strong>✓ DUALIDAD FUERTE VERIFICADA</strong></div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div class='warning-box'><strong>⚠️ Dualidad no completamente verificada</strong></div>",
                            unsafe_allow_html=True)