import streamlit as st
import pandas as pd
from models.programacion_lineal.dual import Dual


def show_dualidad():
    """Vista de análisis de dualidad"""
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