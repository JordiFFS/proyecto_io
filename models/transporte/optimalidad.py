"""
models/transporte/optimalidad.py
Módulo: Prueba de Optimalidad (MODI + Stepping Stone)
Descripción: Implementación del método MODI (Modified Distribution) y Stepping Stone
             para verificar y mejorar la solución inicial del problema de transporte.
"""

import copy


class OptimizadorTransporte:
    """
    Clase para optimizar una solución inicial usando el Método MODI y Stepping Stone.

    El método MODI calcula los potenciales u y v para cada fila y columna, luego
    evalúa las celdas no básicas para ver si pueden mejorar la solución. Si se
    encuentra una mejora, usa Stepping Stone para ajustar la asignación.
    """

    def __init__(self, costos, solucion_inicial):
        """
        Inicializa el optimizador.

        Args:
            costos: Matriz de costos unitarios
            solucion_inicial: Matriz de solución inicial (obtenida de Vogel u otro método)
        """
        self.costos = copy.deepcopy(costos)
        self.solucion = copy.deepcopy(solucion_inicial)

        self.num_origenes = len(costos)
        self.num_destinos = len(costos[0])

        self.pasos = []
        self.iteracion = 0

    def obtener_celdas_basicas(self):
        """
        Identifica las celdas básicas (asignaciones > 0) en la solución actual.

        Returns:
            list: Lista de tuplas (i, j) con las posiciones de celdas básicas
        """
        basicas = []
        for i in range(self.num_origenes):
            for j in range(self.num_destinos):
                if self.solucion[i][j] > 0:
                    basicas.append((i, j))
        return basicas

    def calcular_potenciales_ui_vj(self):
        """
        Calcula los potenciales u_i (filas) y v_j (columnas) usando el método MODI.

        Para cada celda básica (i,j): u_i + v_j = c_ij

        Proceso:
        1. Se establece u_0 = 0 como punto de partida
        2. Se resuelve el sistema de ecuaciones para encontrar todos los u_i y v_j

        Returns:
            tuple: (lista_u, lista_v, explicación_proceso)
        """
        u = [None] * self.num_origenes
        v = [None] * self.num_destinos

        # Paso 1: Establecer u[0] = 0
        u[0] = 0
        explicaciones = ["**Cálculo de Potenciales u y v:**\n"]
        explicaciones.append("Paso 1: Establecemos u₁ = 0 como punto de partida\n")

        basicas = self.obtener_celdas_basicas()

        # Paso 2: Iterativamente calcular u's y v's
        cambios = True
        iteraciones_calculo = 0

        while cambios and iteraciones_calculo < 100:
            cambios = False
            iteraciones_calculo += 1

            for (i, j) in basicas:
                # Si u[i] está definido y v[j] no, calcular v[j]
                if u[i] is not None and v[j] is None:
                    v[j] = self.costos[i][j] - u[i]
                    explicaciones.append(
                        f"  v_{j + 1} = c_{i + 1},{j + 1} - u_{i + 1} = {self.costos[i][j]} - {u[i]} = {v[j]}"
                    )
                    cambios = True

                # Si v[j] está definido y u[i] no, calcular u[i]
                elif v[j] is not None and u[i] is None:
                    u[i] = self.costos[i][j] - v[j]
                    explicaciones.append(
                        f"  u_{i + 1} = c_{i + 1},{j + 1} - v_{j + 1} = {self.costos[i][j]} - {v[j]} = {u[i]}"
                    )
                    cambios = True

        # Asignar 0 a los potenciales que siguen siendo None (casos degenerados)
        for i in range(len(u)):
            if u[i] is None:
                u[i] = 0
                explicaciones.append(f"  u_{i + 1} = 0 (asignado por degeneración)")

        for j in range(len(v)):
            if v[j] is None:
                v[j] = 0
                explicaciones.append(f"  v_{j + 1} = 0 (asignado por degeneración)")

        explicacion_completa = "\n".join(explicaciones)

        return (u, v, explicacion_completa)

    def calcular_costos_marginales(self, u, v):
        """
        Calcula los costos marginales (costos reducidos) para todas las celdas no básicas.

        Costo marginal: Δ_ij = c_ij - (u_i + v_j)

        Si Δ_ij < 0, entonces la celda (i,j) puede mejorar la solución.

        Args:
            u: Lista de potenciales de filas
            v: Lista de potenciales de columnas

        Returns:
            tuple: (matriz_marginales, lista_explicaciones, celda_mejor, valor_mejor)
        """
        marginales = [[0 for _ in range(self.num_destinos)]
                      for _ in range(self.num_origenes)]

        explicaciones = []
        mejor_celda = None
        mejor_valor = 0  # Buscamos el más negativo

        for i in range(self.num_origenes):
            for j in range(self.num_destinos):
                if self.solucion[i][j] == 0:  # Solo celdas no básicas
                    marginal = self.costos[i][j] - (u[i] + v[j])
                    marginales[i][j] = marginal

                    explicacion = (
                        f"  Celda ({i + 1},{j + 1}): Δ = c_{i + 1},{j + 1} - (u_{i + 1} + v_{j + 1}) "
                        f"= {self.costos[i][j]} - ({u[i]} + {v[j]}) = {marginal}"
                    )

                    if marginal < 0:
                        explicacion += " ← **Puede mejorar**"
                        if marginal < mejor_valor:
                            mejor_valor = marginal
                            mejor_celda = (i, j)

                    explicaciones.append(explicacion)

        return (marginales, explicaciones, mejor_celda, mejor_valor)

    def encontrar_ciclo_cerrado(self, i_inicio, j_inicio):
        """
        Encuentra un ciclo cerrado comenzando en la celda (i_inicio, j_inicio).

        El ciclo alterna entre movimientos horizontales y verticales, pasando
        solo por celdas básicas (excepto la celda de inicio).

        Args:
            i_inicio: Fila de inicio (celda a mejorar)
            j_inicio: Columna de inicio

        Returns:
            list: Lista de tuplas (i, j, signo) representando el ciclo
                  signo = '+' para celdas donde se suma, '-' donde se resta
        """
        basicas = set(self.obtener_celdas_basicas())

        # Función recursiva para buscar el ciclo
        def buscar_ciclo(camino, horizontal):
            """
            Búsqueda recursiva del ciclo.

            Args:
                camino: Lista actual de celdas en el camino
                horizontal: True si el siguiente movimiento debe ser horizontal
            """
            i_actual, j_actual = camino[-1]

            # Si tenemos al menos 4 nodos y podemos volver al inicio
            if len(camino) >= 4:
                if horizontal and j_actual == j_inicio:
                    # Encontramos el ciclo
                    return camino
                elif not horizontal and i_actual == i_inicio:
                    return camino

            # Explorar posibles movimientos
            if horizontal:
                # Buscar en la misma fila
                for j in range(self.num_destinos):
                    if j != j_actual and ((i_actual, j) in basicas or (i_actual, j) == (i_inicio, j_inicio)):
                        if (i_actual, j) not in camino:
                            resultado = buscar_ciclo(camino + [(i_actual, j)], False)
                            if resultado:
                                return resultado
            else:
                # Buscar en la misma columna
                for i in range(self.num_origenes):
                    if i != i_actual and ((i, j_actual) in basicas or (i, j_actual) == (i_inicio, j_inicio)):
                        if (i, j_actual) not in camino:
                            resultado = buscar_ciclo(camino + [(i, j_actual)], True)
                            if resultado:
                                return resultado

            return None

        # Intentar encontrar el ciclo comenzando con movimiento horizontal
        ciclo = buscar_ciclo([(i_inicio, j_inicio)], True)

        if ciclo is None:
            # Intentar comenzando con movimiento vertical
            ciclo = buscar_ciclo([(i_inicio, j_inicio)], False)

        if ciclo is None:
            return None

        # Asignar signos alternados (+, -, +, -, ...)
        ciclo_con_signos = []
        for idx, (i, j) in enumerate(ciclo):
            signo = '+' if idx % 2 == 0 else '-'
            ciclo_con_signos.append((i, j, signo))

        return ciclo_con_signos

    def calcular_theta(self, ciclo):
        """
        Calcula el valor theta (cantidad máxima a reasignar) para el ciclo.

        Theta es el mínimo de las cantidades en las celdas con signo negativo.

        Args:
            ciclo: Lista de tuplas (i, j, signo)

        Returns:
            tuple: (theta, explicación)
        """
        valores_negativos = []

        for (i, j, signo) in ciclo:
            if signo == '-':
                valores_negativos.append((self.solucion[i][j], i, j))

        if not valores_negativos:
            return (0, "No hay celdas negativas en el ciclo")

        theta = min(valores_negativos, key=lambda x: x[0])

        explicacion = "**Cálculo de Theta (θ):**\n"
        explicacion += "Theta es el mínimo valor en las celdas con signo '-':\n"
        for val, i, j in valores_negativos:
            marca = " ← Mínimo" if val == theta[0] else ""
            explicacion += f"  Celda ({i + 1},{j + 1}): {val}{marca}\n"
        explicacion += f"\n**θ = {theta[0]}**"

        return (theta[0], explicacion)

    def ajustar_solucion_con_ciclo(self, ciclo, theta):
        """
        Ajusta la solución sumando y restando theta según el ciclo.

        Args:
            ciclo: Lista de tuplas (i, j, signo)
            theta: Cantidad a ajustar

        Returns:
            str: Explicación del ajuste
        """
        explicacion = "**Ajuste de la solución:**\n"

        for (i, j, signo) in ciclo:
            if signo == '+':
                self.solucion[i][j] += theta
                explicacion += f"  Celda ({i + 1},{j + 1}): {self.solucion[i][j] - theta} + {theta} = {self.solucion[i][j]}\n"
            else:
                self.solucion[i][j] -= theta
                explicacion += f"  Celda ({i + 1},{j + 1}): {self.solucion[i][j] + theta} - {theta} = {self.solucion[i][j]}\n"

        return explicacion

    def es_solucion_optima(self, marginales):
        """
        Verifica si la solución actual es óptima.

        La solución es óptima si todos los costos marginales son >= 0.

        Args:
            marginales: Matriz de costos marginales

        Returns:
            bool: True si es óptima
        """
        for i in range(self.num_origenes):
            for j in range(self.num_destinos):
                if self.solucion[i][j] == 0 and marginales[i][j] < 0:
                    return False
        return True

    def resolver(self):
        """
        Ejecuta el proceso completo de optimización con MODI y Stepping Stone.

        Returns:
            list: Matriz de solución óptima
        """
        self.pasos = []
        self.iteracion = 0
        max_iteraciones = 50

        while self.iteracion < max_iteraciones:
            self.iteracion += 1

            # Paso 1: Calcular potenciales
            u, v, explicacion_potenciales = self.calcular_potenciales_ui_vj()

            # Paso 2: Calcular costos marginales
            marginales, explic_marginales, mejor_celda, mejor_valor = self.calcular_costos_marginales(u, v)

            # Paso 3: Verificar optimalidad
            if mejor_celda is None:
                # ¡Solución óptima encontrada!
                paso_final = {
                    'iteracion': self.iteracion,
                    'status': 'optimo',
                    'u': [f"u_{i + 1}={u[i]}" for i in range(len(u))],
                    'v': [f"v_{j + 1}={v[j]}" for j in range(len(v))],
                    'mensaje': '✅ **SOLUCIÓN ÓPTIMA ALCANZADA**\n\nTodos los costos marginales son ≥ 0. No es posible mejorar más la solución.',
                    'matriz': copy.deepcopy(self.solucion)
                }
                self.pasos.append(paso_final)
                break

            # Paso 4: Encontrar ciclo cerrado
            i_mejor, j_mejor = mejor_celda
            ciclo = self.encontrar_ciclo_cerrado(i_mejor, j_mejor)

            if ciclo is None:
                # No se pudo encontrar ciclo (problema degenerado)
                paso = {
                    'iteracion': self.iteracion,
                    'status': 'error',
                    'mensaje': '⚠️ No se pudo encontrar un ciclo cerrado. Posible degeneración.'
                }
                self.pasos.append(paso)
                break

            # Paso 5: Calcular theta
            theta, explicacion_theta = self.calcular_theta(ciclo)

            # Paso 6: Ajustar solución
            explicacion_ajuste = self.ajustar_solucion_con_ciclo(ciclo, theta)

            # Guardar paso
            ciclo_texto = " → ".join([f"({i + 1},{j + 1}){s}" for i, j, s in ciclo])

            seleccion_texto = (
                f"**Celda seleccionada para mejorar:** ({i_mejor + 1}, {j_mejor + 1})\n"
                f"**Costo marginal:** Δ = {mejor_valor} < 0\n\n"
                f"Esta celda tiene el costo marginal más negativo, "
                f"por lo que introducirla en la base reducirá el costo total."
            )

            paso = {
                'iteracion': self.iteracion,
                'u': [f"u_{i + 1}={u[i]}" for i in range(len(u))],
                'v': [f"v_{j + 1}={v[j]}" for j in range(len(v))],
                'explicacion_potenciales': explicacion_potenciales,
                'marginales': explic_marginales,
                'seleccion': seleccion_texto,
                'ciclo': ciclo_texto,
                'theta': theta,
                'explicacion_theta': explicacion_theta,
                'explicacion_ajuste': explicacion_ajuste,
                'matriz': copy.deepcopy(self.solucion)
            }

            self.pasos.append(paso)

        return self.solucion

    def obtener_costo_total(self):
        """
        Calcula el costo total de la solución actual.

        Returns:
            float: Costo total
        """
        costo = 0
        for i in range(self.num_origenes):
            for j in range(self.num_destinos):
                costo += self.solucion[i][j] * self.costos[i][j]
        return costo