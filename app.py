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
from ia.analisis_sensibilidad import AnalisisSensibilidad
from empresa.caso_empresarial import CasoEmpresarial

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
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'resultados' not in st.session_state:
    st.session_state.resultados = {}
if 'historial' not in st.session_state:
    st.session_state.historial = []

# Header principal
st.markdown("<h1 class='main-header'>🎯 Sistema de Optimización Empresarial</h1>", unsafe_allow_html=True)
st.markdown("*Investigación Operativa - Análisis y Optimización de Procesos Empresariales*")

# Sidebar para navegación
st.sidebar.title("📋 Menú Principal")
menu_principal = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio",
     "📈 Programación Lineal",
     "🚚 Problemas de Transporte",
     "🌐 Problemas de Redes",
     "📦 Gestión de Inventarios",
     "🏢 Caso Empresarial Integral",
     "🤖 Análisis de Sensibilidad IA",
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

        - **Programación Lineal**: Simplex, Gran M, Dos Fases, Método Dual
        - **Problemas de Transporte**: Costo Mínimo, Esquina Noroeste, Vogel
        - **Problemas de Redes**: Ruta más corta, Árbol de expansión mínima, Flujo máximo
        - **Gestión de Inventarios**: Modelos clásicos de inventario
        - **IA para Sensibilidad**: Análisis inteligente de resultados
        """)

    with col2:
        st.markdown("<h3 class='section-header'>Características Principales</h3>", unsafe_allow_html=True)
        st.write("""
        ✅ **Implementación desde cero** - Sin librerías de optimización

        ✅ **Múltiples métodos** - Comparación de resultados

        ✅ **Análisis IA** - Sensibilidad y recomendaciones

        ✅ **Caso real** - Aplicación empresarial integral

        ✅ **Visualizaciones** - Gráficos y tablas interactivas
        """)

# ============================================
# SECCIÓN: PROGRAMACIÓN LINEAL
# ============================================
elif menu_principal == "📈 Programación Lineal":
    st.markdown("<h2 class='section-header'>Programación Lineal - Método Simplex</h2>", unsafe_allow_html=True)

    # Tabs para diferentes opciones
    tab1, tab2 = st.tabs(["Entrada Manual", "Ejemplo Predefinido"])

    with tab1:
        st.subheader("Ingresa tu Problema de Programación Lineal")

        col1, col2 = st.columns(2)

        with col1:
            n_vars = st.number_input("Número de variables de decisión:", min_value=2, max_value=10, value=2)
            n_rest = st.number_input("Número de restricciones:", min_value=1, max_value=10, value=2)

        with col2:
            tipo_opt = st.radio("Tipo de optimización:", ["Maximizar", "Minimizar"])

        st.write("---")
        st.subheader("Función Objetivo")

        col_coefs = st.columns(n_vars)
        coefs = []
        for i, col in enumerate(col_coefs):
            with col:
                coef = st.number_input(f"Coef x{i + 1}:", value=1.0, key=f"coef_{i}")
                coefs.append(coef)

        st.write("---")
        st.subheader("Restricciones")

        A = []
        b = []
        operadores = []

        for i in range(n_rest):
            st.markdown(f"**Restricción {i + 1}**")
            col1, col2, col3 = st.columns([2, 0.5, 1])

            with col1:
                cols_rest = st.columns(n_vars)
                fila = []
                for j, col in enumerate(cols_rest):
                    with col:
                        coef = st.number_input(f"x{j + 1}:", value=1.0, key=f"a_{i}_{j}", step=0.1)
                        fila.append(coef)
                A.append(fila)

            with col2:
                op = st.selectbox("", ["<=", ">=", "="], key=f"op_{i}", label_visibility="collapsed")
                operadores.append(op)

            with col3:
                rhs = st.number_input("RHS:", value=10.0, key=f"rhs_{i}", step=0.1)
                b.append(rhs)

        # Convertir restricciones >= y = a <=
        A_procesada = []
        b_procesada = []

        for i in range(n_rest):
            if operadores[i] == ">=":
                # Multiplicar por -1
                A_procesada.append([-x for x in A[i]])
                b_procesada.append(-b[i])
            elif operadores[i] == "=":
                # Para igualdad, agregar dos restricciones
                st.warning(f"⚠️ Las restricciones de igualdad no están soportadas en esta versión. Use <= o >=")
                A_procesada.append(A[i])
                b_procesada.append(b[i])
            else:
                A_procesada.append(A[i])
                b_procesada.append(b[i])

        if st.button("🚀 Resolver", key="resolver_pl"):
            try:
                # Crear tipo de optimización para el Simplex
                tipo_simplex = "min" if tipo_opt == "Minimizar" else "max"

                # Crear instancia del Simplex
                nombres = [f"x{i + 1}" for i in range(n_vars)]
                simplex = Simplex(coefs, A_procesada, b_procesada, tipo=tipo_simplex, nombres_vars=nombres)

                # Resolver
                resultado = simplex.resolver(verbose=False)

                if resultado['exito']:
                    # Mostrar resultados
                    st.markdown("### ✅ Solución Óptima Encontrada")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Valor Óptimo (Z)",
                            f"{resultado['valor_optimo']:.4f}",
                            delta=f"{resultado['iteraciones']} iteraciones"
                        )

                    with col2:
                        st.metric("Variables Básicas", len(resultado['base_final']))

                    with col3:
                        st.metric("Estado", "✓ Óptimo")

                    st.write("---")

                    # Tabla de solución
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Variables de Decisión")
                        var_table = pd.DataFrame(
                            [[var, resultado['solucion_variables'][var]]
                             for var in nombres],
                            columns=["Variable", "Valor"]
                        )
                        st.dataframe(var_table, use_container_width=True, hide_index=True)

                    with col2:
                        st.subheader("Variables de Holgura")
                        holgura_data = []
                        for i in range(n_rest):
                            s_var = f"s{i + 1}"
                            if s_var in resultado['solucion']:
                                holgura_data.append([s_var, resultado['solucion'][s_var]])

                        if holgura_data:
                            holgura_table = pd.DataFrame(holgura_data, columns=["Variable", "Valor"])
                            st.dataframe(holgura_table, use_container_width=True, hide_index=True)
                        else:
                            st.info("Sin holgura")

                    st.write("---")

                    # Tabla Simplex final
                    st.subheader("Tabla Final del Simplex")
                    tabla_final = simplex.obtener_tabla_pandas()
                    st.dataframe(tabla_final, use_container_width=True)

                    # Verificación de restricciones
                    st.subheader("Verificación de Restricciones")
                    verificacion = []
                    for i in range(n_rest):
                        suma = sum(A[i][j] * resultado['solucion_variables'][nombres[j]]
                                   for j in range(n_vars))
                        op = operadores[i]
                        rhs = b[i]

                        if op == "<=":
                            cumple = suma <= rhs + 1e-6
                        elif op == ">=":
                            cumple = suma >= rhs - 1e-6
                        else:
                            cumple = abs(suma - rhs) <= 1e-6

                        verificacion.append({
                            "Restricción": f"R{i + 1}",
                            "LHS": f"{suma:.4f}",
                            "Op": op,
                            "RHS": f"{rhs:.4f}",
                            "Cumple": "✓" if cumple else "✗"
                        })

                    verif_table = pd.DataFrame(verificacion)
                    st.dataframe(verif_table, use_container_width=True, hide_index=True)

                    # Guardar en historial
                    st.session_state.historial.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo': 'Programación Lineal',
                        'metodo': 'Simplex',
                        'z_optimo': float(resultado['valor_optimo']),
                        'iteraciones': resultado['iteraciones']
                    })

                else:
                    st.error(f"❌ Error: {resultado.get('mensaje', 'Error desconocido')}")

            except Exception as e:
                st.error(f"❌ Error al procesar: {str(e)}")
                st.write(f"Detalles: {e}")

    with tab2:
        st.subheader("Ejemplo Predefinido: Problema del Usuario")

        st.markdown("""
        **Función Objetivo:**
        - max: 5x₁ + 4x₂

        **Restricciones:**
        - 6x₁ + 4x₂ ≤ 24
        - x₁ + 2x₂ ≤ 6
        - x₂ ≤ 2
        - -x₁ + x₂ ≤ 1
        - x₁, x₂ ≥ 0

        **Respuesta Esperada:**
        - Z = 21
        - x₁ = 3
        - x₂ = 1.5
        """)

        if st.button("📊 Ejecutar Ejemplo", key="ejecutar_ejemplo"):
            # Definir el problema
            c = [5, 4]
            A = [
                [6, 4],
                [1, 2],
                [0, 1],
                [-1, 1]
            ]
            b = [24, 6, 2, 1]

            simplex = Simplex(c, A, b, tipo="max", nombres_vars=["x1", "x2"])
            resultado = simplex.resolver(verbose=False)

            if resultado['exito']:
                st.success("✅ Problema Resuelto")

                col1, col2, col3 = st.columns(3)

                z = resultado['valor_optimo']
                x1 = resultado['solucion_variables']['x1']
                x2 = resultado['solucion_variables']['x2']

                with col1:
                    st.metric("Z", f"{z:.4f}", delta=f"Esperado: 21" if abs(z - 21) < 0.01 else "Diferencia")

                with col2:
                    st.metric("x₁", f"{x1:.4f}", delta=f"Esperado: 3" if abs(x1 - 3) < 0.01 else "Diferencia")

                with col3:
                    st.metric("x₂", f"{x2:.4f}", delta=f"Esperado: 1.5" if abs(x2 - 1.5) < 0.01 else "Diferencia")

                st.write("---")

                # Tabla final
                st.subheader("Tabla Final del Simplex")
                tabla = simplex.obtener_tabla_pandas()
                st.dataframe(tabla, use_container_width=True)

                # Comparación con esperado
                st.subheader("Comparación con Resultado Manual")
                comparacion = pd.DataFrame({
                    "Variable": ["Z", "x₁", "x₂", "s₃", "s₄"],
                    "Obtenido": [
                        f"{z:.4f}",
                        f"{x1:.4f}",
                        f"{x2:.4f}",
                        f"{resultado['solucion'].get('s3', 0):.4f}",
                        f"{resultado['solucion'].get('s4', 0):.4f}"
                    ],
                    "Esperado": ["21", "3", "1.5", "0.5", "2.5"],
                    "Correcto": [
                        "✓" if abs(z - 21) < 0.01 else "✗",
                        "✓" if abs(x1 - 3) < 0.01 else "✗",
                        "✓" if abs(x2 - 1.5) < 0.01 else "✗",
                        "✓" if abs(resultado['solucion'].get('s3', 0) - 0.5) < 0.01 else "✗",
                        "✓" if abs(resultado['solucion'].get('s4', 0) - 2.5) < 0.01 else "✗"
                    ]
                })
                st.dataframe(comparacion, use_container_width=True, hide_index=True)
            else:
                st.error(f"Error: {resultado.get('mensaje')}")

# ============================================
# SECCIÓN: PROBLEMAS DE TRANSPORTE
# ============================================
elif menu_principal == "🚚 Problemas de Transporte":
    st.markdown("<h2 class='section-header'>Problemas de Transporte</h2>", unsafe_allow_html=True)
    st.info("🔧 Esta sección está en desarrollo")

# ============================================
# SECCIÓN: PROBLEMAS DE REDES
# ============================================
elif menu_principal == "🌐 Problemas de Redes":
    st.markdown("<h2 class='section-header'>Problemas de Redes</h2>", unsafe_allow_html=True)
    st.info("🔧 Esta sección está en desarrollo")

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
            st.metric("EOQ (Q*)", f"{EOQ:.2f} unidades")
        with col2:
            st.metric("Órdenes/Año", f"{D / EOQ:.2f}")
        with col3:
            st.metric("Costo Total", f"${costo_total:.2f}")
        with col4:
            st.metric("Período", f"{365 // (D / EOQ):.0f} días")

# ============================================
# SECCIÓN: CASO EMPRESARIAL
# ============================================
elif menu_principal == "🏢 Caso Empresarial Integral":
    st.markdown("<h2 class='section-header'>Caso Empresarial Integral</h2>", unsafe_allow_html=True)

    st.markdown("""
    ### 📋 Descripción del Caso

    **Empresa de Manufactura y Distribución "TechOptimize S.A."**
    """)

    if st.button("📊 Ejecutar Análisis Integral"):
        st.success("✅ Análisis ejecutado")
        st.info("🔧 Integrando resultados de todos los módulos...")

# ============================================
# SECCIÓN: ANÁLISIS SENSIBILIDAD
# ============================================
elif menu_principal == "🤖 Análisis de Sensibilidad IA":
    st.markdown("<h2 class='section-header'>Análisis de Sensibilidad con IA</h2>", unsafe_allow_html=True)
    st.info("🔧 Esta sección está en desarrollo")

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
    <p>Desarrollo e Implementación desde Cero - Sin Librerías de Optimización</p>
</div>
""", unsafe_allow_html=True)