import numpy as np
from typing import Tuple, List, Dict, Optional
import pandas as pd


class GranM:
    """
    Implementación del Método de Gran M para Programación Lineal

    Resuelve problemas con restricciones de tipo >=, <= y =

    max/min: c^T * x
    s.a: A₁ * x <= b₁  (restricciones <=)
         A₂ * x >= b₂  (restricciones >=)
         A₃ * x = b₃   (restricciones =)
         x >= 0
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str], tipo: str = "max",
                 nombres_vars: List[str] = None, M: float = 1e6):
        """
        Parámetros:
        - c: coeficientes de la función objetivo
        - A: matriz de coeficientes de restricciones
        - b: vector de lados derechos
        - signos: lista de signos ('<=', '>=', '=')
        - tipo: "max" o "min"
        - nombres_vars: nombres de variables (opcional)
        - M: valor grande para penalización (default: 1e6)
        """
        self.c_original = np.array(c, dtype=float)
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.signos = signos
        self.tipo = tipo.lower()
        self.m, self.n = self.A_original.shape  # m restricciones, n variables
        self.M = M

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
        self.mapeo_columnas = {}  # Mapeo de índice a nombre de variable

        self.tabla_simplex = None
        self.base = None
        self.solucion = None
        self.valor_optimo = None
        self.es_optimo = False
        self.es_no_acotado = False
        self.es_infactible = False
        self.iteraciones = 0

    def _preparar_problema(self):
        """Prepara el problema agregando variables de holgura, exceso y artificiales"""

        self.A = self.A_original.copy()
        self.c = self.c_original.copy()
        self.b = self.b_original.copy()

        # IMPORTANTE: Para minimización, multiplicar coeficientes por -1
        # así trabajamos siempre en maximización internamente
        if self.tipo == "min":
            self.c = -self.c

        # Procesar cada restricción
        nuevas_cols = []
        indices_vars_artificiales = []
        col_idx = self.n

        # Mapear variables originales
        for i in range(self.n):
            self.mapeo_columnas[i] = self.nombres_vars[i]

        for i, signo in enumerate(self.signos):
            if signo == "<=":
                # Agregar variable de holgura
                col_holgura = np.zeros(self.m)
                col_holgura[i] = 1
                nuevas_cols.append(col_holgura)
                self.mapeo_columnas[col_idx] = f"s{i + 1}"
                self.num_holgura += 1
                col_idx += 1

            elif signo == ">=":
                # Agregar variable de exceso (negativa)
                col_exceso = np.zeros(self.m)
                col_exceso[i] = -1
                nuevas_cols.append(col_exceso)
                self.mapeo_columnas[col_idx] = f"e{i + 1}"
                self.num_exceso += 1
                col_idx += 1

                # Agregar variable artificial
                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                col_idx += 1

            elif signo == "=":
                # Agregar variable artificial (sin exceso)
                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                col_idx += 1

        # Agregar columnas a la matriz A
        if nuevas_cols:
            matriz_nuevas = np.column_stack(nuevas_cols)
            self.A = np.hstack([self.A, matriz_nuevas])

        # Extender vector c con coeficientes para nuevas variables
        n_original = len(self.c_original)
        nuevos_coefs = np.zeros(self.A.shape[1] - n_original)

        # Para variables artificiales, usar penalización -M
        for idx in indices_vars_artificiales:
            posicion_en_nuevos = idx - n_original
            if posicion_en_nuevos >= 0 and posicion_en_nuevos < len(nuevos_coefs):
                nuevos_coefs[posicion_en_nuevos] = -self.M

        self.c = np.concatenate([self.c, nuevos_coefs])
        self.var_artificiales_indices = indices_vars_artificiales

    def _construir_tabla_inicial(self) -> np.ndarray:
        """Construye la tabla inicial del simplex"""
        # Tabla: [A | b]
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])

        # Fila de costos: [-c | 0] (siempre negativa de c)
        fila_costo = np.hstack([-self.c, 0])
        tabla = np.vstack([tabla, fila_costo])

        return tabla

    def _encontrar_columna_pivote(self) -> int:
        """Encuentra la columna pivote (variable que entra en base)"""
        fila_costo = self.tabla_simplex[-1, :-1]

        # En maximización, buscar coeficientes negativos
        col_negativas = np.where(fila_costo < -1e-10)[0]

        if len(col_negativas) == 0:
            return -1  # Solución óptima encontrada

        # Regla de Dantzig: el más negativo
        return col_negativas[np.argmin(fila_costo[col_negativas])]

    def _encontrar_fila_pivote(self, col_pivote: int) -> int:
        """Encuentra la fila pivote (variable que sale de base)"""
        col = self.tabla_simplex[:-1, col_pivote]
        b_vals = self.tabla_simplex[:-1, -1]

        razones = []
        for i in range(len(col)):
            if col[i] > 1e-10:
                razon = b_vals[i] / col[i]
                razones.append((razon, i))

        if not razones:
            return -1  # Problema no acotado

        return min(razones)[1]

    def _pivotear(self, fila_pivote: int, col_pivote: int):
        """Realiza la operación de pivoteo"""
        pivote = self.tabla_simplex[fila_pivote, col_pivote]

        if abs(pivote) < 1e-10:
            raise ValueError("Elemento pivote muy pequeño")

        # Dividir fila pivote
        self.tabla_simplex[fila_pivote, :] /= pivote

        # Eliminación gaussiana
        for i in range(self.tabla_simplex.shape[0]):
            if i != fila_pivote:
                factor = self.tabla_simplex[i, col_pivote]
                self.tabla_simplex[i, :] -= factor * self.tabla_simplex[fila_pivote, :]

    def _verificar_infactibilidad(self) -> bool:
        """Verifica si el problema es infactible (hay variables artificiales positivas en base)"""
        if not self.es_optimo:
            return False

        for idx in self.var_artificiales_indices:
            if idx in self.base:
                pos_en_base = self.base.index(idx)
                if self.tabla_simplex[pos_en_base, -1] > 1e-6:
                    return True
        return False

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el problema usando el Método de Gran M"""

        # Preparar el problema
        self._preparar_problema()
        self.tabla_simplex = self._construir_tabla_inicial()

        # Inicializar base
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

        if verbose:
            print(f"\n{'=' * 80}")
            print(f"RESOLVIENDO CON MÉTODO DE GRAN M")
            print(f"{'=' * 80}")
            print(f"Tipo: {self.tipo.upper()}")
            print(f"M = {self.M}")

        max_iteraciones = 1000

        while self.iteraciones < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote()

            if col_pivote == -1:
                self.es_optimo = True
                if verbose:
                    print(f"\n✓ Optimalidad alcanzada en iteración {self.iteraciones}")
                break

            fila_pivote = self._encontrar_fila_pivote(col_pivote)

            if fila_pivote == -1:
                # Problema no acotado
                self.es_no_acotado = True
                self._extraer_solucion()
                if verbose:
                    print(f"\n⚠️ PROBLEMA NO ACOTADO en iteración {self.iteraciones}")
                    print(f"Última tabla antes de no acotado:")
                    self._mostrar_tabla()
                break

            # Actualizar base y pivotear
            self.base[fila_pivote] = col_pivote
            self._pivotear(fila_pivote, col_pivote)
            self.iteraciones += 1

            if verbose and self.iteraciones <= 10:
                print(f"\nIteración {self.iteraciones}: entra {self.mapeo_columnas.get(col_pivote)}")

        # Extraer solución al final
        if self.es_optimo or self.es_no_acotado:
            self._extraer_solucion()

        # Verificar infactibilidad DESPUÉS de resolver
        if self.es_optimo and self._verificar_infactibilidad():
            self.es_infactible = True
            self.es_optimo = False

        return self._generar_resultado()

    def _extraer_solucion(self):
        """Extrae la solución"""
        self.solucion = np.zeros(self.n)

        for i, var_base in enumerate(self.base):
            if var_base < self.n:
                self.solucion[var_base] = self.tabla_simplex[i, -1]

        valor = -self.tabla_simplex[-1, -1]

        if self.tipo == "min":
            self.valor_optimo = -valor
        else:
            self.valor_optimo = valor

    def _generar_resultado(self) -> Dict:
        """Genera el resultado final"""
        solucion_dict = {}
        for i in range(self.n):
            solucion_dict[self.nombres_vars[i]] = float(self.solucion[i])

        # Variables de holgura, exceso y artificiales
        col_idx = self.n
        for i, signo in enumerate(self.signos):
            if signo == "<=":
                var_holgura = f"s{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_holgura] = float(self.tabla_simplex[pos, -1])
                else:
                    solucion_dict[var_holgura] = 0.0
                col_idx += 1

            elif signo == ">=":
                var_exceso = f"e{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_exceso] = float(self.tabla_simplex[pos, -1])
                else:
                    solucion_dict[var_exceso] = 0.0
                col_idx += 1

                var_artificial = f"a{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_artificial] = float(self.tabla_simplex[pos, -1])
                else:
                    solucion_dict[var_artificial] = 0.0
                col_idx += 1

            elif signo == "=":
                var_artificial = f"a{i + 1}"
                if col_idx in self.base:
                    pos = self.base.index(col_idx)
                    solucion_dict[var_artificial] = float(self.tabla_simplex[pos, -1])
                else:
                    solucion_dict[var_artificial] = 0.0
                col_idx += 1

        # Determinar estado
        if self.es_infactible:
            estado = "INFACTIBLE"
        elif self.es_no_acotado:
            estado = "NO ACOTADO"
        elif self.es_optimo:
            estado = "ÓPTIMO"
        else:
            estado = "ERROR"

        resultado = {
            'exito': self.es_optimo,
            'es_no_acotado': self.es_no_acotado,
            'es_infactible': self.es_infactible,
            'valor_optimo': float(self.valor_optimo) if self.valor_optimo is not None else None,
            'solucion': solucion_dict,
            'solucion_variables': {self.nombres_vars[i]: float(self.solucion[i])
                                   for i in range(self.n)},
            'iteraciones': self.iteraciones,
            'tabla_final': self.tabla_simplex.tolist() if self.tabla_simplex is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo,
            'metodo': 'Gran M',
            'estado': estado
        }
        return resultado

    def _get_nombres_base(self) -> List[str]:
        """Obtiene los nombres de variables en la base"""
        nombres = []
        for var_idx in self.base:
            nombres.append(self.mapeo_columnas.get(var_idx, f"var{var_idx}"))
        return nombres

    def _mostrar_tabla(self):
        """Muestra la tabla actual"""
        nombres_cols = []
        for i in range(self.tabla_simplex.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = self._get_nombres_base() + ["Z"]

        df = pd.DataFrame(self.tabla_simplex, columns=nombres_cols, index=nombres_filas)
        print("\n" + df.to_string())

    def obtener_tabla_pandas(self) -> Optional[pd.DataFrame]:
        """Retorna tabla final en formato pandas"""
        if self.tabla_simplex is None:
            return None

        nombres_cols = []
        for i in range(self.tabla_simplex.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = self._get_nombres_base() + ["Z"]

        return pd.DataFrame(self.tabla_simplex, columns=nombres_cols, index=nombres_filas)