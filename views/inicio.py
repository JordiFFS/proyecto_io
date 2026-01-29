import streamlit as st


def show_inicio():
    """Vista de inicio del sistema"""
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