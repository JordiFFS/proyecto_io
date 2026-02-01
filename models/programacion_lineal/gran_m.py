import numpy as np
from typing import Tuple, List, Dict, Optional
import pandas as pd


class GranM:
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
        self.m, self.n = self.A_original.shape
        self.M = M

        self.nombres_vars = nombres_vars or [f"x{i + 1}" for i in range(self.n)]

        self.c = None
        self.A = None
        self.b = None

        self.num_holgura = 0
        self.num_exceso = 0
        self.num_artificiales = 0
        self.var_exceso_indices = []
        self.var_artificiales_indices = []
        self.mapeo_columnas = {}

        self.tabla_simplex = None
        self.base = None
        self.solucion = None
        self.valor_optimo = None
        self.es_optimo = False
        self.es_no_acotado = False
        self.es_infactible = False
        self.iteraciones = 0

        # Historial para visualización
        self.historial_tablas = []
        self.historial_pasos = []

    def _preparar_problema(self):
        """Prepara el problema agregando variables de holgura, exceso y artificiales"""
        self.A = self.A_original.copy()
        self.c = self.c_original.copy()
        self.b = self.b_original.copy()

        if self.tipo == "min":
            self.c = -self.c

        nuevas_cols = []
        indices_vars_artificiales = []
        indices_vars_exceso = []
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
                indices_vars_exceso.append(col_idx)
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

        n_original = len(self.c_original)
        nuevos_coefs = np.zeros(self.A.shape[1] - n_original)

        for idx in indices_vars_artificiales:
            posicion_en_nuevos = idx - n_original
            if posicion_en_nuevos >= 0 and posicion_en_nuevos < len(nuevos_coefs):
                nuevos_coefs[posicion_en_nuevos] = -self.M if self.tipo == "max" else self.M

        self.c = np.concatenate([self.c, nuevos_coefs])
        self.var_exceso_indices = indices_vars_exceso
        self.var_artificiales_indices = indices_vars_artificiales

    def _construir_tabla_inicial(self) -> np.ndarray:
        """Construye la tabla inicial del simplex con fila de costos correcta"""
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])

        # CORRECCIÓN: Calcular fila de costos considerando variables artificiales en la base
        fila_costo = np.concatenate([-self.c, np.zeros(1)])

        # Inicializar base
        base_inicial = []
        col_actual = self.n
        for i in range(self.m):
            if self.signos[i] == "<=":
                base_inicial.append(col_actual)
                col_actual += 1
            elif self.signos[i] == ">=":
                col_actual += 1  # exceso
                base_inicial.append(col_actual)  # artificial
                col_actual += 1
            elif self.signos[i] == "=":
                base_inicial.append(col_actual)  # artificial
                col_actual += 1

        # Por cada artificial en la base, restar M veces su fila de la fila de costos
        for i, var_base in enumerate(base_inicial):
            if var_base in self.var_artificiales_indices:
                costo_penalizacion = self.M
                fila_costo[:-1] -= costo_penalizacion * self.A[i, :]
                fila_costo[-1] -= costo_penalizacion * self.b[i]

        tabla = np.vstack([tabla, fila_costo])
        return tabla

    def _encontrar_columna_pivote(self) -> int:
        """Encuentra la columna pivote (variable que entra en base)"""
        fila_costo = self.tabla_simplex[-1, :-1]

        # Buscar columnas negativas EXCLUYENDO exceso y artificiales
        col_negativas = []
        for i in range(len(fila_costo)):
            if fila_costo[i] < -1e-10 and i not in self.var_exceso_indices and i not in self.var_artificiales_indices:
                col_negativas.append(i)

        if len(col_negativas) == 0:
            return -1

        idx_pivote = col_negativas[np.argmin(fila_costo[col_negativas])]
        return idx_pivote

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
            return -1

        min_razon = min(razones, key=lambda x: x[0])
        return min_razon[1]

    def _pivotear(self, fila_pivote: int, col_pivote: int):
        """Realiza la operación de pivoteo"""
        pivote = self.tabla_simplex[fila_pivote, col_pivote]

        if abs(pivote) < 1e-10:
            raise ValueError("Elemento pivote muy pequeño")

        self.tabla_simplex[fila_pivote, :] /= pivote

        for i in range(self.tabla_simplex.shape[0]):
            if i != fila_pivote:
                factor = self.tabla_simplex[i, col_pivote]
                if abs(factor) > 1e-10:
                    self.tabla_simplex[i, :] -= factor * self.tabla_simplex[fila_pivote, :]

    def _crear_dataframe_tabla(self) -> pd.DataFrame:
        """Crea DataFrame de la tabla actual"""
        nombres_cols = []
        for i in range(self.tabla_simplex.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = [self.mapeo_columnas.get(var_idx, f"var{var_idx}") for var_idx in self.base] + ["Z"]

        return pd.DataFrame(self.tabla_simplex, columns=nombres_cols, index=nombres_filas)

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el problema usando el Método de Gran M"""
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

        # Guardar tabla inicial
        self.historial_tablas.append({
            'iteracion': 0,
            'tabla': self._crear_dataframe_tabla(),
            'base': self.base.copy(),
            'variable_entra': None,
            'variable_sale': None,
            'elemento_pivote': None,
            'posicion_pivote': None
        })

        max_iteraciones = 1000

        while self.iteraciones < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote()

            if col_pivote == -1:
                self.es_optimo = True
                break

            fila_pivote = self._encontrar_fila_pivote(col_pivote)

            if fila_pivote == -1:
                self.es_no_acotado = True
                break

            var_entra = self.mapeo_columnas.get(col_pivote, f"var{col_pivote}")
            var_sale = self.mapeo_columnas.get(self.base[fila_pivote], f"var{self.base[fila_pivote]}")
            elemento_pivote = float(self.tabla_simplex[fila_pivote, col_pivote])

            self.base[fila_pivote] = col_pivote
            self._pivotear(fila_pivote, col_pivote)
            self.iteraciones += 1

            # Guardar iteración
            self.historial_tablas.append({
                'iteracion': self.iteraciones,
                'tabla': self._crear_dataframe_tabla(),
                'base': self.base.copy(),
                'variable_entra': var_entra,
                'variable_sale': var_sale,
                'elemento_pivote': elemento_pivote,
                'posicion_pivote': f"[{fila_pivote + 1}, {col_pivote + 1}]"
            })

        if self.es_optimo or self.es_no_acotado:
            self._extraer_solucion()

        # Verificar infactibilidad
        if self.es_optimo:
            for idx in self.var_artificiales_indices:
                if idx in self.base:
                    pos = self.base.index(idx)
                    if self.tabla_simplex[pos, -1] > 1e-4:
                        self.es_infactible = True
                        break

        return self._generar_resultado()

    def _extraer_solucion(self):
        """Extrae la solución - CON PRINTS DE DEBUG"""
        print("\n" + "=" * 80)
        print("EXTRAYENDO SOLUCIÓN - DEBUG DETALLADO")
        print("=" * 80)

        total_variables = self.A.shape[1]
        self.solucion = np.zeros(total_variables)

        print(f"\nINFORMACIÓN BASE:")
        print(f"  Total variables en tabla: {total_variables}")
        print(f"  Número de variables de decisión: {self.n}")
        print(f"  Base final (índices): {self.base}")
        print(f"  Base final (nombres): {[self.mapeo_columnas.get(idx) for idx in self.base]}")

        # Mostrar la última fila completa (fila de costos)
        print(f"\nÚLTIMA FILA DE LA TABLA (Fila de costos):")
        print(f"  {self.tabla_simplex[-1, :]}")
        print(f"  Primeros 5 elementos: {self.tabla_simplex[-1, :5]}")
        print(f"  Último elemento (RHS): {self.tabla_simplex[-1, -1]}")

        # Mostrar cada variable básica
        print(f"\nVARIABLES BÁSICAS:")
        for i, var_base in enumerate(self.base):
            if var_base < total_variables:
                valor = self.tabla_simplex[i, -1]
                self.solucion[var_base] = valor
                var_nombre = self.mapeo_columnas.get(var_base, f'var{var_base}')
                print(f"  Fila {i}: {var_nombre:20s} (índice {var_base:2d}) = {valor:12.2f}")

        # Mostrar variables no básicas
        print(f"\nVARIABLES NO BÁSICAS (valor = 0):")
        for i in range(self.n):
            if i not in self.base:
                var_nombre = self.mapeo_columnas.get(i, f'var{i}')
                print(f"  {var_nombre:20s} (índice {i:2d}) = 0.00")

        # EXTRACCIÓN DEL VALOR ÓPTIMO
        print(f"\n" + "=" * 80)
        print("CÁLCULO DEL VALOR ÓPTIMO")
        print("=" * 80)

        valor_tabla = self.tabla_simplex[-1, -1]
        print(f"\ntabla[-1, -1] (RHS de fila de costos) = {valor_tabla:.6f}")

        print(f"\nTipo de optimización: {self.tipo}")
        print(f"Coeficientes originales c_original: {self.c_original}")
        print(f"Coeficientes después de preparación c: {self.c}")

        print(f"\nLÓGICA GRAN M:")
        print(f"  En Gran M se niega c en preparación para AMBOS MIN y MAX")
        print(f"  Por lo tanto tabla[-1,-1] siempre = -Z")
        print(f"  Z = -tabla[-1,-1] = {-valor_tabla:.6f}")

        # GRAN M SIEMPRE NIEGA
        self.valor_optimo = -valor_tabla

        print(f"\nVALOR ÓPTIMO FINAL: {self.valor_optimo:.6f}")

        # Verificación manual: sumar costos de variables básicas
        print(f"\n" + "=" * 80)
        print("VERIFICACIÓN MANUAL DEL VALOR ÓPTIMO")
        print("=" * 80)

        valor_manual = 0.0
        print(f"\nSuma de c_original[i] * x[i] para variables básicas:")
        for i in range(self.n):
            if self.solucion[i] > 1e-6:
                contribucion = self.c_original[i] * self.solucion[i]
                valor_manual += contribucion
                print(
                    f"  {self.nombres_vars[i]:20s}: {self.c_original[i]:8.2f} × {self.solucion[i]:12.2f} = {contribucion:12.2f}")

        print(f"\nValor manual calculado: {valor_manual:.6f}")
        print(f"Valor extraído de tabla: {self.valor_optimo:.6f}")
        print(f"Diferencia: {abs(valor_manual - self.valor_optimo):.6f}")

        print("=" * 80)

    def _generar_resultado(self) -> Dict:
        """Genera el resultado final"""
        solucion_dict = {}
        for i in range(self.n):
            solucion_dict[self.nombres_vars[i]] = float(self.solucion[i])

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

        if self.es_infactible:
            estado = "INFACTIBLE"
        elif self.es_no_acotado:
            estado = "NO ACOTADO"
        elif self.es_optimo:
            estado = "ÓPTIMO"
        else:
            estado = "ERROR"

        return {
            'exito': self.es_optimo and not self.es_infactible,
            'es_no_acotado': self.es_no_acotado,
            'es_infactible': self.es_infactible,
            'valor_optimo': float(self.valor_optimo) if self.valor_optimo is not None else None,
            'solucion': solucion_dict,
            'solucion_variables': {self.nombres_vars[i]: float(self.solucion[i]) for i in range(self.n)},
            'iteraciones': self.iteraciones,
            'tabla_final': self.tabla_simplex.tolist() if self.tabla_simplex is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo,
            'metodo': 'Gran M',
            'estado': estado,
            'historial_tablas': self.historial_tablas
        }

    def _get_nombres_base(self) -> List[str]:
        """Obtiene los nombres de variables en la base"""
        nombres = []
        for var_idx in self.base:
            nombres.append(self.mapeo_columnas.get(var_idx, f"var{var_idx}"))
        return nombres

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