import numpy as np
from typing import List, Dict, Optional
import pandas as pd


class DosFases:
    """
    Implementación del Método de Dos Fases para Programación Lineal

    Resuelve problemas con restricciones de tipo >=, <= y =

    max/min: c^T * x
    s.a: A₁ * x <= b₁  (restricciones <=)
         A₂ * x >= b₂  (restricciones >=)
         A₃ * x = b₃   (restricciones =)
         x >= 0

    FASE 1: Encontrar una solución básica factible (sin variables artificiales)
    FASE 2: Optimizar usando la función objetivo original
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str], tipo: str = "max",
                 nombres_vars: List[str] = None):
        """
        Parámetros:
        - c: coeficientes de la función objetivo
        - A: matriz de coeficientes de restricciones
        - b: vector de lados derechos
        - signos: lista de signos ('<=', '>=', '=')
        - tipo: "max" o "min"
        - nombres_vars: nombres de variables (opcional)
        """
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.signos = signos
        self.tipo = tipo.lower()
        self.m, self.n = self.A_original.shape

        self.nombres_vars = nombres_vars or [f"x{i + 1}" for i in range(self.n)]

        # Matrices modificadas
        self.c = None
        self.A = None
        self.b = None

        # Variables para el algoritmo
        self.num_holgura = 0
        self.num_exceso = 0
        self.num_artificiales = 0
        self.var_artificiales_indices = []
        self.mapeo_columnas = {}

        # Tablas y resultados
        self.tabla_fase1 = None
        self.tabla_fase2 = None
        self.base = None
        self.solucion = None
        self.valor_optimo = None

        self.es_optimo = False
        self.es_no_acotado = False
        self.es_infactible = False

        self.iteraciones_fase1 = 0
        self.iteraciones_fase2 = 0

    def _preparar_problema(self):
        """Prepara el problema agregando variables de holgura, exceso y artificiales"""
        self.A = self.A_original.copy()
        self.c = self.c_original.copy()
        self.b = self.b_original.copy()

        if self.tipo == "min":
            self.c = -self.c

        nuevas_cols = []
        indices_vars_artificiales = []
        col_idx = self.n

        for i in range(self.n):
            self.mapeo_columnas[i] = self.nombres_vars[i]

        for i, signo in enumerate(self.signos):
            if signo == "<=":
                col_holgura = np.zeros(self.m)
                col_holgura[i] = 1
                nuevas_cols.append(col_holgura)
                self.mapeo_columnas[col_idx] = f"s{i + 1}"
                self.num_holgura += 1
                col_idx += 1

            elif signo == ">=":
                col_exceso = np.zeros(self.m)
                col_exceso[i] = -1
                nuevas_cols.append(col_exceso)
                self.mapeo_columnas[col_idx] = f"e{i + 1}"
                self.num_exceso += 1
                col_idx += 1

                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                col_idx += 1

            elif signo == "=":
                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                col_idx += 1

        if nuevas_cols:
            matriz_nuevas = np.column_stack(nuevas_cols)
            self.A = np.hstack([self.A, matriz_nuevas])

        # Extender c con ceros para nuevas variables
        nuevos_coefs = np.zeros(self.A.shape[1] - len(self.c))
        self.c = np.concatenate([self.c, nuevos_coefs])

        self.var_artificiales_indices = indices_vars_artificiales

    def _construir_tabla_fase1(self) -> np.ndarray:
        """Construye tabla para Fase 1 (minimizar suma de variables artificiales)"""
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])

        # Función objetivo Fase 1: minimizar suma de artificiales
        c_fase1 = np.zeros(self.A.shape[1])
        for idx in self.var_artificiales_indices:
            c_fase1[idx] = 1  # Coeficiente 1 para variables artificiales

        fila_costo = np.hstack([-c_fase1, 0])
        tabla = np.vstack([tabla, fila_costo])

        return tabla

    def _construir_tabla_fase2(self) -> np.ndarray:
        """Construye tabla para Fase 2 (función objetivo original)"""
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])

        fila_costo = np.hstack([-self.c, 0])
        tabla = np.vstack([tabla, fila_costo])

        return tabla

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

    def _fase1(self) -> bool:
        """
        Fase 1: Encontrar solución básica factible
        Retorna True si es factible, False si es infactible
        """
        self.tabla_fase1 = self._construir_tabla_fase1()

        # Inicializar base con variables artificiales
        self.base = []
        col_actual = self.n

        for i in range(self.m):
            if self.signos[i] == "<=":
                self.base.append(col_actual)
                col_actual += 1
            elif self.signos[i] == ">=" or self.signos[i] == "=":
                if self.signos[i] == ">=":
                    col_actual += 1
                self.base.append(col_actual)
                col_actual += 1

        max_iteraciones = 1000

        while self.iteraciones_fase1 < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote(self.tabla_fase1)

            if col_pivote == -1:
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase1, col_pivote)

            if fila_pivote == -1:
                return False

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase1, fila_pivote, col_pivote)
            self.iteraciones_fase1 += 1

        # Verificar si es factible (todas las artificiales = 0)
        valor_fase1 = -self.tabla_fase1[-1, -1]

        if valor_fase1 > 1e-6:
            return False  # Infactible

        return True  # Factible

    def _fase2(self):
        """Fase 2: Optimizar con función objetivo original"""
        self.tabla_fase2 = self._construir_tabla_fase2()

        # Actualizar fila Z basada en base actual
        for i, var_base in enumerate(self.base):
            if var_base < self.A.shape[1]:
                self.tabla_fase2[-1, :] -= self.c[var_base] * self.tabla_fase2[i, :]

        max_iteraciones = 1000

        while self.iteraciones_fase2 < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote(self.tabla_fase2)

            if col_pivote == -1:
                self.es_optimo = True
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase2, col_pivote)

            if fila_pivote == -1:
                self.es_no_acotado = True
                break

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase2, fila_pivote, col_pivote)
            self.iteraciones_fase2 += 1

    def _extraer_solucion(self):
        """Extrae la solución óptima"""
        self.solucion = np.zeros(self.n)

        for i, var_base in enumerate(self.base):
            if var_base < self.n:
                self.solucion[var_base] = self.tabla_fase2[i, -1]

        valor = -self.tabla_fase2[-1, -1]

        if self.tipo == "min":
            self.valor_optimo = -valor
        else:
            self.valor_optimo = valor

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el problema usando Dos Fases"""
        self._preparar_problema()

        if verbose:
            print(f"\n{'=' * 80}")
            print(f"MÉTODO DE DOS FASES")
            print(f"{'=' * 80}")

        # FASE 1
        if verbose:
            print(f"\nFASE 1: Encontrar solución básica factible")

        es_factible = self._fase1()

        if not es_factible:
            self.es_infactible = True
            if verbose:
                print("❌ Problema INFACTIBLE - No existe solución factible")

            return {
                'exito': False,
                'es_infactible': True,
                'es_no_acotado': False,
                'estado': 'INFACTIBLE',
                'valor_optimo': None,
                'solucion': {},
                'solucion_variables': {},
                'iteraciones': self.iteraciones_fase1,
                'tabla_fase1': self.tabla_fase1.tolist() if self.tabla_fase1 is not None else None,
                'tabla_fase2': None,
                'base_final': self._get_nombres_base(),
                'tipo_optimizacion': self.tipo,
                'metodo': 'Dos Fases'
            }

        if verbose:
            print(f"✓ Solución factible encontrada en {self.iteraciones_fase1} iteraciones")

        # FASE 2
        if verbose:
            print(f"\nFASE 2: Optimizar función objetivo")

        self._fase2()

        if self.es_optimo or self.es_no_acotado:
            self._extraer_solucion()

        # Determinar estado
        if self.es_optimo:
            estado = "ÓPTIMO"
        elif self.es_no_acotado:
            estado = "NO ACOTADO"
        else:
            estado = "ERROR"

        if verbose:
            if self.es_optimo:
                print(f"✓ Solución óptima encontrada en {self.iteraciones_fase2} iteraciones")
            elif self.es_no_acotado:
                print(f"⚠️ Problema NO ACOTADO")

        # Generar resultado
        solucion_dict = {}
        for i in range(self.n):
            solucion_dict[self.nombres_vars[i]] = float(self.solucion[i])

        col_idx = self.n
        for i, signo in enumerate(self.signos):
            if signo == "<=":
                var_holgura = f"s{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_holgura] = float(self.tabla_fase2[pos, -1])
                else:
                    solucion_dict[var_holgura] = 0.0
                col_idx += 1

            elif signo == ">=":
                var_exceso = f"e{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_exceso] = float(self.tabla_fase2[pos, -1])
                else:
                    solucion_dict[var_exceso] = 0.0
                col_idx += 1

                var_artificial = f"a{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_artificial] = float(self.tabla_fase2[pos, -1])
                else:
                    solucion_dict[var_artificial] = 0.0
                col_idx += 1

            elif signo == "=":
                var_artificial = f"a{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_artificial] = float(self.tabla_fase2[pos, -1])
                else:
                    solucion_dict[var_artificial] = 0.0
                col_idx += 1

        return {
            'exito': self.es_optimo,
            'es_infactible': self.es_infactible,
            'es_no_acotado': self.es_no_acotado,
            'estado': estado,
            'valor_optimo': float(self.valor_optimo) if self.valor_optimo is not None else None,
            'solucion': solucion_dict,
            'solucion_variables': {self.nombres_vars[i]: float(self.solucion[i]) for i in range(self.n)},
            'iteraciones': self.iteraciones_fase1 + self.iteraciones_fase2,
            'iteraciones_fase1': self.iteraciones_fase1,
            'iteraciones_fase2': self.iteraciones_fase2,
            'tabla_fase1': self.tabla_fase1.tolist() if self.tabla_fase1 is not None else None,
            'tabla_fase2': self.tabla_fase2.tolist() if self.tabla_fase2 is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo,
            'metodo': 'Dos Fases'
        }

    def _get_nombres_base(self) -> List[str]:
        """Obtiene nombres de variables en la base"""
        nombres = []
        for var_idx in self.base:
            nombres.append(self.mapeo_columnas.get(var_idx, f"var{var_idx}"))
        return nombres

    def obtener_tabla_fase1_pandas(self) -> Optional[pd.DataFrame]:
        """Retorna tabla Fase 1 en formato pandas"""
        if self.tabla_fase1 is None:
            return None

        nombres_cols = []
        for i in range(self.tabla_fase1.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = self._get_nombres_base() + ["Z"]

        return pd.DataFrame(self.tabla_fase1, columns=nombres_cols, index=nombres_filas)

    def obtener_tabla_fase2_pandas(self) -> Optional[pd.DataFrame]:
        """Retorna tabla Fase 2 en formato pandas"""
        if self.tabla_fase2 is None:
            return None

        nombres_cols = []
        for i in range(self.tabla_fase2.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = self._get_nombres_base() + ["Z"]

        return pd.DataFrame(self.tabla_fase2, columns=nombres_cols, index=nombres_filas)


# Ejemplo de uso
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PRUEBA: MÉTODO DE DOS FASES")
    print("=" * 80)

    print("\nProblema:")
    print("min: 2x₁ + 3x₂")
    print("s.a: x₁ + x₂ ≥ 5")
    print("     x₁ ≥ 2")
    print("     x₂ ≥ 1")

    c = [2, 3]
    A = [[1, 1], [1, 0], [0, 1]]
    b = [5, 2, 1]
    signos = [">=", ">=", ">="]

    dos_fases = DosFases(c, A, b, signos, tipo="min", nombres_vars=["x1", "x2"])
    resultado = dos_fases.resolver(verbose=True)

    print("\n" + "-" * 80)
    print("RESULTADO")
    print("-" * 80)

    if resultado['exito']:
        print(f"\n✓ SOLUCIÓN ÓPTIMA")
        print(f"Z = {resultado['valor_optimo']:.6f}")
        print(f"x₁ = {resultado['solucion_variables']['x1']:.6f}")
        print(f"x₂ = {resultado['solucion_variables']['x2']:.6f}")
        print(f"Iteraciones Fase 1: {resultado['iteraciones_fase1']}")
        print(f"Iteraciones Fase 2: {resultado['iteraciones_fase2']}")

        print("\nTabla Fase 1:")
        print(dos_fases.obtener_tabla_fase1_pandas())

        print("\nTabla Fase 2:")
        print(dos_fases.obtener_tabla_fase2_pandas())

    elif resultado['es_infactible']:
        print(f"\n❌ PROBLEMA INFACTIBLE")
    elif resultado['es_no_acotado']:
        print(f"\n⚠️ PROBLEMA NO ACOTADO")