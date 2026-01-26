import numpy as np
from typing import Tuple, List, Dict, Optional
import pandas as pd


class Simplex:
    """
    Implementación del Método Simplex para Programación Lineal
    Resuelve problemas de la forma:
    max/min: c^T * x
    s.a: A * x <= b
         x >= 0
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 tipo: str = "max", nombres_vars: List[str] = None):
        """
        Parámetros:
        - c: coeficientes de la función objetivo
        - A: matriz de coeficientes de restricciones
        - b: vector de lados derechos
        - tipo: "max" o "min"
        - nombres_vars: nombres de variables (opcional)
        """
        self.c_original = np.array(c, dtype=float)
        self.c = self.c_original.copy()
        self.A_original = np.array(A, dtype=float)
        self.A = self.A_original.copy()
        self.b = np.array(b, dtype=float)
        self.tipo = tipo.lower()
        self.m, self.n = self.A.shape  # m restricciones, n variables

        # Ajustar para minimización (multiplicar por -1)
        if self.tipo == "min":
            self.c = -self.c

        self.nombres_vars = nombres_vars or [f"x{i + 1}" for i in range(self.n)]
        self.tabla_simplex = None
        self.base = None
        self.solucion = None
        self.valor_optimo = None
        self.es_optimo = False
        self.iteraciones = 0
        self.historial_iteraciones = []

    def _construir_tabla_inicial(self) -> np.ndarray:
        """Construye la tabla inicial del simplex con variables de holgura"""
        # Agregar variables de holgura (m variables nuevas)
        I = np.eye(self.m)

        # Matriz extendida: [A | I | b]
        tabla = np.hstack([self.A, I, self.b.reshape(-1, 1)])

        # Agregar fila de costos (función objetivo):
        # [-c | 0 | 0] donde los ceros corresponden a las variables de holgura
        fila_costo = np.hstack([-self.c, np.zeros(self.m), 0])
        tabla = np.vstack([tabla, fila_costo])

        return tabla

    def _encontrar_columna_pivote(self) -> int:
        """
        Encuentra la columna pivote (variable que entra en base)
        Usa regla de Dantzig: selecciona la columna con el coeficiente más negativo
        """
        fila_costo = self.tabla_simplex[-1, :-1]
        col_negativas = np.where(fila_costo < -1e-10)[0]  # Usar tolerancia numérica

        if len(col_negativas) == 0:
            return -1  # Solución óptima encontrada

        # Regla de Dantzig: máximo coeficiente negativo (más negativo)
        idx_min = np.argmin(fila_costo[col_negativas])
        return col_negativas[idx_min]

    def _encontrar_fila_pivote(self, col_pivote: int) -> int:
        """
        Encuentra la fila pivote (variable que sale de base)
        Usa método de razones mínimas
        """
        col = self.tabla_simplex[:-1, col_pivote]
        b_vals = self.tabla_simplex[:-1, -1]

        # Calcular razones solo para elementos positivos
        razones = []
        for i in range(len(col)):
            if col[i] > 1e-10:  # Solo considerar elementos positivos
                razon = b_vals[i] / col[i]
                razones.append((razon, i))

        if not razones:
            return -1  # Problema no acotado

        # Seleccionar la razón mínima
        return min(razones)[1]

    def _pivotear(self, fila_pivote: int, col_pivote: int):
        """
        Realiza la operación de pivoteo (operaciones de fila elementales)
        """
        # Elemento pivote
        pivote = self.tabla_simplex[fila_pivote, col_pivote]

        if abs(pivote) < 1e-10:
            raise ValueError("Elemento pivote muy pequeño")

        # 1. Dividir la fila pivote por el elemento pivote
        self.tabla_simplex[fila_pivote, :] /= pivote

        # 2. Eliminación gaussiana: hacer ceros en el resto de la columna
        for i in range(self.tabla_simplex.shape[0]):
            if i != fila_pivote:
                factor = self.tabla_simplex[i, col_pivote]
                self.tabla_simplex[i, :] -= factor * self.tabla_simplex[fila_pivote, :]

    def resolver(self, verbose: bool = False) -> Dict:
        """
        Resuelve el problema de programación lineal
        """
        self.tabla_simplex = self._construir_tabla_inicial()

        # Inicializar base con variables de holgura
        # Las primeras m variables básicas son las de holgura (índices n a n+m-1)
        self.base = list(range(self.n, self.n + self.m))

        if verbose:
            print(f"\n{'=' * 80}")
            print(f"RESOLVIENDO PROBLEMA DE PROGRAMACIÓN LINEAL")
            print(f"{'=' * 80}")
            print(f"Tipo: {self.tipo.upper()}")
            print(f"Variables: {self.m} restricciones, {self.n} variables de decisión")
            print(f"\nTabla Inicial:")
            self._mostrar_tabla()

        max_iteraciones = 1000

        while self.iteraciones < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote()

            if col_pivote == -1:
                self.es_optimo = True
                if verbose:
                    print(f"\n✓ Solución óptima encontrada en iteración {self.iteraciones}")
                break

            fila_pivote = self._encontrar_fila_pivote(col_pivote)

            if fila_pivote == -1:
                # Problema no acotado
                return {'exito': False, 'mensaje': 'Problema no acotado'}

            # Actualizar base
            var_sale = self.base[fila_pivote]
            var_entra = col_pivote
            self.base[fila_pivote] = col_pivote

            # Pivotear
            self._pivotear(fila_pivote, col_pivote)
            self.iteraciones += 1

            if verbose:
                print(f"\nIteración {self.iteraciones}:")
                print(f"  Variable entra: x{var_entra + 1} (columna {var_entra})")
                print(f"  Variable sale: s{var_sale - self.n + 1 if var_sale >= self.n else var_sale + 1}")
                print(f"  Pivote: fila {fila_pivote}, columna {col_pivote}")
                self._mostrar_tabla()

        if self.es_optimo:
            self._extraer_solucion()

        return self._generar_resultado()

    def _extraer_solucion(self):
        """Extrae la solución óptima de la tabla final"""
        # Inicializar solución con ceros
        self.solucion = np.zeros(self.n)

        # Llenar solución: para cada variable en la base
        for i, var_base in enumerate(self.base):
            if var_base < self.n:  # Solo variables de decisión
                self.solucion[var_base] = self.tabla_simplex[i, -1]

        # Valor óptimo (ajustar por minimización)
        # En la tabla, el valor óptimo está en tabla_simplex[-1, -1]
        valor = -self.tabla_simplex[-1, -1]

        # Si es minimización, se multiplicó por -1 al inicio, así que ajustar
        if self.tipo == "min":
            self.valor_optimo = -valor  # Devolver al negativo original
        else:
            self.valor_optimo = valor

    def _generar_resultado(self) -> Dict:
        """Genera el resultado final"""
        # Crear diccionario de solución
        solucion_dict = {}
        for i in range(self.n):
            solucion_dict[self.nombres_vars[i]] = float(self.solucion[i])

        # Agregar variables de holgura
        for i in range(self.m):
            if self.base[i] >= self.n:
                var_holgura_idx = self.base[i] - self.n
                solucion_dict[f's{var_holgura_idx + 1}'] = float(self.tabla_simplex[i, -1])

        resultado = {
            'exito': self.es_optimo,
            'valor_optimo': float(self.valor_optimo) if self.valor_optimo is not None else None,
            'solucion': solucion_dict,
            'solucion_variables': {self.nombres_vars[i]: float(self.solucion[i])
                                   for i in range(self.n)},
            'iteraciones': self.iteraciones,
            'tabla_final': self.tabla_simplex.tolist() if self.tabla_simplex is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo
        }
        return resultado

    def _get_nombres_base(self) -> List[str]:
        """Obtiene los nombres de las variables en la base final"""
        nombres = []
        for i, var_idx in enumerate(self.base):
            if var_idx < self.n:
                nombres.append(self.nombres_vars[var_idx])
            else:
                nombres.append(f"s{var_idx - self.n + 1}")
        return nombres

    def _mostrar_tabla(self):
        """Muestra la tabla actual de forma legible"""
        nombres_cols = (
                [f"x{i + 1}" for i in range(self.n)] +
                [f"s{i + 1}" for i in range(self.m)] +
                ["RHS"]
        )

        nombres_filas = [
                            self.nombres_vars[i] if i < self.n else f"s{i - self.n + 1}"
                            for i in self.base
                        ] + ["Z"]

        df = pd.DataFrame(
            self.tabla_simplex,
            columns=nombres_cols,
            index=nombres_filas
        )

        print("\n" + df.to_string())

    def obtener_tabla_pandas(self) -> Optional[pd.DataFrame]:
        """Retorna la tabla final en formato pandas"""
        if self.tabla_simplex is None:
            return None

        nombres_cols = (
                [f"x{i + 1}" for i in range(self.n)] +
                [f"s{i + 1}" for i in range(self.m)] +
                ["RHS"]
        )

        nombres_filas = self._get_nombres_base() + ["Z"]

        return pd.DataFrame(self.tabla_simplex, columns=nombres_cols, index=nombres_filas)


# Ejemplo de uso - Probando con tu problema
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PRUEBA: Problema de Programación Lineal")
    print("=" * 80)
    print("\nFunción Objetivo: max 5x₁ + 4x₂")
    print("\nRestricciones:")
    print("  6x₁ + 4x₂ ≤ 24")
    print("  x₁ + 2x₂ ≤ 6")
    print("  x₂ ≤ 2")
    print("  x₂ - x₁ ≤ 1")
    print("  x₁, x₂ ≥ 0")

    # Definir el problema
    # max: 5x1 + 4x2
    # s.a: 6x1 + 4x2 <= 24
    #      x1 + 2x2 <= 6
    #      x2 <= 2
    #      -x1 + x2 <= 1
    #      x1, x2 >= 0

    c = [5, 4]
    A = [
        [6, 4],
        [1, 2],
        [0, 1],
        [-1, 1]
    ]
    b = [24, 6, 2, 1]

    simplex = Simplex(c, A, b, tipo="max", nombres_vars=["x1", "x2"])
    resultado = simplex.resolver(verbose=True)

    print("\n" + "=" * 80)
    print("RESULTADOS FINALES")
    print("=" * 80)

    if resultado['exito']:
        print(f"\n✓ Problema resuelto exitosamente")
        print(f"\nValor Óptimo: Z = {resultado['valor_optimo']:.4f}")
        print(f"\nSolución Óptima:")
        for var, valor in resultado['solucion_variables'].items():
            print(f"  {var} = {valor:.4f}")
        print(f"\nVariables de Holgura:")
        for var, valor in resultado['solucion'].items():
            if var.startswith('s'):
                print(f"  {var} = {valor:.4f}")
        print(f"\nIteraciones realizadas: {resultado['iteraciones']}")
    else:
        print(f"\n✗ Error: {resultado.get('mensaje', 'Error desconocido')}")

    print(f"\nTabla Final:")
    print(simplex.obtener_tabla_pandas())

    print("\n" + "=" * 80)
    print("VERIFICACIÓN CON VALORES ESPERADOS")
    print("=" * 80)
    print("Esperado: Z = 21, x₁ = 3, x₂ = 1.5")
    print(f"Obtenido: Z = {resultado['valor_optimo']:.1f}, ", end="")
    print(f"x₁ = {resultado['solucion_variables'].get('x1', 0):.1f}, ", end="")
    print(f"x₂ = {resultado['solucion_variables'].get('x2', 0):.1f}")