import streamlit as st
import pandas as pd


def show_historial():
    """Vista del historial de análisis"""
    st.markdown("<h2 class='section-header'>Historial de Análisis</h2>", unsafe_allow_html=True)

    if st.session_state.historial:
        historial_df = pd.DataFrame(st.session_state.historial)
        st.dataframe(historial_df, use_container_width=True, hide_index=True)

        if st.button("🗑️ Limpiar Historial"):
            st.session_state.historial = []
            st.rerun()
    else:
        st.info("📭 No hay análisis registrados aún")