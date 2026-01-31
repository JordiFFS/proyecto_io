import streamlit as st
import pandas as pd
from datetime import datetime
from models.programacion_lineal.simplex import Simplex
from models.programacion_lineal.gran_m import GranM
from models.programacion_lineal.dos_fases import DosFases
from models.programacion_lineal.dual import Dual
from .resolucion_simplex import mostrar_resolucion_simplex, mostrar_ejemplos
from .resolucion_gran_m import mostrar_resolucion_gran_m, ejemplo_gran_m_coca_cola
from .resolucion_dos_fases import mostrar_resolucion_dos_fases, ejemplo_dos_fases_coca_cola
from .resolucion_dual_con_ejemplo import mostrar_resolucion_dual, ejemplo_dual_coca_cola


def show_programacion_lineal():
    """Vista de programación lineal"""
    st.markdown("<h2 class='section-header'>Programación Lineal - Método Simplex Detallado</h2>",
                unsafe_allow_html=True)

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
        st.info("**Método Simplex** - Restricciones ≤ únicamente - CON VISUALIZACIÓN DETALLADA DE PASOS")
    elif metodo == "gran_m":
        st.info("**Método Gran M** - Restricciones ≤, ≥ y =")
    elif metodo == "dos_fases":
        st.info("**Método de Dos Fases** - Restricciones ≤, ≥ y = (Más robusto)")
    elif metodo == "dual":
        st.info("**Método de Dualidad** - Análisis Primal-Dual de problemas de optimización")

    st.write("---")

    # Tabs para entrada manual y ejemplos
    tab1, tab2 = st.tabs(["Entrada Manual", "Ejemplos"])

    with tab1:
        st.subheader("📋 Ingresa tu Problema de Programación Lineal")

        col1, col2 = st.columns(2)

        with col1:
            n_vars = st.number_input("Número de variables:", min_value=2, max_value=10, value=2, key="n_vars")
            n_rest = st.number_input("Número de restricciones:", min_value=1, max_value=10, value=2, key="n_rest")

        with col2:
            tipo_opt = st.radio("Optimización:", ["Maximizar", "Minimizar"], key="tipo_opt")

        st.write("---")
        st.subheader("🎯 Función Objetivo")

        col_coefs = st.columns(n_vars)
        coefs = []
        for i, col in enumerate(col_coefs):
            with col:
                coef = st.number_input(f"c{i + 1}:", value=1.0, key=f"c_{i}", step=0.1)
                coefs.append(coef)

        st.write("---")
        st.subheader("⚙️ Restricciones")

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
        if st.button("🚀 Resolver y Mostrar Todos los Pasos", key="resolver_pl", use_container_width=True):
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

                    # Mostrar resolución completa
                    mostrar_resolucion_simplex(resultado, tabla_final, nombres, A, b, signos, n_vars, n_rest, tipo_opt,
                                               metodo_usado)

                    # Guardar historial
                    st.session_state.historial.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo': 'Programación Lineal',
                        'metodo': metodo_usado,
                        'z_optimo': float(resultado['valor_optimo']),
                        'iteraciones': resultado['iteraciones'],
                        'estado': resultado.get('estado', 'Desconocido')
                    })

                elif metodo == "gran_m":
                    gran_m = GranM(coefs, A, b, signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = gran_m.resolver(verbose=False)
                    tabla_final = gran_m.obtener_tabla_pandas()
                    metodo_usado = "Gran M"

                    # Mostrar resolución completa
                    mostrar_resolucion_gran_m(resultado, nombres, n_vars, n_rest, tipo_opt)

                    # Guardar historial
                    st.session_state.historial.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo': 'Programación Lineal',
                        'metodo': metodo_usado,
                        'z_optimo': float(resultado['valor_optimo']) if resultado['valor_optimo'] else None,
                        'iteraciones': resultado['iteraciones'],
                        'estado': resultado.get('estado', 'Desconocido')
                    })

                elif metodo == "dos_fases":
                    dos_fases = DosFases(coefs, A, b, signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = dos_fases.resolver(verbose=False)
                    tabla_final = dos_fases.obtener_tabla_fase2_pandas()
                    metodo_usado = "Dos Fases"

                    # Mostrar resolución completa
                    mostrar_resolucion_dos_fases(resultado, nombres, n_vars, n_rest, tipo_opt)

                    # Guardar historial
                    st.session_state.historial.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo': 'Programación Lineal',
                        'metodo': metodo_usado,
                        'z_optimo': float(resultado['valor_optimo']) if resultado['valor_optimo'] else None,
                        'iteraciones': resultado['iteraciones'],
                        'estado': resultado.get('estado', 'Desconocido')
                    })

                elif metodo == "dual":
                    dual = Dual(coefs, A, b, signos=signos, tipo=tipo_simplex, nombres_vars=nombres)
                    resultado = dual.resolver(verbose=False)

                    # Mostrar resolución completa del Dual
                    mostrar_resolucion_dual(resultado)

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

            except Exception as e:
                st.error(f"Error: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

    with tab2:
        if metodo == "gran_m":
            ejemplo_gran_m_coca_cola()
        elif metodo == "dos_fases":
            ejemplo_dos_fases_coca_cola()
        elif metodo == "dual":
            ejemplo_dual_coca_cola()
        else:
            mostrar_ejemplos(metodo)