# views/resolucion_optimalidad.py

import streamlit as st
import pandas as pd
from models.transporte.optimalidad import OptimizadorTransporte


def mostrar_resolucion_optimalidad(costos, oferta, demanda, solucion_inicial, nombre_metodo):
    """
    Muestra la optimización de la solución inicial usando MODI + Stepping Stone
    """

    st.success("✅ Optimización de Solución Iniciada (MODI + Stepping Stone)")

    # INFORMACIÓN DEL MÉTODO
    st.write("---")
    st.markdown("<h2 class='section-header'>📚 Información del Método MODI</h2>",
                unsafe_allow_html=True)

    st.info("""
    **Método MODI (Modified Distribution Method):**
    1. Calcula potenciales u_i (filas) y v_j (columnas)
    2. Evalúa costos marginales de celdas no básicas (Δ_ij = c_ij - u_i - v_j)
    3. Si existe Δ_ij < 0, la solución puede mejorarse
    4. Usa Stepping Stone para encontrar el ciclo cerrado y ajustar asignaciones
    5. Repite hasta que todos los Δ_ij ≥ 0 (solución óptima)
    """)

    # SOLUCIÓN INICIAL
    st.write("---")
    st.markdown(f"<h2 class='section-header'>🔍 Solución Inicial (Método: {nombre_metodo})</h2>",
                unsafe_allow_html=True)

    solucion_inicial_df = pd.DataFrame(
        solucion_inicial,
        index=[f"O{i + 1}" for i in range(len(oferta))],
        columns=[f"D{j + 1}" for j in range(len(demanda))]
    )
    st.dataframe(solucion_inicial_df, use_container_width=True)

    # Costo inicial
    costo_inicial = 0
    for i in range(len(oferta)):
        for j in range(len(demanda)):
            costo_inicial += solucion_inicial[i][j] * costos[i][j]

    st.metric("💰 Costo Inicial", f"${costo_inicial:.2f}")

    # RESOLVER
    try:
        optimizador = OptimizadorTransporte(costos, solucion_inicial)
        resultado = optimizador.resolver()
        pasos = optimizador.pasos
    except Exception as e:
        st.error(f"Error durante la optimización: {str(e)}")
        return

    # ITERACIONES DE OPTIMIZACIÓN
    st.write("---")
    st.markdown("<h2 class='section-header'>🔄 Proceso de Optimización (MODI)</h2>",
                unsafe_allow_html=True)

    if pasos:
        # Filtrar pasos (excluir el final de óptimo)
        pasos_iteracion = [p for p in pasos if p.get('status') != 'optimo' and p.get('status') != 'error']

        if pasos_iteracion:
            tab_list = [f"Iteración {p['iteracion']}" for p in pasos_iteracion]
            tabs_iter = st.tabs(tab_list)

            for idx, tab in enumerate(tabs_iter):
                with tab:
                    paso = pasos_iteracion[idx]

                    st.markdown(
                        f"<div class='iteration-header'><h3>Iteración {paso['iteracion']}: Búsqueda de Mejora</h3></div>",
                        unsafe_allow_html=True)

                    # Potenciales
                    st.subheader("1️⃣ Cálculo de Potenciales (u, v)")

                    col_pot1, col_pot2 = st.columns(2)
                    with col_pot1:
                        st.write("**Potenciales de Filas (u):**")
                        st.code(", ".join(paso['u']))
                    with col_pot2:
                        st.write("**Potenciales de Columnas (v):**")
                        st.code(", ".join(paso['v']))

                    with st.expander("📖 Ver proceso de cálculo"):
                        st.markdown(paso['explicacion_potenciales'])

                    # Costos marginales
                    st.subheader("2️⃣ Evaluación de Costos Marginales")
                    st.markdown(paso['seleccion'])

                    with st.expander("📖 Ver todos los costos marginales"):
                        for exp in paso['marginales']:
                            st.text(exp)

                    # Ciclo y Theta
                    if paso.get('ciclo'):
                        st.subheader("3️⃣ Ciclo Cerrado (Stepping Stone)")
                        st.write(f"**Ciclo encontrado:** {paso['ciclo']}")

                        st.subheader("4️⃣ Cálculo de Theta (θ)")
                        st.markdown(paso['explicacion_theta'])

                        st.subheader("5️⃣ Ajuste de la Solución")
                        st.markdown(paso['explicacion_ajuste'])

                    # Matriz después de la iteración
                    st.subheader("📊 Matriz Después de Ajuste")
                    matriz_df = pd.DataFrame(
                        paso['matriz'],
                        index=[f"O{i + 1}" for i in range(len(oferta))],
                        columns=[f"D{j + 1}" for j in range(len(demanda))]
                    )
                    st.dataframe(matriz_df, use_container_width=True)

    # SOLUCIÓN ÓPTIMA
    st.write("---")
    st.markdown("<h2 class='section-header'>🏆 SOLUCIÓN ÓPTIMA ENCONTRADA</h2>",
                unsafe_allow_html=True)

    # Buscar paso óptimo
    paso_optimo = None
    for p in pasos:
        if p.get('status') == 'optimo':
            paso_optimo = p
            break

    if paso_optimo:
        st.success(paso_optimo['mensaje'])

        costo_optimo = optimizador.obtener_costo_total()
        mejora = costo_inicial - costo_optimo
        porcentaje_mejora = (mejora / costo_inicial) * 100 if costo_inicial > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Costo Óptimo", f"${costo_optimo:.2f}")
        with col2:
            st.metric("📉 Mejora", f"${mejora:.2f}")
        with col3:
            st.metric("📊 % Mejora", f"{porcentaje_mejora:.2f}%")
        with col4:
            st.metric("🔄 Iteraciones", paso_optimo['iteracion'])

        # Matriz óptima
        st.subheader("✅ Matriz Óptima Final")
        matriz_optima_df = pd.DataFrame(
            resultado,
            index=[f"O{i + 1}" for i in range(len(oferta))],
            columns=[f"D{j + 1}" for j in range(len(demanda))]
        )
        st.dataframe(matriz_optima_df, use_container_width=True)

        # Desglose de costos
        st.subheader("💹 Desglose de Costos Óptimos")
        desglose_data = []

        for i in range(len(oferta)):
            for j in range(len(demanda)):
                if resultado[i][j] > 0:
                    cant = resultado[i][j]
                    costo_unit = costos[i][j]
                    costo_total_asign = cant * costo_unit

                    desglose_data.append({
                        'Ruta': f"O{i + 1} → D{j + 1}",
                        'Cantidad': int(cant),
                        'Costo Unitario': f"${costo_unit:.2f}",
                        'Costo Total': f"${costo_total_asign:.2f}"
                    })

        if desglose_data:
            desglose_df = pd.DataFrame(desglose_data)
            st.dataframe(desglose_df, use_container_width=True, hide_index=True)

        # Verificación
        st.subheader("✔️ Verificación de Oferta y Demanda")

        verif_data = []
        for i in range(len(oferta)):
            suma_fila = sum(resultado[i])
            verif_data.append({
                'Origen': f"O{i + 1}",
                'Oferta': oferta[i],
                'Asignado': int(suma_fila),
                'Cumple': "✓" if suma_fila == oferta[i] else "✗"
            })

        for j in range(len(demanda)):
            suma_col = sum(resultado[i][j] for i in range(len(oferta)))
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

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.write("**Proceso:**")
        st.write(f"- Método Inicial: {nombre_metodo}")
        st.write("- Optimización: MODI")
        st.write("- Algoritmo Secundario: Stepping Stone")

    with summary_col2:
        st.write("**Mejoras:**")
        st.write(f"- Costo Inicial: ${costo_inicial:.2f}")
        st.write(f"- Costo Final: ${costo_optimo:.2f}")
        st.write(f"- Ahorro Total: ${mejora:.2f}")

    with summary_col3:
        iteraciones = paso_optimo['iteracion'] if paso_optimo else 0
        st.write("**Resultados:**")
        st.write(f"- Iteraciones: {iteraciones}")
        st.write(f"- Variables Básicas: {len(oferta) + len(demanda) - 1}")
        st.write("- Status: ✅ Óptimo")

    return resultado