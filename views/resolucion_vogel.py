# views/resolucion_vogel.py

import streamlit as st
import pandas as pd
from models.transporte.vogel import MetodoVogel


def mostrar_resolucion_vogel(costos, oferta, demanda):
    """
    Muestra la resolución del método de Vogel paso a paso

    Args:
        costos: Matriz de costos unitarios
        oferta: Vector de oferta
        demanda: Vector de demanda
    """

    st.success("✅ Solución Inicial por Método de Vogel Calculada")

    # CONFIGURACIÓN DEL PROBLEMA
    st.write("---")
    st.markdown("<h2 class='section-header'>✅ Configuración del Problema</h2>",
                unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Orígenes", len(oferta))
    with col2:
        st.metric("🎯 Destinos", len(demanda))
    with col3:
        st.metric("📊 Total Oferta", sum(oferta))
    with col4:
        st.metric("📊 Total Demanda", sum(demanda))

    # INFORMACIÓN DEL MÉTODO
    st.info("""
    **Método de Vogel (VAM - Vogel's Approximation Method):**
    - Calcula penalizaciones (diferencia entre 2 costos mínimos) para filas y columnas
    - Asigna en la celda de menor costo de la fila/columna con mayor penalización
    - Genera soluciones iniciales mejor que esquina noroeste
    - Suele requerir menos iteraciones de optimización
    """)

    # MATRIZ DE COSTOS
    st.write("---")
    st.markdown("<h2 class='section-header'>💰 Matriz de Costos Unitarios</h2>",
                unsafe_allow_html=True)

    costos_df = pd.DataFrame(
        costos,
        index=[f"O{i + 1}" for i in range(len(oferta))],
        columns=[f"D{j + 1}" for j in range(len(demanda))]
    )
    st.dataframe(costos_df, use_container_width=True)

    # RESOLVER
    vogel = MetodoVogel(costos, oferta, demanda)
    asignacion = vogel.resolver()
    pasos = vogel.obtener_pasos()

    # ITERACIONES
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Iteraciones del Algoritmo</h2>",
                unsafe_allow_html=True)

    if pasos:
        tab_list = [f"Paso {p['iteracion']}" for p in pasos]
        tabs_iter = st.tabs(tab_list)

        for idx, tab in enumerate(tabs_iter):
            with tab:
                paso = pasos[idx]

                st.markdown(
                    f"<div class='iteration-header'><h3>Paso {paso['iteracion']}: Cálculo de Penalizaciones</h3></div>",
                    unsafe_allow_html=True)

                # Penalizaciones Filas
                st.subheader("📐 Penalizaciones de Filas")
                if paso['penal_filas_txt']:
                    penal_f_text = "\n".join(paso['penal_filas_txt'])
                    st.code(penal_f_text, language=None)
                else:
                    st.info("Sin penalizaciones de filas")

                # Penalizaciones Columnas
                st.subheader("📐 Penalizaciones de Columnas")
                if paso['penal_cols_txt']:
                    penal_c_text = "\n".join(paso['penal_cols_txt'])
                    st.code(penal_c_text, language=None)
                else:
                    st.info("Sin penalizaciones de columnas")

                # Decisión
                st.subheader("🔎 Decisión")
                st.write(paso['decision'])

                # Asignación
                st.subheader("✏️ Asignación Realizada")
                st.write(paso['asignacion'])

                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.metric("Celda", f"O{paso['celda'][0] + 1}-D{paso['celda'][1] + 1}")
                with col_info2:
                    st.metric("Cantidad", paso['cantidad'])
                with col_info3:
                    st.metric("Costo Unitario", f"${paso['costo_unitario']:.2f}")

                # Matriz actual
                st.subheader("📊 Matriz de Asignación Actual")
                matriz_df = pd.DataFrame(
                    paso['matriz'],
                    index=[f"O{i + 1}" for i in range(len(oferta))],
                    columns=[f"D{j + 1}" for j in range(len(demanda))]
                )
                st.dataframe(matriz_df, use_container_width=True)

    # SOLUCIÓN FINAL
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN INICIAL FINAL</h2>",
                unsafe_allow_html=True)

    costo_total = vogel.obtener_costo_total()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Costo Total", f"${costo_total:.2f}")
    with col2:
        st.metric("📦 Asignaciones", sum(1 for fila in asignacion for val in fila if val > 0))
    with col3:
        st.metric("🔍 Método", "Vogel (VAM)")

    st.subheader("✅ Matriz Final de Asignación")
    matriz_final_df = pd.DataFrame(
        asignacion,
        index=[f"O{i + 1}" for i in range(len(oferta))],
        columns=[f"D{j + 1}" for j in range(len(demanda))]
    )
    st.dataframe(matriz_final_df, use_container_width=True)

    # DESGLOSE DE COSTOS
    st.subheader("💹 Desglose de Costos por Asignación")
    desglose_data = []

    for i in range(len(oferta)):
        for j in range(len(demanda)):
            if asignacion[i][j] > 0:
                cant = asignacion[i][j]
                costo_unit = costos[i][j]
                costo_total_asign = cant * costo_unit

                desglose_data.append({
                    'Ruta': f"O{i + 1} → D{j + 1}",
                    'Cantidad': int(cant),
                    'Costo Unitario': f"${costo_unit:.2f}",
                    'Costo Total': f"${costo_total_asign:.2f}"
                })

    desglose_df = pd.DataFrame(desglose_data)
    st.dataframe(desglose_df, use_container_width=True, hide_index=True)

    # VERIFICACIÓN
    st.subheader("✔️ Verificación de Oferta y Demanda")

    verif_data = []
    for i in range(len(oferta)):
        suma_fila = sum(asignacion[i])
        verif_data.append({
            'Origen': f"O{i + 1}",
            'Oferta': oferta[i],
            'Asignado': int(suma_fila),
            'Cumple': "✓" if suma_fila == oferta[i] else "✗"
        })

    for j in range(len(demanda)):
        suma_col = sum(asignacion[i][j] for i in range(len(oferta)))
        verif_data.append({
            'Origen': f"D{j + 1}",
            'Oferta': demanda[j],
            'Asignado': int(suma_col),
            'Cumple': "✓" if suma_col == demanda[j] else "✗"
        })

    verif_df = pd.DataFrame(verif_data)
    st.dataframe(verif_df, use_container_width=True, hide_index=True)

    # RESUMEN
    st.write("---")
    st.markdown("<h2 class='section-header'>📊 Resumen Ejecutivo</h2>", unsafe_allow_html=True)

    summary_col1, summary_col2 = st.columns(2)
    with summary_col1:
        st.write(f"""
        **Problema:**
        - Método: Vogel (VAM)
        - Orígenes: {len(oferta)}
        - Destinos: {len(demanda)}
        - Oferta Total: {sum(oferta)}
        """)

    with summary_col2:
        st.write(f"""
        **Solución:**
        - Costo Total: ${costo_total:.2f}
        - Asignaciones: {sum(1 for fila in asignacion for val in fila if val > 0)}
        - Variables Básicas: {len(oferta) + len(demanda) - 1} (esperadas)
        """)

    return asignacion


def ejemplo_vogel():
    """Ejemplo de Vogel"""
    st.subheader("Ejemplo: Método de Vogel")
    st.write("""
    **Problema:** Distribuir mercancía desde 3 orígenes a 4 destinos.

    **Oferta:** O1=100, O2=150, O3=120
    **Demanda:** D1=80, D2=70, D3=90, D4=60
    """)

    if st.button("Ejecutar Ejemplo", key="ej_vogel_example"):
        costos = [
            [4, 6, 8, 6],
            [5, 4, 7, 5],
            [6, 5, 4, 6]
        ]
        oferta = [100, 150, 120]
        demanda = [80, 70, 90, 60]

        mostrar_resolucion_vogel(costos, oferta, demanda)