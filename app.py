import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos
from models.programacion_lineal.simplex import Simplex
from models.programacion_lineal.gran_m import GranM
from models.programacion_lineal.dos_fases import DosFases
from models.programacion_lineal.dual import Dual

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Optimización Empresarial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2ca02c;
        border-bottom: 2px solid #2ca02c;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .error-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'resultados' not in st.session_state:
    st.session_state.resultados = {}
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'metodo_seleccionado' not in st.session_state:
    st.session_state.metodo_seleccionado = "simplex"

# Header principal
st.markdown("<h1 class='main-header'>🎯 Sistema de Optimización Empresarial</h1>", unsafe_allow_html=True)
st.markdown("*Investigación Operativa - Análisis y Optimización de Procesos Empresariales*")

# Sidebar para navegación
st.sidebar.title("📋 Menú Principal")
menu_principal = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio",
     "📈 Programación Lineal",
     "🔀 Análisis de Dualidad",
     "📦 Gestión de Inventarios",
     "📊 Historial de Resultados"]
)

# ============================================
# SECCIÓN: INICIO
# ============================================
if menu_principal == "🏠 Inicio":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 class='section-header'>¿Qué es este Sistema?</h3>", unsafe_allow_html=True)
        st.write("""
        Este sistema integra diversos métodos de **Investigación Operativa** para resolver 
        problemas de optimización en contextos empresariales:

        - **Programación Lineal**: Simplex, Gran M, Dos Fases
        - **Análisis de Dualidad**: Transformación Primal-Dual
        - **Gestión de Inventarios**: Modelo EOQ
        """)

    with col2:
        st.markdown("<h3 class='section-header'>Características Principales</h3>", unsafe_allow_html=True)
        st.write("""
        ✅ **Implementación desde cero** - Sin librerías de optimización

        ✅ **Múltiples métodos** - Simplex, Gran M, Dos Fases y Dualidad

        ✅ **Análisis completo** - Tablas, validación de restricciones

        ✅ **Detección de casos** - Óptimo, No Acotado, Infactible
        """)

# ============================================
# SECCIÓN: PROGRAMACIÓN LINEAL
# ============================================
elif menu_principal == "📈 Programación Lineal":
    st.markdown("<h2 class='section-header'>Programación Lineal</h2>", unsafe_allow_html=True)

    # Seleccionar método
    st.markdown("### 📌 Selecciona el Método de Resolución")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Simplex", use_container_width=True, key="btn_simplex"):
            st.session_state.metodo_seleccionado = "simplex"
    with col2:
        if st.button("⚙️ Gran M", use_container_width=True, key="btn_granm"):
            st.session_state.metodo_seleccionado = "gran_m"
    with col3:
        if st.button("🔄 Dos Fases", use_container_width=True, key="btn_dosfases"):
            st.session_state.metodo_seleccionado = "dos_fases"
    with col4:
        if st.button("🔀 Dualidad", use_container_width=True, key="btn_dual"):
            st.session_state.metodo_seleccionado = "dual"

    metodo = st.session_state.metodo_seleccionado

    st.write("---")

    if metodo == "simplex":
        st.info("**Método Simplex** - Restricciones ≤ únicamente")
    elif metodo == "gran_m":
        st.info("**Método Gran M** - Restricciones ≤, ≥ y =")
    elif metodo == "dos_fases":
        st.info("**Método de Dos Fases** - Restricciones ≤, ≥ y = (Más robusto)")
    elif metodo == "dual":
        st.info("**Método de Dualidad** - Análisis Primal-Dual de problemas de optimización")

    st.write("---")

    # Tabs para entrada manual y ejemplos
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Entrada Manual", "Ejemplo Simplex", "Ejemplo Gran M", "Ejemplo Dos Fases", "Ejemplo Dualidad"])

    with tab1:
        st.subheader("Ingresa tu Problema de Programación Lineal")

        col1, col2 = st.columns(2)

        with col1:
            n_vars = st.number_input("Número de variables:", min_value=2, max_value=10, value=2, key="n_vars")
            n_rest = st.number_input("Número de restricciones:", min_value=1, max_value=10, value=2, key="n_rest")

        with col2:
            tipo_opt = st.radio("Optimización:", ["Maximizar", "Minimizar"], key="tipo_opt")

        st.write("---")
        st.subheader("Función Objetivo")

        col_coefs = st.columns(n_vars)
        coefs = []
        for i, col in enumerate(col_coefs):
            with col:
                coef = st.number_input(f"c{i + 1}:", value=1.0, key=f"c_{i}", step=0.1)
                coefs.append(coef)

        st.write("---")
        st.subheader("Restricciones")

        A = []
        b = []
        signos = []

        for i in range(n_rest):
            st.markdown(f"**Restricción {i + 1}**")
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                cols_rest = st.columns(n_vars)
                fila = []
                for j, col in enumerate(cols_rest):
                    with col:
                        coef = st.number_input(f"a{i + 1}{j + 1}:", value=1.0, key=f"a_{i}_{j}", step=0.1)
                        fila.append(coef)
                A.append(fila)

            with col2:
                op = st.selectbox("Op", ["<=", ">=", "="], key=f"op_{i}", label_visibility="collapsed")
                signos.append(op)

            with col3:
                rhs = st.number_input("RHS", value=10.0, key=f"rhs_{i}", step=0.1, label_visibility="collapsed")
                b.append(rhs)

        # Resolver
        if st.button("🚀 Resolver", key="resolver_pl"):
            tipo_simplex = "min" if tipo_opt == "Minimizar" else "max"
            nombres = [f"x{i + 1}" for i in range(n_vars)]

            try:
                if metodo == "simplex":
                    # Convertir >= a <=
                    A_procesada = []
                    b_procesada = []
                    for i in range(n_rest):
                        if signos[i] == ">=":
                            A_procesada.append([-x for x in A[i]])
                            b_procesada.append(-b[i])
                        elif signos[i] == "=":
                            st.warning(f"⚠️ R{i + 1}: Igualdad no soportada en Simplex")
                            A_procesada.append(A[i])
                            b_procesada.append(b[i])
                        else:
                            A_procesada.append(A[i])
                            b_procesada.append(b[i])

                    simplex = Simplex(coefs, A_procesada, b_procesada, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = simplex.resolver(verbose=False)
                    tabla_final = simplex.obtener_tabla_pandas()
                    metodo_usado = "Simplex"

                elif metodo == "gran_m":
                    gran_m = GranM(coefs, A, b, signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = gran_m.resolver(verbose=False)
                    tabla_final = gran_m.obtener_tabla_pandas()
                    metodo_usado = "Gran M"

                elif metodo == "dos_fases":
                    dos_fases = DosFases(coefs, A, b, signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = dos_fases.resolver(verbose=False)
                    tabla_final = dos_fases.obtener_tabla_fase2_pandas()
                    metodo_usado = "Dos Fases"

                elif metodo == "dual":
                    dual = Dual(coefs, A, b, signos=signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = dual.resolver(verbose=False)
                    st.success("✅ Análisis de Dualidad Completado")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Z Primal", f"{resultado['primal']['valor_optimo']:.6f}")
                    with col2:
                        st.metric("Z Dual", f"{resultado['dual']['valor_optimo']:.6f}")
                    with col3:
                        st.metric("Diferencia", f"{resultado['diferencia_valores_optimos']:.2e}")

                    st.write("---")
                    st.subheader("Comparación Primal - Dual")
                    st.dataframe(dual.obtener_comparacion_problemas(), use_container_width=True, hide_index=True)

                    st.write("---")
                    st.subheader("Solución Primal")
                    primal_data = []
                    for var in nombres:
                        primal_data.append([var, f"{resultado['primal']['solucion'][var]:.6f}"])
                    st.dataframe(pd.DataFrame(primal_data, columns=["Variable", "Valor"]), use_container_width=True,
                                 hide_index=True)

                    st.write("---")
                    st.subheader("Solución Dual")
                    dual_data = []
                    for var, val in resultado['dual']['solucion'].items():
                        dual_data.append([var, f"{val:.6f}"])
                    st.dataframe(pd.DataFrame(dual_data, columns=["Variable", "Valor"]), use_container_width=True,
                                 hide_index=True)

                    st.write("---")
                    st.subheader("Interpretación de Dualidad")
                    if resultado['dualidad_fuerte']:
                        st.markdown(
                            "<div class='success-box'><strong>✓ DUALIDAD FUERTE VERIFICADA</strong><br>Los valores óptimos del primal y dual son iguales</div>",
                            unsafe_allow_html=True)
                    else:
                        st.markdown(
                            "<div class='warning-box'><strong>⚠️ Dualidad no verificada</strong><br>Verificar la solución</div>",
                            unsafe_allow_html=True)

                    # Guardar historial
                    st.session_state.historial.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo': 'Programación Lineal',
                        'metodo': 'Dualidad',
                        'z_optimo_primal': float(resultado['primal']['valor_optimo']) if resultado['primal'][
                            'valor_optimo'] else None,
                        'z_optimo_dual': float(resultado['dual']['valor_optimo']) if resultado['dual'][
                            'valor_optimo'] else None,
                        'dualidad_fuerte': resultado['dualidad_fuerte']
                    })

                    st.stop()

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

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Valor Z", f"{resultado['valor_optimo']:.6f}")
                with col2:
                    st.metric("Iteraciones", resultado['iteraciones'])
                with col3:
                    st.metric("Estado", estado)

                st.write("---")

                # Variables de decisión
                st.subheader("Variables de Decisión")
                var_data = []
                for var in nombres:
                    var_data.append([var, f"{resultado['solucion_variables'][var]:.6f}"])
                st.dataframe(pd.DataFrame(var_data, columns=["Variable", "Valor"]), use_container_width=True,
                             hide_index=True)

                st.write("---")

                # Tabla final
                st.subheader("Tabla Final")
                st.dataframe(tabla_final, use_container_width=True)

                st.write("---")

                # Verificación de restricciones
                st.subheader("Verificación de Restricciones")
                verif = []
                for i in range(n_rest):
                    suma = sum(A[i][j] * resultado['solucion_variables'][nombres[j]] for j in range(n_vars))
                    op = signos[i]
                    rhs = b[i]

                    if op == "<=":
                        cumple = suma <= rhs + 1e-4
                    elif op == ">=":
                        cumple = suma >= rhs - 1e-4
                    else:
                        cumple = abs(suma - rhs) <= 1e-4

                    verif.append(["R" + str(i + 1), f"{suma:.6f}", op, f"{rhs:.6f}", "✓" if cumple else "✗"])

                st.dataframe(pd.DataFrame(verif, columns=["Restricción", "LHS", "Op", "RHS", "Cumple"]),
                             use_container_width=True, hide_index=True)

                # Guardar historial
                st.session_state.historial.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'tipo': 'Programación Lineal',
                    'metodo': metodo_usado,
                    'z_optimo': float(resultado['valor_optimo']),
                    'iteraciones': resultado['iteraciones'],
                    'estado': estado
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")

    with tab2:
        st.subheader("Ejemplo Simplex")
        st.write("max: 3x₁ + 2x₂")
        st.write("s.a: x₁ + x₂ ≤ 10")
        st.write("     2x₁ + x₂ ≤ 15")

        if st.button("Ejecutar", key="ej_simplex"):
            simplex = Simplex([3, 2], [[1, 1], [2, 1]], [10, 15], tipo="max", nombres_vars=["x1", "x2"])
            resultado = simplex.resolver(verbose=False)

            st.metric("Z", f"{resultado['valor_optimo']:.4f}")
            st.metric("x₁", f"{resultado['solucion_variables']['x1']:.4f}")
            st.metric("x₂", f"{resultado['solucion_variables']['x2']:.4f}")

            st.dataframe(simplex.obtener_tabla_pandas(), use_container_width=True)

    with tab3:
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

    with tab4:
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

    with tab5:
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

# ============================================
# SECCIÓN: ANÁLISIS DE DUALIDAD
# ============================================
elif menu_principal == "🔀 Análisis de Dualidad":
    st.markdown("<h2 class='section-header'>Análisis de Dualidad en Programación Lineal</h2>", unsafe_allow_html=True)

    st.write("""
    La **dualidad** es un concepto fundamental en programación lineal que relaciona dos problemas de optimización:

    - **Problema Primal**: El problema original
    - **Problema Dual**: Derivado matemáticamente del primal

    ### Teorema de Dualidad Fuerte
    Si el problema primal tiene una solución óptima, entonces el problema dual también la tiene,
    y los valores óptimos de ambos son iguales: **Z_primal = Z_dual**
    """)

    st.write("---")

    st.subheader("📊 Ingresa tu Problema Primal")

    col1, col2 = st.columns(2)
    with col1:
        n_vars_dual = st.number_input("Número de variables:", min_value=2, max_value=10, value=2, key="n_vars_dual")
        n_rest_dual = st.number_input("Número de restricciones:", min_value=1, max_value=10, value=2, key="n_rest_dual")

    with col2:
        tipo_opt_dual = st.radio("Optimización:", ["Maximizar", "Minimizar"], key="tipo_opt_dual")

    st.write("---")
    st.subheader("Función Objetivo")

    col_coefs_dual = st.columns(n_vars_dual)
    coefs_dual = []
    for i, col in enumerate(col_coefs_dual):
        with col:
            coef = st.number_input(f"c{i + 1}:", value=1.0, key=f"c_dual_{i}", step=0.1)
            coefs_dual.append(coef)

    st.write("---")
    st.subheader("Restricciones")

    A_dual = []
    b_dual = []
    signos_dual = []

    for i in range(n_rest_dual):
        st.markdown(f"**Restricción {i + 1}**")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            cols_rest_dual = st.columns(n_vars_dual)
            fila = []
            for j, col in enumerate(cols_rest_dual):
                with col:
                    coef = st.number_input(f"a{i + 1}{j + 1}:", value=1.0, key=f"a_dual_{i}_{j}", step=0.1)
                    fila.append(coef)
            A_dual.append(fila)

        with col2:
            op = st.selectbox("Op", ["<=", ">=", "="], key=f"op_dual_{i}", label_visibility="collapsed")
            signos_dual.append(op)

        with col3:
            rhs = st.number_input("RHS", value=10.0, key=f"rhs_dual_{i}", step=0.1, label_visibility="collapsed")
            b_dual.append(rhs)

    if st.button("🚀 Analizar Dualidad", key="resolver_dual"):
        tipo_dual_simplex = "min" if tipo_opt_dual == "Minimizar" else "max"
        nombres_dual = [f"x{i + 1}" for i in range(n_vars_dual)]

        try:
            dual_obj = Dual(coefs_dual, A_dual, b_dual, signos=signos_dual, tipo=tipo_dual_simplex,
                            nombres_vars=nombres_dual)
            resultado_dual = dual_obj.resolver(verbose=False)

            # Mostrar comparación
            st.write("---")
            st.subheader("📋 Comparación Primal - Dual")
            st.dataframe(dual_obj.obtener_comparacion_problemas(), use_container_width=True, hide_index=True)

            st.write("---")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Solución Primal")
                if resultado_dual['primal']['exito']:
                    st.metric("Z Primal", f"{resultado_dual['primal']['valor_optimo']:.6f}")
                    st.metric("Iteraciones", resultado_dual['primal']['iteraciones'])

                    primal_sol = pd.DataFrame([
                        [var, f"{val:.6f}"]
                        for var, val in resultado_dual['primal']['solucion'].items()
                    ], columns=["Variable", "Valor"])
                    st.dataframe(primal_sol, use_container_width=True, hide_index=True)
                else:
                    st.error("No se encontró solución primal")

            with col2:
                st.subheader("✅ Solución Dual")
                if resultado_dual['dual']['exito']:
                    st.metric("Z Dual", f"{resultado_dual['dual']['valor_optimo']:.6f}")
                    st.metric("Iteraciones", resultado_dual['dual']['iteraciones'])

                    dual_sol = pd.DataFrame([
                        [var, f"{val:.6f}"]
                        for var, val in resultado_dual['dual']['solucion'].items()
                    ], columns=["Variable", "Valor"])
                    st.dataframe(dual_sol, use_container_width=True, hide_index=True)
                else:
                    st.error("No se encontró solución dual")

            st.write("---")
            st.subheader("🔍 Verificación de Dualidad Fuerte")

            if resultado_dual['dualidad_fuerte']:
                st.markdown("""
                <div class='success-box'>
                <h4>✓ DUALIDAD FUERTE VERIFICADA</h4>
                <p>Los valores óptimos del problema primal y dual son iguales (dentro de tolerancia numérica).</p>
                <p>Esto confirma que ambos problemas tienen soluciones óptimas equivalentes.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='warning-box'>
                <h4>⚠️ Verificación incompleta</h4>
                <p>La dualidad fuerte no se verificó completamente. Esto puede indicar:</p>
                <ul>
                <li>Uno de los problemas es infactible</li>
                <li>Uno de los problemas es no acotado</li>
                <li>Errores numéricos en la resolución</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

            st.metric("Diferencia en valores óptimos", f"{resultado_dual['diferencia_valores_optimos']:.2e}")

        except Exception as e:
            st.error(f"Error en el análisis: {str(e)}")

# ============================================
# SECCIÓN: GESTIÓN DE INVENTARIOS
# ============================================
elif menu_principal == "📦 Gestión de Inventarios":
    st.markdown("<h2 class='section-header'>Gestión de Inventarios</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        D = st.number_input("Demanda anual (D):", value=1000.0, step=100.0)
    with col2:
        K = st.number_input("Costo de orden (K):", value=50.0, step=10.0)
    with col3:
        h = st.number_input("Costo de mantener (h):", value=2.0, step=0.1)

    if st.button("🚀 Calcular EOQ"):
        EOQ = np.sqrt((2 * D * K) / h)
        costo_total = (D / EOQ) * K + (EOQ / 2) * h

        st.success("✅ Cálculo completado")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("EOQ (Q*)", f"{EOQ:.2f}")
        with col2:
            st.metric("Órdenes/Año", f"{D / EOQ:.2f}")
        with col3:
            st.metric("Costo Total", f"${costo_total:.2f}")
        with col4:
            st.metric("Período", f"{365 // (D / EOQ):.0f} días")

# ============================================
# SECCIÓN: HISTORIAL
# ============================================
elif menu_principal == "📊 Historial de Resultados":
    st.markdown("<h2 class='section-header'>Historial de Análisis</h2>", unsafe_allow_html=True)

    if st.session_state.historial:
        historial_df = pd.DataFrame(st.session_state.historial)
        st.dataframe(historial_df, use_container_width=True, hide_index=True)

        if st.button("🗑️ Limpiar Historial"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("📭 No hay análisis registrados aún")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
    <p>Sistema de Optimización Empresarial - Investigación Operativa</p>
    <p>Implementación desde Cero - Sin Librerías de Optimización</p>
    <p>Métodos: Simplex | Gran M | Dos Fases | Dualidad</p>
</div>
""", unsafe_allow_html=True)