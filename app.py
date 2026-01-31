import streamlit as st
from views import (
    show_programacion_lineal,
    show_inventarios,
    show_historial,
    show_redes,
    show_transporte
)
from views.inicio_caso_empresarial import show_inicio_caso_empresarial

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Optimización Empresarial - Coca-Cola",
    page_icon="🏭",
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
        background-color: #000000;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #000000;
        border: 2px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
    }
    .error-box {
        background-color: #000000;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
    }
    .info-box {
        background-color: #000000;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .iteration-header {
        background-color: #000000;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: #000000;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
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
if 'resultado_actual' not in st.session_state:
    st.session_state.resultado_actual = None
if 'metodo_redes' not in st.session_state:
    st.session_state.metodo_redes = None
if 'metodo_transp' not in st.session_state:
    st.session_state.metodo_transp = None

# Header principal
st.markdown("<h1 class='main-header'>🏭 Sistema de Optimización Empresarial</h1>", unsafe_allow_html=True)
st.markdown("*Coca-Cola Embotelladora Nacional - Análisis Integral de Optimización*")

# Sidebar para navegación
st.sidebar.title("📋 Menú Principal")
menu_principal = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio - Caso Empresarial",
     "📈 Programación Lineal",
     "🌐 Problemas de Redes",
     "🚚 Problema de Transporte",
     "📦 Gestión de Inventarios",
     "📊 Historial de Resultados"]
)

# Mostrar la vista correspondiente según el menú seleccionado
if menu_principal == "🏠 Inicio - Caso Empresarial":
    show_inicio_caso_empresarial()

elif menu_principal == "📈 Programación Lineal":
    show_programacion_lineal()

elif menu_principal == "🌐 Problemas de Redes":
    show_redes()

elif menu_principal == "🚚 Problema de Transporte":
    show_transporte()

elif menu_principal == "📦 Gestión de Inventarios":
    show_inventarios()

elif menu_principal == "📊 Historial de Resultados":
    show_historial()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
    <p>Sistema de Optimización Empresarial - Investigación Operativa</p>
    <p>Caso de Estudio: Coca-Cola Embotelladora Nacional</p>
    <p>Implementación desde Cero - Sin Librerías de Optimización</p>
    <p>Métodos: Simplex | Gran M | Dos Fases | Dualidad | Redes | Transporte | Inventarios</p>
    <p>✨ Con visualización detallada de TODOS los pasos de cada algoritmo</p>
    <p>🤖 Análisis de Sensibilidad con Inteligencia Artificial</p>
</div>
""", unsafe_allow_html=True)