import streamlit as st
import numpy as np


def show_inventarios():
    """Vista de gestión de inventarios"""
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