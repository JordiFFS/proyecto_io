import numpy as np
from typing import List, Dict, Optional
import pandas as pd


class DosFases:
    """
    Implementación del Método de Dos Fases - VERSIÓN ULTRA DEBUG
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str], tipo: str = "max",
                 nombres_vars: List[str] = None):
        self.c_original = np.array(c, dtype=float)  # ← GUARDAR ORIGINAL
        self.A_original = np.array(A, dtype=float)
        self.b_original = np.array(b, dtype=float)
        self.tipo = tipo.lower()
        self.m, self.n = self.A_original.shape

        if signos is None:
            self.signos = ["<="] * self.m
        else:
            self.signos = signos
            if len(self.signos) != self.m:
                if len(self.signos) < self.m:
                    self.signos.extend(["<="] * (self.m - len(self.signos)))
                else:
                    self.signos = self.signos[:self.m]

        self.nombres_vars = nombres_vars or [f"x{i + 1}" for i in range(self.n)]

        self.c = None
        self.A = None
        self.b = None

        self.num_holgura = 0
        self.num_exceso = 0
        self.num_artificiales = 0
        self.var_artificiales_indices = []
        self.mapeo_columnas = {}

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

        self.historial_tablas_fase1 = []
        self.historial_tablas_fase2 = []

    def _preparar_problema(self):
        self.A = self.A_original.copy()
        self.c = self.c_original.copy()
        self.b = self.b_original.copy()

        for i in range(self.m):
            if self.b[i] < 0:
                self.A[i, :] *= -1
                self.b[i] *= -1
                if self.signos[i] == "<=":
                    self.signos[i] = ">="
                elif self.signos[i] == ">=":
                    self.signos[i] = "<="

        if self.tipo == "min":
            self.c = -self.c

        for i in range(self.n):
            self.mapeo_columnas[i] = self.nombres_vars[i]

        nuevas_cols = []
        indices_vars_artificiales = []
        col_idx = self.n

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

        nuevos_coefs = np.zeros(self.A.shape[1] - len(self.c))
        self.c = np.concatenate([self.c, nuevos_coefs])

        self.var_artificiales_indices = indices_vars_artificiales

    def _construir_tabla_fase1(self) -> np.ndarray:
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])
        c_fase1 = np.zeros(self.A.shape[1])
        for idx in self.var_artificiales_indices:
            c_fase1[idx] = 1
        fila_costo = np.hstack([-c_fase1, 0])
        tabla = np.vstack([tabla, fila_costo])
        return tabla

    def _construir_tabla_fase2(self) -> np.ndarray:
        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])
        fila_costo = np.hstack([-self.c, 0])
        tabla = np.vstack([tabla, fila_costo])
        return tabla

    def _encontrar_columna_pivote(self, tabla: np.ndarray, es_fase1: bool = False) -> int:
        fila_costo = tabla[-1, :-1]
        col_negativas = np.where(fila_costo < -1e-10)[0]

        if len(col_negativas) == 0:
            return -1

        if es_fase1:
            col_negativas = col_negativas[col_negativas < self.n]
            if len(col_negativas) == 0:
                return -1

        columnas_validas = []
        for col in col_negativas:
            elementos_positivos = np.where(tabla[:-1, col] > 1e-10)[0]
            if len(elementos_positivos) > 0:
                columnas_validas.append(col)

        if len(columnas_validas) == 0:
            return -1

        col_seleccionada = columnas_validas[np.argmin(fila_costo[columnas_validas])]
        return col_seleccionada

    def _encontrar_fila_pivote(self, tabla: np.ndarray, col_pivote: int) -> int:
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
        try:
            pivote = tabla[fila_pivote, col_pivote]
            if abs(pivote) < 1e-10:
                raise ValueError("Pivote muy pequeño")

            tabla[fila_pivote, :] /= pivote
            for i in range(tabla.shape[0]):
                if i != fila_pivote:
                    factor = tabla[i, col_pivote]
                    tabla[i, :] -= factor * tabla[fila_pivote, :]
        except Exception as e:
            print(f"Error en pivoteo: {e}")

    def _crear_dataframe_tabla(self, tabla: np.ndarray) -> pd.DataFrame:
        nombres_cols = [self.mapeo_columnas.get(i, f"var{i}") for i in range(tabla.shape[1] - 1)] + ["RHS"]
        nombres_filas = [self.mapeo_columnas.get(var_idx, f"var{var_idx}") for var_idx in self.base] + ["Z"]
        return pd.DataFrame(tabla, columns=nombres_cols, index=nombres_filas)

    def _fase1(self) -> bool:
        print("\n" + "=" * 80)
        print("INICIANDO FASE 1")
        print("=" * 80)

        self.tabla_fase1 = self._construir_tabla_fase1()

        self.base = []
        col_actual = self.n

        for i in range(self.m):
            if self.signos[i] == "<=":
                self.base.append(col_actual)
                col_actual += 1
            elif self.signos[i] == ">=":
                col_actual += 1
                self.base.append(col_actual)
                col_actual += 1
            elif self.signos[i] == "=":
                self.base.append(col_actual)
                col_actual += 1

        print(f"\nBase inicial: {[self.mapeo_columnas.get(idx) for idx in self.base]}")
        print(f"Índices base: {self.base}")

        for i, var_base in enumerate(self.base):
            if var_base in self.var_artificiales_indices:
                self.tabla_fase1[-1, :] -= self.tabla_fase1[i, :]

        self.historial_tablas_fase1.append({
            'iteracion': 0,
            'tabla': self._crear_dataframe_tabla(self.tabla_fase1),
            'base': self.base.copy(),
            'variable_entra': None,
            'variable_sale': None
        })

        max_iteraciones = 1000

        while self.iteraciones_fase1 < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote(self.tabla_fase1, es_fase1=True)

            if col_pivote == -1:
                print(f"\nFase 1 completada.")
                print(f"Base final Fase 1: {[self.mapeo_columnas.get(idx) for idx in self.base]}")
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase1, col_pivote)

            if fila_pivote == -1:
                print(f"\nNo hay fila pivote válida. Problema infactible.")
                return False

            var_entra = self.mapeo_columnas.get(col_pivote, f"var{col_pivote}")
            var_sale = self.mapeo_columnas.get(self.base[fila_pivote], f"var{self.base[fila_pivote]}")

            print(f"\nIteración Fase 1 #{self.iteraciones_fase1 + 1}: {var_entra} entra, {var_sale} sale")

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase1, fila_pivote, col_pivote)
            self.iteraciones_fase1 += 1

            self.historial_tablas_fase1.append({
                'iteracion': self.iteraciones_fase1,
                'tabla': self._crear_dataframe_tabla(self.tabla_fase1),
                'base': self.base.copy(),
                'variable_entra': var_entra,
                'variable_sale': var_sale
            })

        valor_fase1 = -self.tabla_fase1[-1, -1]
        print(f"\nValor Fase 1: {valor_fase1}")

        if valor_fase1 > 1e-6:
            print("INFACTIBLE")
            return False

        print("FACTIBLE - Pasando a Fase 2")
        return True

    def _fase2(self):
        """Fase 2 - ULTRA DEBUG - VERSIÓN CORRECTA"""
        print("\n" + "=" * 80)
        print("INICIANDO FASE 2")
        print("=" * 80)

        self.tabla_fase2 = self._construir_tabla_fase2()

        print(f"\n✓ Base al inicio de Fase 2: {[self.mapeo_columnas.get(idx, f'var{idx}') for idx in self.base]}")
        print(f"✓ Coeficientes c (en tabla, negados): {self.c}")

        print(f"\n>>> TABLA INICIAL FASE 2:")
        print(f"    Fila costos: {self.tabla_fase2[-1, :]}")
        print(f"    RHS inicial: {self.tabla_fase2[-1, -1]}")

        print(f"\n>>> CÁLCULO DE Z INICIAL (CORRECTO):")
        print(f"    Fórmula: Z = Σ c_original[i] × RHS[i] para cada var básica")
        print(f"    NOTA: Usar c_original, NO los c negados de la tabla")

        # CRUCIAL: Usar c_original, no self.c (que está negado)
        valor_z_inicial = 0.0
        for i, var_base in enumerate(self.base):
            if var_base < len(self.c_original):  # ← USAR c_original
                coef = self.c_original[var_base]
                rhs_valor = self.tabla_fase2[i, -1]
                contribucion = coef * rhs_valor
                valor_z_inicial += contribucion
                print(
                    f"    i={i}: var={self.mapeo_columnas.get(var_base)}, idx={var_base}, c_original[{var_base}]={coef:.6f}, RHS[{i}]={rhs_valor:.2f} → {contribucion:.2f}")
            else:
                print(
                    f"    i={i}: var={self.mapeo_columnas.get(var_base)}, idx={var_base} → coef=0 (variable de holgura/exceso)")

        print(f"    Z_inicial = {valor_z_inicial:.2f}")

        print(f"\n>>> AJUSTE DE FILA DE COSTOS:")
        print(f"    ANTES: {self.tabla_fase2[-1, :5]}")

        for i, var_base in enumerate(self.base):
            if var_base < len(self.c):
                coef = self.c[var_base]
                if abs(coef) > 1e-10:
                    self.tabla_fase2[-1, :] -= coef * self.tabla_fase2[i, :]

        print(f"    DESPUÉS: {self.tabla_fase2[-1, :5]}")
        print(f"    RHS ANTES de ajuste manual: {self.tabla_fase2[-1, -1]}")

        # El RHS debe ser -Z_inicial (formato simplex donde tabla[-1,-1] = -Z)
        print(f"\n>>> CÁLCULO RHS CORRECTO:")
        print(f"    Tipo de optimización: {self.tipo}")

        # Para MIN: c fue negado, entonces tabla[-1,-1] = Z_min (sin negar)
        # Para MAX: c no fue negado, entonces tabla[-1,-1] = -Z_max
        if self.tipo == "min":
            # c fue negado, entonces tabla[-1,-1] debe ser -Z_min
            rhs_correcto = -valor_z_inicial
            print(f"    MIN: RHS = -Z_inicial = -({valor_z_inicial:.2f}) = {rhs_correcto:.2f}")
        else:
            # c no fue negado, entonces tabla[-1,-1] debe ser Z_max directo
            rhs_correcto = valor_z_inicial
            print(f"    MAX: RHS = Z_inicial = {valor_z_inicial:.2f}")

        self.tabla_fase2[-1, -1] = rhs_correcto
        print(f"    RHS DESPUÉS de corrección: {self.tabla_fase2[-1, -1]}")

        self.historial_tablas_fase2.append({
            'iteracion': 0,
            'tabla': self._crear_dataframe_tabla(self.tabla_fase2),
            'base': self.base.copy(),
            'variable_entra': None,
            'variable_sale': None
        })

        max_iteraciones = 1000

        while self.iteraciones_fase2 < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote(self.tabla_fase2, es_fase1=False)

            if col_pivote == -1:
                print(f"\n✓ Solución óptima encontrada.")
                self.es_optimo = True
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase2, col_pivote)

            if fila_pivote == -1:
                print(f"\n✗ Problema NO ACOTADO.")
                self.es_no_acotado = True
                break

            var_entra = self.mapeo_columnas.get(col_pivote, f"var{col_pivote}")
            var_sale = self.mapeo_columnas.get(self.base[fila_pivote], f"var{self.base[fila_pivote]}")

            print(f"\nIteración Fase 2 #{self.iteraciones_fase2 + 1}: {var_entra} entra, {var_sale} sale")

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase2, fila_pivote, col_pivote)
            self.iteraciones_fase2 += 1

            self.historial_tablas_fase2.append({
                'iteracion': self.iteraciones_fase2,
                'tabla': self._crear_dataframe_tabla(self.tabla_fase2),
                'base': self.base.copy(),
                'variable_entra': var_entra,
                'variable_sale': var_sale
            })

    def _extraer_solucion(self):
        """Extrae la solución"""
        self.solucion = np.zeros(self.n)

        for i, var_base in enumerate(self.base):
            if var_base < self.n:
                self.solucion[var_base] = self.tabla_fase2[i, -1]

        print(f"\n>>> EXTRACCIÓN DE SOLUCIÓN:")
        print(f"    Tipo: {self.tipo}")
        print(f"    Base final: {[self.mapeo_columnas.get(idx) for idx in self.base]}")

        valor_tabla = self.tabla_fase2[-1, -1]
        print(f"    tabla[-1, -1] = {valor_tabla}")

        # LÓGICA CORRECTA FINAL:
        # Para MIN: c fue negado, entonces tabla[-1,-1] es el valor directo
        #          Z_min = tabla[-1, -1]
        # Para MAX: c no fue negado, entonces tabla[-1,-1] está en formato Simplex
        #          Z_max = tabla[-1, -1] (ya está correctamente ajustado en Fase 2)
        # En ambos casos: Z = tabla[-1, -1]
        self.valor_optimo = valor_tabla
        print(f"    Z_final = tabla[-1, -1] = {valor_tabla}")

        if self.valor_optimo is None:
            self.valor_optimo = 0.0

    def resolver(self, verbose: bool = False) -> Dict:
        self._preparar_problema()

        es_factible = self._fase1()

        if not es_factible:
            self.es_infactible = True
            return {
                'exito': False,
                'es_infactible': True,
                'es_no_acotado': False,
                'estado': 'INFACTIBLE',
                'valor_optimo': None,
                'solucion': {},
                'solucion_variables': {},
                'iteraciones': self.iteraciones_fase1,
                'iteraciones_fase1': self.iteraciones_fase1,
                'iteraciones_fase2': 0,
                'tabla_fase1': self.tabla_fase1.tolist() if self.tabla_fase1 is not None else None,
                'tabla_fase2': None,
                'base_final': self._get_nombres_base() if self.base else [],
                'tipo_optimizacion': self.tipo,
                'metodo': 'Dos Fases',
                'historial_tablas_fase1': self.historial_tablas_fase1,
                'historial_tablas_fase2': []
            }

        self._fase2()

        if self.es_optimo:
            self._extraer_solucion()
        elif self.es_no_acotado:
            self.solucion = np.zeros(self.n)

        if self.es_optimo:
            estado = "ÓPTIMO"
        elif self.es_no_acotado:
            estado = "NO ACOTADO"
        else:
            estado = "ERROR"

        solucion_dict = {}
        for i in range(self.n):
            solucion_dict[self.nombres_vars[i]] = float(self.solucion[i]) if self.solucion is not None else 0.0

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
            'valor_optimo': float(self.valor_optimo) if self.valor_optimo is not None else 0.0,
            'solucion': solucion_dict,
            'solucion_variables': {self.nombres_vars[i]: float(self.solucion[i]) if self.solucion is not None else 0.0
                                   for i in range(self.n)},
            'iteraciones': self.iteraciones_fase1 + self.iteraciones_fase2,
            'iteraciones_fase1': self.iteraciones_fase1,
            'iteraciones_fase2': self.iteraciones_fase2,
            'tabla_fase1': self.tabla_fase1.tolist() if self.tabla_fase1 is not None else None,
            'tabla_fase2': self.tabla_fase2.tolist() if self.tabla_fase2 is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo,
            'metodo': 'Dos Fases',
            'historial_tablas_fase1': self.historial_tablas_fase1,
            'historial_tablas_fase2': self.historial_tablas_fase2
        }

    def _get_nombres_base(self) -> List[str]:
        if self.base is None:
            return []
        return [self.mapeo_columnas.get(var_idx, f"var{var_idx}") for var_idx in self.base]

    def obtener_tabla_fase1_pandas(self) -> Optional[pd.DataFrame]:
        if self.tabla_fase1 is None:
            return None
        nombres_cols = [self.mapeo_columnas.get(i, f"var{i}") for i in range(self.tabla_fase1.shape[1] - 1)] + ["RHS"]
        nombres_filas = self._get_nombres_base() + ["Z"]
        return pd.DataFrame(self.tabla_fase1, columns=nombres_cols, index=nombres_filas)

    def obtener_tabla_fase2_pandas(self) -> Optional[pd.DataFrame]:
        if self.tabla_fase2 is None:
            return None
        nombres_cols = [self.mapeo_columnas.get(i, f"var{i}") for i in range(self.tabla_fase2.shape[1] - 1)] + ["RHS"]
        nombres_filas = self._get_nombres_base() + ["Z"]
        return pd.DataFrame(self.tabla_fase2, columns=nombres_cols, index=nombres_filas)