import streamlit as st
import pandas as pd
from models.programacion_lineal.dual import Dual


def mostrar_resolucion_dual(resultado):
    """Muestra la resolución completa del análisis de dualidad"""

    st.write("---")
    st.markdown("<h2 class='section-header'>📋 Comparación Primal - Dual</h2>", unsafe_allow_html=True)

    # Crear vista comparativa
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 Problema PRIMAL")
        st.write(f"""
        **Tipo:** {resultado['tipo_primal_original'].upper()}

        **Variables:** {len(resultado['nombres_vars_primal'])}
        - {', '.join(resultado['nombres_vars_primal'])}

        **Restricciones:** {len(resultado['primal']['solucion'])} (aproximado)
        """)

    with col2:
        st.subheader("🔴 Problema DUAL")
        st.write(f"""
        **Tipo:** {resultado['tipo_dual'].upper()}

        **Variables:** {len(resultado['nombres_vars_dual'])}
        - {', '.join(resultado['nombres_vars_dual'])}

        **Restricciones:** {len(resultado['dual']['solucion'])} (aproximado)
        """)

    st.write("---")

    # SOLUCIONES
    st.markdown("<h2 class='section-header'>✅ Soluciones</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔵 Solución PRIMAL")
        if resultado['primal']['exito']:
            st.success(f"✓ Solución Óptima")
            st.metric("Z Primal", f"{resultado['primal']['valor_optimo']:.6f}")
            st.metric("Iteraciones", resultado['primal']['iteraciones'])

            primal_data = []
            for var, val in resultado['primal']['solucion'].items():
                primal_data.append({
                    'Variable': var,
                    'Valor': f"{val:.6f}",
                    'Estado': 'Básica' if val > 1e-6 else 'No Básica'
                })

            primal_df = pd.DataFrame(primal_data)
            st.dataframe(primal_df, use_container_width=True, hide_index=True)
        else:
            st.error("❌ No se encontró solución primal")
            if resultado['primal']['es_no_acotado']:
                st.write("Problema NO ACOTADO")
            if resultado['primal']['es_infactible']:
                st.write("Problema INFACTIBLE")

    with col2:
        st.subheader("🔴 Solución DUAL")
        if resultado['dual']['exito']:
            st.success(f"✓ Solución Óptima")
            st.metric("Z Dual", f"{resultado['dual']['valor_optimo']:.6f}")
            st.metric("Iteraciones", resultado['dual']['iteraciones'])

            dual_data = []
            for var, val in resultado['dual']['solucion'].items():
                dual_data.append({
                    'Variable': var,
                    'Valor': f"{val:.6f}",
                    'Estado': 'Básica' if val > 1e-6 else 'No Básica'
                })

            dual_df = pd.DataFrame(dual_data)
            st.dataframe(dual_df, use_container_width=True, hide_index=True)
        else:
            st.error("❌ No se encontró solución dual")
            if resultado['dual']['es_no_acotado']:
                st.write("Problema NO ACOTADO")
            if resultado['dual']['es_infactible']:
                st.write("Problema INFACTIBLE")

    st.write("---")

    # VERIFICACIÓN DE DUALIDAD FUERTE
    st.markdown("<h2 class='section-header'>🔍 Verificación de Dualidad Fuerte</h2>", unsafe_allow_html=True)

    if resultado['dualidad_fuerte']:
        st.markdown("""
        <div class='success-box'>
        <h4>✓ DUALIDAD FUERTE VERIFICADA</h4>
        <p>Los valores óptimos del problema primal y dual son iguales (dentro de tolerancia numérica).</p>
        <p>Esto confirma que ambos problemas tienen soluciones óptimas equivalentes.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Z Primal", f"{resultado['primal']['valor_optimo']:.6f}")
        with col2:
            st.metric("Z Dual", f"{resultado['dual']['valor_optimo']:.6f}")
        with col3:
            st.metric("Diferencia", f"{resultado['diferencia_valores_optimos']:.2e}")
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

    st.write("---")

    # TEORÍA DE DUALIDAD
    st.markdown("<h2 class='section-header'>📚 Información de Dualidad</h2>", unsafe_allow_html=True)

    st.write("""
    **Teorema de Dualidad Fuerte:**

    Si el problema PRIMAL tiene una solución óptima finita, entonces el problema DUAL también tiene 
    una solución óptima finita, y los valores óptimos de ambos son iguales:

    **Z_primal = Z_dual**

    **Relaciones de Complementariedad:**
    - Si una variable primal es positiva en la solución óptima, su restricción dual correspondiente 
      debe ser activa (satisfecha con igualdad)
    - Si una restricción primal es inactiva (variable de holgura > 0), la variable dual correspondiente 
      debe ser cero
    """)

    st.write("---")

    # RESUMEN EJECUTIVO
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Análisis Realizado:**
        - Tipo Primal: {resultado['tipo_primal_original'].upper()}
        - Tipo Dual: {resultado['tipo_dual'].upper()}
        - Variables Primal: {len(resultado['nombres_vars_primal'])}
        - Variables Dual: {len(resultado['nombres_vars_dual'])}
        """)

    with summary_col2:
        st.write(f"""
        **Resultados:**
        - Primal Óptimo: {'✓ Sí' if resultado['primal']['exito'] else '✗ No'}
        - Dual Óptimo: {'✓ Sí' if resultado['dual']['exito'] else '✗ No'}
        - Dualidad Fuerte: {'✓ Verificada' if resultado['dualidad_fuerte'] else '✗ No verificada'}
        - Iteraciones Primal: {resultado['primal']['iteraciones']}
        - Iteraciones Dual: {resultado['dual']['iteraciones']}
        """)