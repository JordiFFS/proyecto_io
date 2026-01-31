# empresa/caso_empresarial.py

"""
Caso Empresarial: Coca-Cola Embotelladora Nacional
Análisis integral de optimización para la industria de bebidas

Este módulo contiene la descripción detallada del problema empresarial,
la formulación matemática y los análisis correspondientes.
"""

import streamlit as st
import pandas as pd
from empresa.datos_empresa import *


class CasoEmpresarial:
    """Clase para gestionar el caso empresarial de Coca-Cola"""

    def __init__(self):
        self.empresa = EMPRESA_INFO
        self.plantas = PLANTAS
        self.centros = CENTROS_DISTRIBUCION
        self.puntos_venta = PUNTOS_VENTA
        self.productos = PRODUCTOS
        self.materias_primas = MATERIAS_PRIMAS

    def obtener_resumen_empresa(self):
        """Retorna un resumen de la empresa"""
        return {
            "nombre": self.empresa["nombre"],
            "tipo": self.empresa["tipo"],
            "ubicacion": self.empresa["ubicacion"],
            "empleados": self.empresa["empleados"],
            "plantas": len(self.plantas),
            "centros_distribucion": len(self.centros),
            "puntos_venta": len(self.puntos_venta),
            "productos": len(self.productos),
        }

    def obtener_capacidad_total_plantas(self):
        """Calcula la capacidad total de producción mensual"""
        total = 0
        for planta in self.plantas.values():
            total += planta["capacidad_mensual"]
        return total

    def obtener_demanda_total_mensual(self):
        """Calcula la demanda total mensual de todos los productos"""
        return sum(DEMANDA_MENSUAL.values())

    def obtener_info_productos(self):
        """Retorna información de productos"""
        data = []
        for cod, prod in self.productos.items():
            data.append({
                'Código': cod,
                'Producto': prod['nombre'],
                'Precio Venta': f"${prod['precio_venta']:.2f}",
                'Costo Producción': f"${prod['costo_produccion']:.2f}",
                'Margen': f"{prod['margen_bruto'] * 100:.1f}%",
                'Demanda Diaria': f"{prod['demanda_promedio_diaria']:,} botellas"
            })
        return pd.DataFrame(data)

    def obtener_info_plantas(self):
        """Retorna información de plantas"""
        data = []
        for cod, planta in self.plantas.items():
            data.append({
                'Código': cod,
                'Planta': planta['nombre'],
                'Ubicación': planta['ubicacion'],
                'Capacidad Mensual': f"{planta['capacidad_mensual']:,} botellas",
                'Costo Unitario': f"${planta['costo_produccion_unitario']:.2f}",
                'Eficiencia': f"{planta['eficiencia'] * 100:.0f}%",
                'Productos': ', '.join(planta['productos'])
            })
        return pd.DataFrame(data)

    def obtener_info_centros(self):
        """Retorna información de centros de distribución"""
        data = []
        for cod, centro in self.centros.items():
            data.append({
                'Código': cod,
                'Centro': centro['nombre'],
                'Ubicación': centro['ubicacion'],
                'Capacidad': f"{centro['capacidad_almacenamiento']:,} botellas",
                'Costo Almacén (diario)': f"${centro['costo_almacenamiento_diario']:.3f}/botella",
                'Punto Reorden': f"{centro['punto_reorden']:,} botellas"
            })
        return pd.DataFrame(data)

    def obtener_info_materias_primas(self):
        """Retorna información de materias primas"""
        data = []
        for cod, mp in self.materias_primas.items():
            perecedera = "Sí" if mp['perecedera'] else "No"
            data.append({
                'Código': cod,
                'Materia Prima': mp['nombre'],
                'Stock Actual': f"{mp['stock_actual']:,.0f}",
                'Stock Mínimo': f"{mp['stock_minimo']:,.0f}",
                'Stock Máximo': f"{mp['stock_maximo']:,.0f}",
                'Costo Unitario': f"${mp['costo_unitario']:.3f}",
                'Perecedera': perecedera
            })
        return pd.DataFrame(data)

    def calcular_indicadores_clave(self):
        """Calcula KPIs de la empresa"""
        capacidad_total = self.obtener_capacidad_total_plantas()
        demanda_total = self.obtener_demanda_total_mensual()

        return {
            "capacidad_total_plantas": capacidad_total,
            "demanda_total_mensual": demanda_total,
            "utilidad_capacidad": (demanda_total / capacidad_total) * 100,
            "num_plantas": len(self.plantas),
            "num_centros_distribucion": len(self.centros),
            "num_puntos_venta": len(self.puntos_venta),
            "num_productos": len(self.productos),
            "ingresos_potenciales_mensuales": sum(
                DEMANDA_MENSUAL[cod] * self.productos[cod]['precio_venta']
                for cod in DEMANDA_MENSUAL
            ),
        }


def mostrar_caso_empresarial():
    """Muestra el caso empresarial completo en Streamlit"""

    st.markdown("<h1 class='main-header'>🏭 Caso Empresarial: Coca-Cola</h1>",
                unsafe_allow_html=True)
    st.markdown("*Optimización Integral de Producción, Distribución e Inventarios*")

    caso = CasoEmpresarial()

    # ========================================================================
    # 1. PRESENTACIÓN DE LA EMPRESA
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>1️⃣ Información General de la Empresa</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏢 Empresa", EMPRESA_INFO["nombre"])
    with col2:
        st.metric("📍 Ubicación", EMPRESA_INFO["ubicacion"])
    with col3:
        st.metric("👥 Empleados", f"{EMPRESA_INFO['empleados']}")
    with col4:
        st.metric("🏭 Fundación", EMPRESA_INFO["fundacion"])

    st.write(f"**Descripción:** {EMPRESA_INFO['descripcion']}")

    # ========================================================================
    # 2. ESTRUCTURA OPERATIVA
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>2️⃣ Estructura Operativa</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏭 Plantas de Producción", len(PLANTAS))
    with col2:
        st.metric("📦 Centros de Distribución", len(CENTROS_DISTRIBUCION))
    with col3:
        st.metric("🛒 Puntos de Venta", len(PUNTOS_VENTA))

    # Información de plantas
    st.subheader("Plantas de Producción")
    st.dataframe(caso.obtener_info_plantas(), use_container_width=True, hide_index=True)

    # Información de centros de distribución
    st.subheader("Centros de Distribución")
    st.dataframe(caso.obtener_info_centros(), use_container_width=True, hide_index=True)

    # ========================================================================
    # 3. CARTERA DE PRODUCTOS
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>3️⃣ Cartera de Productos</h2>",
                unsafe_allow_html=True)

    st.dataframe(caso.obtener_info_productos(), use_container_width=True, hide_index=True)

    # ========================================================================
    # 4. PUNTOS DE VENTA Y MERCADOS
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>4️⃣ Puntos de Venta y Mercados</h2>",
                unsafe_allow_html=True)

    puntos_data = []
    for cod, punto in PUNTOS_VENTA.items():
        puntos_data.append({
            'Código': cod,
            'Punto de Venta': punto['nombre'],
            'Ubicación': punto['ubicacion'],
            'Demanda Diaria': f"{punto['demanda_diaria']:,} botellas",
            'Margen': f"{punto['margen'] * 100:.0f}%",
            'Tipo': punto['tipo']
        })

    st.dataframe(pd.DataFrame(puntos_data), use_container_width=True, hide_index=True)

    # ========================================================================
    # 5. MATERIAS PRIMAS E INVENTARIOS
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>5️⃣ Materias Primas e Inventarios</h2>",
                unsafe_allow_html=True)

    st.dataframe(caso.obtener_info_materias_primas(), use_container_width=True, hide_index=True)

    # ========================================================================
    # 6. INDICADORES CLAVE DE DESEMPEÑO
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>6️⃣ Indicadores Clave de Desempeño (KPIs)</h2>",
                unsafe_allow_html=True)

    kpis = caso.calcular_indicadores_clave()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Capacidad Total/Mes", f"{kpis['capacidad_total_plantas']:,.0f} botellas")
    with col2:
        st.metric("📈 Demanda Total/Mes", f"{kpis['demanda_total_mensual']:,.0f} botellas")
    with col3:
        st.metric("⚡ Utilidad Capacidad", f"{kpis['utilidad_capacidad']:.1f}%")
    with col4:
        st.metric("💰 Ingresos Potenciales", f"${kpis['ingresos_potenciales_mensuales']:,.2f}")

    # ========================================================================
    # 7. PROBLEMAS A RESOLVER
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>7️⃣ Problemas de Optimización a Resolver</h2>",
                unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 1. Programación Lineal: Planificación de Producción
    **Objetivo:** Maximizar la ganancia de producción respetando restricciones de capacidad

    - **Variables:** Cantidad a producir de cada producto en cada planta
    - **Restricciones:** Capacidad de plantas, demanda mínima a satisfacer
    - **Función Objetivo:** Maximizar ingresos - costos de producción

    ### 🚚 2. Transporte: Optimización de Envíos
    **Objetivo:** Minimizar costos de transporte desde plantas a centros y a puntos de venta

    - **Variables:** Cantidad a transportar en cada ruta
    - **Restricciones:** Oferta de plantas, demanda de centros/puntos
    - **Función Objetivo:** Minimizar costo total de transporte

    ### 🌐 3. Redes: Flujo Máximo y Costo Mínimo
    **Objetivo:** Determinar el flujo máximo desde plantas a mercados con mínimo costo

    - **Problema 3a - Ruta Más Corta:** Encontrar rutas más eficientes
    - **Problema 3b - Flujo Máximo:** Maximizar distribución con capacidades limitadas
    - **Problema 3c - Costo Mínimo:** Distribuir con mínimo costo total
    - **Problema 3d - Árbol Mínimo:** Conectar centros con mínima inversión

    ### 📦 4. Inventarios: Control de Materias Primas
    **Objetivo:** Gestionar eficientemente inventarios de materias primas perecederas

    - **Variables:** Cantidad a ordenar, punto de reorden
    - **Objetivo:** Minimizar costos mantenimiento vs. escasez
    - **Consideraciones:** Materia prima perecedera (jarabe - 180 días de vida útil)

    ### 🤖 5. Análisis de Sensibilidad con IA
    **Objetivo:** Evaluar impacto de variaciones en parámetros clave

    - Variaciones en precios de insumos
    - Cambios en demanda por región
    - Modificaciones en costos de transporte
    - Alteraciones en capacidades de plantas
    """)

    # ========================================================================
    # 8. METODOLOGÍA
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>8️⃣ Metodología de Solución</h2>",
                unsafe_allow_html=True)

    st.markdown("""
    **Paso 1: Formulación Matemática**
    - Definir variables de decisión
    - Establecer restricciones
    - Formular función objetivo

    **Paso 2: Resolución Computacional**
    - Utilizar métodos de Programación Lineal (Simplex, Gran M, Dos Fases)
    - Aplicar algoritmos de transporte (Vogel, Esquina Noroeste, MODI)
    - Implementar algoritmos de redes (Dijkstra, Kruskal, Ford-Fulkerson)

    **Paso 3: Análisis de Resultados**
    - Validar solución contra restricciones
    - Analizar eficiencia de utilización de recursos
    - Identificar cuellos de botella

    **Paso 4: Análisis de Sensibilidad**
    - Evaluar variaciones paramétricas
    - Determinar rangos de viabilidad
    - Proponer escenarios alternativos

    **Paso 5: Recomendaciones e Implementación**
    - Cuantificar ahorros potenciales
    - Proponer cambios operacionales
    - Estimar ROI de implementación
    """)

    # ========================================================================
    # 9. INFORMACIÓN ADICIONAL
    # ========================================================================

    st.write("---")
    st.markdown("<h2 class='section-header'>9️⃣ Información Operativa Adicional</h2>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏰ Horas Operación/Día", f"{HORAS_OPERACION_DIARIA}")
        st.metric("📅 Días Operación/Mes", f"{DIAS_OPERACION_MES}")
    with col2:
        st.metric("📅 Días Operación/Año", f"{DIAS_OPERACION_ANIO}")
        st.write("**Distribución Demanda Regional:**")
        for region, pct in DISTRIBUCION_DEMANDA_REGIONAL.items():
            st.write(f"- {region}: {pct * 100:.0f}%")
    with col3:
        st.write("**Horarios de Distribución:**")
        for ciudad, horario in HORARIOS_DISTRIBUCION.items():
            st.write(f"- {ciudad}: {horario['inicio']} a {horario['fin']}")