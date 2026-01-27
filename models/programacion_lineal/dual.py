import numpy as np
from typing import List, Dict, Optional, Tuple
import pandas as pd


class Dual:
    """
    Implementación CORRECTA del Método de Dualidad para Programación Lineal

    TRANSFORMACIONES CORRECTAS SEGÚN TEORÍA MATEMÁTICA:

    REGLA: Si el PRIMAL es:
           op: c^T * x
           s.a: A * x ≤/≥/= b
                x ≥ 0

           El DUAL es el problema TRANSPUESTO con OPERADOR INVERTIDO

    CASO 1: PRIMAL MAX con <=
    max: c^T * x
    s.a: A * x <= b
         x >= 0

    DUAL (MIN):
    min: b^T * y
    s.a: A^T * y >= c
         y >= 0

    CASO 2: PRIMAL MIN con >=
    min: c^T * x
    s.a: A * x >= b
         x >= 0

    DUAL (MAX):
    max: b^T * y
    s.a: A^T * y <= c
         y >= 0

    CASO 3: PRIMAL MIN con <=
    min: c^T * x
    s.a: A * x <= b
         x >= 0

    DUAL (MAX):
    max: b^T * y
    s.a: A^T * y <= c
         y >= 0

    CASO 4: PRIMAL MAX con >=
    max: c^T * x
    s.a: A * x >= b
         x >= 0

    DUAL (MIN):
    min: b^T * y
    s.a: A^T * y >= c
         y >= 0
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str] = None, tipo: str = "max",
                 nombres_vars: List[str] = None, nombres_restricciones: List[str] = None):
        """
        Parámetros:
        - c: coeficientes de la función objetivo (Primal)
        - A: matriz de coeficientes de restricciones (Primal)
        - b: vector de lados derechos (Primal)
        - signos: lista de signos de restricciones
        - tipo: "max" o "min"
        - nombres_vars: nombres de variables primales
        - nombres_restricciones: nombres de restricciones primales
        """
        self.c_primal_original = np.array(c, dtype=float)
        self.A_primal_original = np.array(A, dtype=float)
        self.b_primal_original = np.array(b, dtype=float)
        self.tipo_primal_original = tipo.lower()

        self.m, self.n = self.A_primal_original.shape

        self.nombres_vars_primal = nombres_vars or [f"x{i + 1}" for i in range(self.n)]
        self.nombres_restricciones = nombres_restricciones or [f"R{i + 1}" for i in range(self.m)]

        # Signos de restricciones
        if signos is None:
            self.signos_primal_original = ["<="] * self.m
        else:
            self.signos_primal_original = signos

        # Variables de trabajo (después de normalizar)
        self.c_primal = None
        self.A_primal = None
        self.b_primal = None
        self.signos_primal = None
        self.tipo_primal_trabajo = None

        # Variables del dual
        self.c_dual = None
        self.A_dual = None
        self.b_dual = None
        self.signos_dual = None
        self.nombres_vars_dual = None
        self.tipo_dual_teorico = None

        # Soluciones
        self.solucion_primal = None
        self.solucion_dual = None
        self.valor_optimo_primal = None
        self.valor_optimo_dual = None

        self.es_optimo_primal = False
        self.es_optimo_dual = False
        self.es_no_acotado_primal = False
        self.es_no_acotado_dual = False
        self.es_infactible_primal = False
        self.es_infactible_dual = False

        self.tabla_primal = None
        self.tabla_dual = None
        self.base_primal = None
        self.base_dual = None

        self.iteraciones_primal = 0
        self.iteraciones_dual = 0

    def _construir_dual_teorico(self):
        """
        Construye el dual TEÓRICO según las reglas matemáticas.

        No normaliza, solo transpone correctamente.
        """
        # Variables duales: una por cada restricción del primal
        self.nombres_vars_dual = [f"y{i + 1}" for i in range(self.m)]

        # Función objetivo dual: b^T * y
        self.c_dual = self.b_primal_original.copy()

        # Matriz dual: A^T
        self.A_dual = self.A_primal_original.T.copy()

        # RHS del dual: c primal
        self.b_dual = self.c_primal_original.copy()

        # Determinar tipo y signos del dual según reglas
        if self.tipo_primal_original == "max":
            self.tipo_dual_teorico = "min"
            # MAX -> MIN invierte los signos de restricción
            # <= -> >=
            # >= -> <=
            self.signos_dual = []
            for signo in self.signos_primal_original:
                if signo == "<=":
                    self.signos_dual.append(">=")
                elif signo == ">=":
                    self.signos_dual.append("<=")
                else:  # "="
                    self.signos_dual.append("=")
        else:  # "min"
            self.tipo_dual_teorico = "max"
            # MIN -> MAX invierte los signos de restricción
            # <= -> <=
            # >= -> >=
            self.signos_dual = []
            for signo in self.signos_primal_original:
                if signo == "<=":
                    self.signos_dual.append("<=")
                elif signo == ">=":
                    self.signos_dual.append(">=")
                else:  # "="
                    self.signos_dual.append("=")

    def _normalizar_para_simplex(self, c, A, b, signos, tipo):
        """
        Convierte un problema a forma estándar para Simplex:
        max c*x s.a Ax <= b, x >= 0
        """
        c_norm = c.copy()
        A_norm = A.copy()
        b_norm = b.copy()
        signos_norm = signos.copy()

        # Si es MIN, convertir a MAX negando c
        if tipo == "min":
            c_norm = -c_norm

        # Procesar restricciones
        for i in range(len(signos_norm)):
            if signos_norm[i] == ">=":
                # Convertir >= a <= multiplicando por -1
                A_norm[i, :] = -A_norm[i, :]
                b_norm[i] = -b_norm[i]
                signos_norm[i] = "<="

        return c_norm, A_norm, b_norm, signos_norm

    def _encontrar_columna_pivote(self, tabla: np.ndarray) -> int:
        """Encuentra columna pivote (variable que entra)"""
        fila_costo = tabla[-1, :-1]
        col_negativas = np.where(fila_costo < -1e-10)[0]

        if len(col_negativas) == 0:
            return -1

        return col_negativas[np.argmin(fila_costo[col_negativas])]

    def _encontrar_fila_pivote(self, tabla: np.ndarray, col_pivote: int) -> int:
        """Encuentra fila pivote (variable que sale)"""
        col = tabla[:-1, col_pivote]
        b_vals = tabla[:-1, -1]

        razones = []
        for i in range(len(col)):
            if col[i] > 1e-10:
                razon = b_vals[i] / col[i]
                razones.append((razon, i))

        if not razones:
            return -1

        return min(razones)[1]

    def _pivotear(self, tabla: np.ndarray, fila_pivote: int, col_pivote: int):
        """Realiza operación de pivoteo"""
        pivote = tabla[fila_pivote, col_pivote]

        if abs(pivote) < 1e-10:
            raise ValueError("Elemento pivote muy pequeño")

        tabla[fila_pivote, :] /= pivote

        for i in range(tabla.shape[0]):
            if i != fila_pivote:
                factor = tabla[i, col_pivote]
                tabla[i, :] -= factor * tabla[fila_pivote, :]

    def _construir_tabla_simplex(self, c: np.ndarray, A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Construye tabla del Simplex"""
        tabla = np.hstack([A, b.reshape(-1, 1)])
        fila_costo = np.hstack([-c, 0])
        tabla = np.vstack([tabla, fila_costo])
        return tabla

    def _resolver_problema_simplex(self, c: np.ndarray, A: np.ndarray, b: np.ndarray,
                                   tipo_original: str) -> Tuple[bool, np.ndarray, np.ndarray, int]:
        """
        Resuelve un problema de PL usando Simplex.
        Retorna: (es_optimo, solucion, tabla, iteraciones)
        """
        # Normalizar para Simplex
        c_norm, A_norm, b_norm, _ = self._normalizar_para_simplex(c, A, b, ["<="] * len(b), tipo_original)

        # Agregar variables de holgura
        num_restricciones = A_norm.shape[0]
        num_variables_orig = A_norm.shape[1]

        A_extendida = np.hstack([A_norm, np.eye(num_restricciones)])
        c_extendida = np.concatenate([c_norm, np.zeros(num_restricciones)])

        tabla = self._construir_tabla_simplex(c_extendida, A_extendida, b_norm)

        # Base inicial: variables de holgura
        base = list(range(num_variables_orig, num_variables_orig + num_restricciones))

        iteraciones = 0
        max_iter = 1000

        while iteraciones < max_iter:
            col_pivote = self._encontrar_columna_pivote(tabla)

            if col_pivote == -1:
                # Es óptimo
                break

            fila_pivote = self._encontrar_fila_pivote(tabla, col_pivote)

            if fila_pivote == -1:
                # No acotado
                return False, None, tabla, iteraciones

            base[fila_pivote] = col_pivote
            self._pivotear(tabla, fila_pivote, col_pivote)
            iteraciones += 1

        # Extraer solución
        solucion = np.zeros(A_extendida.shape[1])
        for i, var_base in enumerate(base):
            solucion[var_base] = tabla[i, -1]

        return True, solucion[:num_variables_orig], tabla, iteraciones

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el primal y el dual, y verifica dualidad fuerte"""

        # Construir dual TEÓRICO (sin normalizar)
        self._construir_dual_teorico()

        if verbose:
            print(f"\n{'=' * 100}")
            print("MÉTODO DE DUALIDAD - VERSIÓN 3 (CORREGIDA)")
            print(f"{'=' * 100}")
            print(f"\nPRIMAL ORIGINAL:")
            print(f"  Tipo: {self.tipo_primal_original.upper()}")
            print(f"  c: {self.c_primal_original.tolist()}")
            print(f"  A: {self.A_primal_original.tolist()}")
            print(f"  b: {self.b_primal_original.tolist()}")
            print(f"  signos: {self.signos_primal_original}")

            print(f"\nDUAL TEÓRICO (SIN NORMALIZAR):")
            print(f"  Tipo: {self.tipo_dual_teorico.upper()}")
            print(f"  c: {self.c_dual.tolist()}")
            print(f"  A': {self.A_dual.tolist()}")
            print(f"  b: {self.b_dual.tolist()}")
            print(f"  signos: {self.signos_dual}")

        # Resolver PRIMAL (normalizado internamente)
        es_opt_p, sol_p, tab_p, iter_p = self._resolver_problema_simplex(
            self.c_primal_original, self.A_primal_original, self.b_primal_original,
            self.tipo_primal_original
        )

        self.es_optimo_primal = es_opt_p
        self.tabla_primal = tab_p
        self.iteraciones_primal = iter_p

        if es_opt_p and sol_p is not None:
            self.solucion_primal = sol_p
            z_p = -tab_p[-1, -1]

            # Ajustar si el primal original era MIN
            if self.tipo_primal_original == "min":
                z_p = -z_p

            self.valor_optimo_primal = z_p
        else:
            self.es_no_acotado_primal = True

        # Resolver DUAL (normalizado internamente)
        es_opt_d, sol_d, tab_d, iter_d = self._resolver_problema_simplex(
            self.c_dual, self.A_dual, self.b_dual,
            self.tipo_dual_teorico
        )

        self.es_optimo_dual = es_opt_d
        self.tabla_dual = tab_d
        self.iteraciones_dual = iter_d

        if es_opt_d and sol_d is not None:
            self.solucion_dual = sol_d
            z_d = -tab_d[-1, -1]

            # Ajustar según tipo dual
            if self.tipo_dual_teorico == "min":
                z_d = -z_d

            self.valor_optimo_dual = z_d
        else:
            self.es_no_acotado_dual = True

        # Verificar dualidad fuerte
        dualidad_fuerte = False
        diferencia = None

        if self.es_optimo_primal and self.es_optimo_dual:
            diferencia = abs(self.valor_optimo_primal - self.valor_optimo_dual)
            dualidad_fuerte = diferencia < 1e-4

            if verbose:
                print(f"\n{'-' * 100}")
                print("VERIFICACIÓN DE DUALIDAD FUERTE")
                print(f"{'-' * 100}")
                print(f"Z_primal = {self.valor_optimo_primal:.6f}")
                print(f"Z_dual = {self.valor_optimo_dual:.6f}")
                print(f"Diferencia = {diferencia:.6e}")
                if dualidad_fuerte:
                    print("✓ DUALIDAD FUERTE VERIFICADA")
                else:
                    print("⚠️ Dualidad fuerte no verificada")

        # Construir resultado
        resultado_primal = {
            'tipo': 'PRIMAL',
            'exito': self.es_optimo_primal,
            'valor_optimo': float(self.valor_optimo_primal) if self.valor_optimo_primal is not None else None,
            'solucion': {self.nombres_vars_primal[i]: float(self.solucion_primal[i])
                         for i in range(self.n)} if self.solucion_primal is not None else {},
            'iteraciones': self.iteraciones_primal,
            'es_optimo': self.es_optimo_primal,
            'es_no_acotado': self.es_no_acotado_primal,
            'es_infactible': self.es_infactible_primal
        }

        resultado_dual = {
            'tipo': 'DUAL',
            'exito': self.es_optimo_dual,
            'valor_optimo': float(self.valor_optimo_dual) if self.valor_optimo_dual is not None else None,
            'solucion': {self.nombres_vars_dual[i]: float(self.solucion_dual[i])
                         for i in range(self.m)} if self.solucion_dual is not None else {},
            'iteraciones': self.iteraciones_dual,
            'es_optimo': self.es_optimo_dual,
            'es_no_acotado': self.es_no_acotado_dual,
            'es_infactible': self.es_infactible_dual
        }

        return {
            'primal': resultado_primal,
            'dual': resultado_dual,
            'dualidad_fuerte': dualidad_fuerte,
            'diferencia_valores_optimos': float(diferencia) if diferencia is not None else None,
            'tipo_primal_original': self.tipo_primal_original,
            'tipo_dual': self.tipo_dual_teorico,
            'nombres_vars_primal': self.nombres_vars_primal,
            'nombres_vars_dual': self.nombres_vars_dual,
        }

    def obtener_comparacion_problemas(self) -> pd.DataFrame:
        """Retorna comparación entre primal y dual"""
        comparacion = {
            'Aspecto': [
                'Tipo Optimización',
                'Variables',
                'Restricciones',
                'Vector c',
                'Vector b',
                'Matriz A',
                'Signos Restricciones'
            ],
            'Primal': [
                self.tipo_primal_original.upper(),
                f"{self.n} variables: {', '.join(self.nombres_vars_primal)}",
                f"{self.m} restricciones",
                str([float(x) for x in self.c_primal_original]),
                str([float(x) for x in self.b_primal_original]),
                "Original",
                str(self.signos_primal_original)
            ],
            'Dual': [
                self.tipo_dual_teorico.upper(),
                f"{self.m} variables: {', '.join(self.nombres_vars_dual)}",
                f"{self.n} restricciones",
                str([float(x) for x in self.c_dual]),
                str([float(x) for x in self.b_dual]),
                "Transpuesta (A')",
                str(self.signos_dual)
            ]
        }

        return pd.DataFrame(comparacion)


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("EJEMPLO: PROBLEMA DE MINIMIZACIÓN CON RESTRICCIONES >=")
    print("=" * 100)

    print("\nProblem Dual (Minimización)")
    print("min: 18y₁ + 42y₂ + 24y₃")
    print("s.a: 2y₁ + 2y₂ + 3y₃ ≥ 3")
    print("     y₁ + 3y₂ + y₃ ≥ 2")
    print("     y₁, y₂, y₃ ≥ 0")

    # Datos del problema
    c = [18, 42, 24]
    A = [[2, 2, 3], [1, 3, 1]]
    b = [3, 2]
    signos = [">=", ">="]

    dual = Dual(c, A, b, signos=signos, tipo="min",
                nombres_vars=["y1", "y2", "y3"],
                nombres_restricciones=["Restriccion_1", "Restriccion_2"])

    resultado = dual.resolver(verbose=True)

    print("\n" + "=" * 100)
    print("RESULTADO")
    print("=" * 100)

    print("\n✅ SOLUCIÓN PRIMAL:")
    if resultado['primal']['exito']:
        print(f"W = {resultado['primal']['valor_optimo']:.6f}")
        for var, val in resultado['primal']['solucion'].items():
            print(f"  {var} = {val:.6f}")
    else:
        print("No se encontró solución")

    print(f"\n🔍 Dualidad Fuerte Verificada: {resultado['dualidad_fuerte']}")
    if resultado['dualidad_fuerte']:
        print(f"  Z_primal = {resultado['primal']['valor_optimo']:.6f}")
        print(f"  Z_dual = {resultado['dual']['valor_optimo']:.6f}")

    print("\n" + "=" * 100)
    print("COMPARACIÓN")
    print("=" * 100)
    print(dual.obtener_comparacion_problemas())