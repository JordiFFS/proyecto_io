# views/inicio_caso_empresarial.py

"""
Vista principal del caso empresarial de Coca-Cola
Se muestra al iniciar la aplicación
"""

import streamlit as st
from empresa.caso_empresarial import CasoEmpresarial, mostrar_caso_empresarial


def show_inicio_caso_empresarial():
    """Muestra el caso empresarial al inicio de la aplicación"""

    # Mostrar caso empresarial
    mostrar_caso_empresarial()

    # Sección de llamada a acción
    st.write("---")
    st.markdown("<h2 class='section-header'>🚀 Comienza el Análisis</h2>", unsafe_allow_html=True)

    st.info("""
    Esta aplicación te permite resolver los problemas de optimización descrito arriba.

    Utiliza el menú lateral para acceder a cada módulo:
    - **📈 Programación Lineal:** Optimiza la producción
    - **🚚 Problema de Transporte:** Minimiza costos de distribución
    - **🌐 Problemas de Redes:** Maximiza flujo de distribución
    - **📦 Gestión de Inventarios:** Controla materias primas
    - **🤖 Análisis de Sensibilidad:** Evalúa variaciones paramétricas
    """)

    st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #000000; border-radius: 10px;'>
        <h3>¿Cómo usar esta aplicación?</h3>
        <ol style='text-align: left; display: inline-block;'>
            <li><strong>Selecciona</strong> el módulo que deseas utilizar</li>
            <li><strong>Ingresa</strong> los datos o usa los valores predefinidos</li>
            <li><strong>Resuelve</strong> el problema con un clic</li>
            <li><strong>Analiza</strong> los resultados detalladamente</li>
            <li><strong>Toma decisiones</strong> basadas en las recomendaciones</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar próximos pasos
    st.write("---")
    st.markdown("<h2 class='section-header'>📋 Próximos Pasos Recomendados</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 1️⃣ Programación Lineal
        - Planifica la producción
        - Maximiza ganancias
        - Respeta capacidades
        """)

    with col2:
        st.markdown("""
        #### 2️⃣ Transporte
        - Optimiza envíos
        - Minimiza costos
        - Satisface demanda
        """)

    with col3:
        st.markdown("""
        #### 3️⃣ Redes
        - Maximiza distribución
        - Reduce tiempos
        - Optimiza flujos
        """)