# views/resolucion_simplex.py

import streamlit as st
import pandas as pd
from models.programacion_lineal.simplex import Simplex
from models.programacion_lineal.gran_m import GranM
from models.programacion_lineal.dos_fases import DosFases
from models.programacion_lineal.dual import Dual


def mostrar_resolucion_simplex(resultado, tabla_final, nombres, A, b, signos, n_vars, n_rest, tipo_opt, metodo_usado):
    """
    Muestra la resolución completa del Simplex con todos los pasos

    Args:
        resultado: Diccionario con los resultados del Simplex
        tabla_final: DataFrame con la tabla final
        nombres: Lista con nombres de variables
        A: Matriz de coeficientes de restricciones
        b: Vector de lado derecho
        signos: Lista de operadores de restricciones
        n_vars: Número de variables
        n_rest: Número de restricciones
        tipo_opt: Tipo de optimización (Maximizar/Minimizar)
        metodo_usado: Nombre del método utilizado
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

    # MOSTRAR CONFIGURACIÓN DEL PROBLEMA
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
        st.dataframe(resultado['historial_tablas'][0]['tabla'], use_container_width=True)

    # DETALLES DE CADA ITERACIÓN
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

                    # TABLA ANTERIOR
                    st.subheader("📊 Tabla ANTES del Pivoteo")
                    if iter_num > 1:
                        tabla_anterior = resultado['historial_tablas'][iter_num - 1]['tabla']
                    else:
                        tabla_anterior = resultado['historial_tablas'][0]['tabla']
                    st.dataframe(tabla_anterior, use_container_width=True)

                    # TABLA DESPUÉS
                    st.subheader("📊 Tabla DESPUÉS del Pivoteo")
                    st.dataframe(iter_info['tabla'], use_container_width=True)

                    # INFORMACIÓN ADICIONAL
                    st.subheader("📈 Información de la Iteración")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Posición del Pivote:** {iter_info.get('posicion_pivote', 'N/A')}")
                    with col2:
                        if 'historial_pasos' in resultado and len(resultado['historial_pasos']) > iter_num:
                            paso = resultado['historial_pasos'][iter_num]
                            if 'contenido' in paso and 'valor_z_actual' in paso['contenido']:
                                st.metric("Valor Z Actual", f"{paso['contenido']['valor_z_actual']:.6f}")

    else:
        st.success("✅ La solución óptima se encontró en la iteración inicial.")

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

    # VARIABLES DE DECISIÓN
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

    # VARIABLES DE HOLGURA
    st.subheader("📦 Variables de Holgura")
    if 'solucion_holguras' in resultado:
        holgura_data = []
        for s, valor in resultado['solucion_holguras'].items():
            holgura_data.append({
                'Variable de Holgura': s,
                'Valor': f"{valor:.6f}",
                'Restricción': 'Activa' if valor < 1e-6 else 'Inactiva'
            })

        holgura_df = pd.DataFrame(holgura_data)
        st.dataframe(holgura_df, use_container_width=True, hide_index=True)

    # TABLA FINAL
    st.subheader("📊 Tabla Final del Simplex")
    st.dataframe(tabla_final, use_container_width=True)

    # VERIFICACIÓN DE RESTRICCIONES
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

    # RESUMEN FINAL
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


def mostrar_ejemplos(metodo):
    """
    Muestra ejemplos según el método seleccionado

    Args:
        metodo: Tipo de método ('simplex', 'gran_m', 'dos_fases', 'dual')
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
        - Demanda Coca-Cola: x₁ ≥ 450,000
        - Demanda Sprite: x₂ ≥ 300,000
        - Demanda Fanta: x₃ ≥ 360,000
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

    elif metodo == "gran_m":
        st.subheader("Ejemplo Gran M")
        st.write("min: 2x₁ + 3x₂")
        st.write("s.a: x₁ + x₂ ≥ 5")
        st.write("     x₁ ≥ 2")
        st.write("     x₂ ≥ 1")

        if st.button("Ejecutar", key="ej_granm"):
            gran_m = GranM([2, 3], [[1, 1], [1, 0], [0, 1]], [5, 2, 1], [">=", ">=", ">="], tipo="min",
                           nombres_vars=["x1", "x2"])
            resultado = gran_m.resolver(verbose=False)

            st.metric("Z", f"{resultado['valor_optimo']:.4f}")
            st.metric("x₁", f"{resultado['solucion_variables']['x1']:.4f}")
            st.metric("x₂", f"{resultado['solucion_variables']['x2']:.4f}")

            st.dataframe(gran_m.obtener_tabla_pandas(), use_container_width=True)

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