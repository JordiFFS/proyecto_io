import numpy as np
from typing import List, Dict, Optional
import pandas as pd


class DosFases:
    """
    Implementación CORRECTA del Método de Dos Fases
    Maneja restricciones mixtas (<=, >=, =) y optimización de MIN/MAX
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
        self.tipo = tipo.lower()
        self.m, self.n = self.A_original.shape

        # Validar que signos tenga la longitud correcta
        if signos is None:
            self.signos = ["<="] * self.m
        else:
            self.signos = signos
            if len(self.signos) != self.m:
                print(f"ADVERTENCIA: len(signos)={len(self.signos)} != m={self.m}")
                print(f"Ajustando signos a m={self.m} elementos")
                # Si hay menos signos que restricciones, rellenar con "<="
                # Si hay más signos que restricciones, truncar
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

        # Historial para visualización
        self.historial_tablas_fase1 = []
        self.historial_tablas_fase2 = []

    def _preparar_problema(self):
        """Prepara el problema agregando variables de holgura, exceso y artificiales"""
        print("\n" + "=" * 80)
        print("PREPARANDO PROBLEMA")
        print("=" * 80)

        self.A = self.A_original.copy()
        self.c = self.c_original.copy()
        self.b = self.b_original.copy()

        print(f"Función objetivo original: {self.c}")
        print(f"Tipo de optimización: {self.tipo}")
        print(f"Restricciones: {self.signos}")
        print(f"RHS (b): {self.b}")

        # IMPORTANTE: Normalizar restricciones con RHS negativo
        # Si b_i < 0, multiplicar la fila i por -1 e invertir el signo
        print(f"\nNormalizando restricciones con RHS negativo:")
        restrictiones_normalizadas = False
        for i in range(self.m):
            if self.b[i] < 0:
                print(f"  Restricción {i + 1}: b={self.b[i]} < 0, multiplicando por -1")
                self.A[i, :] *= -1
                self.b[i] *= -1
                # Invertir el signo
                if self.signos[i] == "<=":
                    self.signos[i] = ">="
                elif self.signos[i] == ">=":
                    self.signos[i] = "<="
                # "=" no cambia
                print(f"    Nueva restricción: signo = {self.signos[i]}, b = {self.b[i]}")
                restrictiones_normalizadas = True

        if restrictiones_normalizadas:
            print(f"\nRHS después de normalizar: {self.b}")
            print(f"Signos después de normalizar: {self.signos}")
        else:
            print(f"  Todas las restricciones tienen RHS >= 0")

        # IMPORTANTE: Para minimización, negar la función objetivo
        # para convertir a maximización
        if self.tipo == "min":
            self.c = -self.c
            print(f"Función objetivo convertida a MAX: {self.c}")

        # Mapear variables originales
        for i in range(self.n):
            self.mapeo_columnas[i] = self.nombres_vars[i]

        nuevas_cols = []
        indices_vars_artificiales = []
        col_idx = self.n

        print(f"\nProcesando {len(self.signos)} restricciones:")

        # Procesar cada restricción
        for i, signo in enumerate(self.signos):
            print(f"\n  Restricción {i + 1}: signo = {signo}")

            if signo == "<=":
                # Restricción <= : agregar variable de holgura
                col_holgura = np.zeros(self.m)
                col_holgura[i] = 1
                nuevas_cols.append(col_holgura)
                self.mapeo_columnas[col_idx] = f"s{i + 1}"
                self.num_holgura += 1
                print(f"    → Agregada variable de holgura: s{i + 1} (índice {col_idx})")
                col_idx += 1

            elif signo == ">=":
                # Restricción >= : agregar variable de exceso y artificial
                col_exceso = np.zeros(self.m)
                col_exceso[i] = -1
                nuevas_cols.append(col_exceso)
                self.mapeo_columnas[col_idx] = f"e{i + 1}"
                self.num_exceso += 1
                print(f"    → Agregada variable de exceso: e{i + 1} (índice {col_idx})")
                col_idx += 1

                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                print(f"    → Agregada variable artificial: a{i + 1} (índice {col_idx})")
                col_idx += 1

            elif signo == "=":
                # Restricción = : agregar variable artificial
                col_artificial = np.zeros(self.m)
                col_artificial[i] = 1
                nuevas_cols.append(col_artificial)
                indices_vars_artificiales.append(col_idx)
                self.mapeo_columnas[col_idx] = f"a{i + 1}"
                self.num_artificiales += 1
                print(f"    → Agregada variable artificial: a{i + 1} (índice {col_idx})")
                col_idx += 1

        # Agregar nuevas columnas a la matriz A
        if nuevas_cols:
            matriz_nuevas = np.column_stack(nuevas_cols)
            self.A = np.hstack([self.A, matriz_nuevas])

        # Extender coeficientes de función objetivo
        nuevos_coefs = np.zeros(self.A.shape[1] - len(self.c))
        self.c = np.concatenate([self.c, nuevos_coefs])

        self.var_artificiales_indices = indices_vars_artificiales

        print(f"\nMatriz A después de preparación: shape {self.A.shape}")
        print(f"Variables artificiales en índices: {indices_vars_artificiales}")
        print(f"Coeficientes c: {self.c}")
        print(f"Mapeo de columnas: {self.mapeo_columnas}")

    def _construir_tabla_fase1(self) -> np.ndarray:
        """Construye tabla para Fase 1"""
        print("\n" + "=" * 80)
        print("CONSTRUYENDO TABLA FASE 1")
        print("=" * 80)

        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])

        # Función objetivo Fase 1: minimizar suma de artificiales
        c_fase1 = np.zeros(self.A.shape[1])
        for idx in self.var_artificiales_indices:
            c_fase1[idx] = 1

        print(f"Función objetivo Fase 1 (suma de artificiales): {c_fase1}")

        # Negamos para maximización
        fila_costo = np.hstack([-c_fase1, 0])
        tabla = np.vstack([tabla, fila_costo])

        print(f"Tabla Fase 1 inicial:")
        print(tabla)

        return tabla

    def _construir_tabla_fase2(self) -> np.ndarray:
        """Construye tabla para Fase 2"""
        print("\n" + "=" * 80)
        print("CONSTRUYENDO TABLA FASE 2")
        print("=" * 80)

        tabla = np.hstack([self.A, self.b.reshape(-1, 1)])
        fila_costo = np.hstack([-self.c, 0])
        tabla = np.vstack([tabla, fila_costo])

        print(f"Tabla Fase 2 inicial (antes de ajuste):")
        print(tabla)

        return tabla

    def _encontrar_columna_pivote(self, tabla: np.ndarray, es_fase1: bool = False) -> int:
        """Encuentra columna pivote (Regla de Dantzig - mejorada)"""
        fila_costo = tabla[-1, :-1]
        col_negativas = np.where(fila_costo < -1e-10)[0]

        if len(col_negativas) == 0:
            return -1

        # En Fase 1, PREFERIR variables de decisión (x_i) sobre variables artificiales
        if es_fase1:
            # Asumir que las primeras self.n columnas son variables de decisión
            col_decisión = col_negativas[col_negativas < self.n]
            if len(col_decisión) > 0:
                # Si hay variables de decisión negativas, elegir la más negativa
                col_negativas = col_decisión

        # Filtrar columnas que tengan al menos un elemento positivo en la restricción
        columnas_validas = []
        for col in col_negativas:
            elementos_positivos = np.where(tabla[:-1, col] > 1e-10)[0]
            if len(elementos_positivos) > 0:
                columnas_validas.append(col)

        if len(columnas_validas) == 0:
            return -1

        # Seleccionar la columna más negativa entre las válidas
        col_seleccionada = columnas_validas[np.argmin(fila_costo[columnas_validas])]
        return col_seleccionada

    def _encontrar_fila_pivote(self, tabla: np.ndarray, col_pivote: int) -> int:
        """Encuentra fila pivote (Mínima razón)"""
        col = tabla[:-1, col_pivote]
        b_vals = tabla[:-1, -1]

        print(f"      Buscando fila pivote para columna {col_pivote}")
        print(f"      Valores en columna: {col}")
        print(f"      RHS: {b_vals}")

        razones = []
        for i in range(len(col)):
            if col[i] > 1e-10:
                razon = b_vals[i] / col[i]
                razones.append((razon, i))
                print(f"      Fila {i}: {b_vals[i]} / {col[i]} = {razon}")

        if not razones:
            print(f"      NO HAY FILAS VÁLIDAS (todas tienen elementos <= 0 en la columna)")
            return -1

        resultado = min(razones)[1]
        print(f"      Fila pivote seleccionada: {resultado}")
        return resultado

    def _pivotear(self, tabla: np.ndarray, fila_pivote: int, col_pivote: int):
        """Realiza operación de pivoteo"""
        try:
            pivote = tabla[fila_pivote, col_pivote]

            if abs(pivote) < 1e-10:
                raise ValueError("Elemento pivote muy pequeño")

            print(f"      Pivoteo: fila {fila_pivote}, columna {col_pivote}, pivote = {pivote}")
            print(f"      Antes - RHS fila de costo: {tabla[-1, -1]}")

            tabla[fila_pivote, :] /= pivote

            for i in range(tabla.shape[0]):
                if i != fila_pivote:
                    factor = tabla[i, col_pivote]
                    tabla[i, :] -= factor * tabla[fila_pivote, :]

            print(f"      Después - RHS fila de costo: {tabla[-1, -1]}")
        except Exception as e:
            print(f"Error en pivoteo: {e}")
            pass

    def _crear_dataframe_tabla(self, tabla: np.ndarray) -> pd.DataFrame:
        """Crea DataFrame de tabla"""
        nombres_cols = []
        for i in range(tabla.shape[1] - 1):
            nombres_cols.append(self.mapeo_columnas.get(i, f"var{i}"))
        nombres_cols.append("RHS")

        nombres_filas = [self.mapeo_columnas.get(var_idx, f"var{var_idx}") for var_idx in self.base] + ["Z"]

        return pd.DataFrame(tabla, columns=nombres_cols, index=nombres_filas)

    def _fase1(self) -> bool:
        """Fase 1: Encontrar solución básica factible"""
        print("\n" + "=" * 80)
        print("INICIANDO FASE 1")
        print("=" * 80)

        self.tabla_fase1 = self._construir_tabla_fase1()

        # Inicializar base
        self.base = []
        col_actual = self.n

        print("\nIniciando base con variables básicas iniciales:")

        for i in range(self.m):
            if self.signos[i] == "<=":
                self.base.append(col_actual)
                print(f"  Restricción {i + 1} (<=): variable s{i + 1} (índice {col_actual}) en base")
                col_actual += 1
            elif self.signos[i] == ">=":
                # Variable de exceso
                col_actual += 1
                # Variable artificial
                self.base.append(col_actual)
                print(f"  Restricción {i + 1} (>=): variable a{i + 1} (índice {col_actual}) en base")
                col_actual += 1
            elif self.signos[i] == "=":
                # Variable artificial
                self.base.append(col_actual)
                print(f"  Restricción {i + 1} (=): variable a{i + 1} (índice {col_actual}) en base")
                col_actual += 1

        print(f"\nBase inicial: {[self.mapeo_columnas.get(idx, f'var{idx}') for idx in self.base]}")

        # Ajustar fila de costo para que sea consistente con la base inicial
        print("\nAjustando fila de costo para ser consistente con la base...")
        for i, var_base in enumerate(self.base):
            if var_base in self.var_artificiales_indices:
                print(f"  Variable artificial {self.mapeo_columnas.get(var_base)} en base (fila {i})")
                # Para la función objetivo Fase 1, el coeficiente de cada variable artificial es 1
                # Si a_j está en base en fila i, restamos fila i de la fila de costo para hacer el coeficiente 0
                self.tabla_fase1[-1, :] -= self.tabla_fase1[i, :]
                print(f"    Restando la fila {i} de la fila de costo")

        print(f"\nTabla Fase 1 después de ajuste:")
        print(self.tabla_fase1)

        # Guardar tabla inicial Fase 1
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
                print(f"\nNo hay más columnas negativas. Fase 1 completada.")
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase1, col_pivote)

            if fila_pivote == -1:
                print(f"\nNo hay fila pivote válida. Problema infactible.")
                return False

            var_entra = self.mapeo_columnas.get(col_pivote, f"var{col_pivote}")
            var_sale = self.mapeo_columnas.get(self.base[fila_pivote], f"var{self.base[fila_pivote]}")

            print(f"\nIteración Fase 1 #{self.iteraciones_fase1 + 1}:")
            print(f"  Entra: {var_entra} (columna {col_pivote})")
            print(f"  Sale: {var_sale} (fila {fila_pivote})")

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase1, fila_pivote, col_pivote)
            self.iteraciones_fase1 += 1

            print(f"  Base actual: {[self.mapeo_columnas.get(idx, f'var{idx}') for idx in self.base]}")

            self.historial_tablas_fase1.append({
                'iteracion': self.iteraciones_fase1,
                'tabla': self._crear_dataframe_tabla(self.tabla_fase1),
                'base': self.base.copy(),
                'variable_entra': var_entra,
                'variable_sale': var_sale
            })

        # Verificar factibilidad
        valor_fase1 = -self.tabla_fase1[-1, -1]

        print(f"\nValor de función objetivo Fase 1: {valor_fase1}")

        if valor_fase1 > 1e-6:
            print("ERROR: Valor > 0, problema INFACTIBLE")
            return False

        print("Problema es FACTIBLE")
        return True

    def _fase2(self):
        """Fase 2: Optimizar con función objetivo original"""
        print("\n" + "=" * 80)
        print("INICIANDO FASE 2")
        print("=" * 80)

        self.tabla_fase2 = self._construir_tabla_fase2()

        print(f"\nBase al inicio de Fase 2: {[self.mapeo_columnas.get(idx, f'var{idx}') for idx in self.base]}")

        # Ajustar fila de costo basada en la base actual
        print("\nAjustando fila de costo de Fase 2 según la base...")
        for i, var_base in enumerate(self.base):
            if var_base < self.A.shape[1]:
                if self.c[var_base] != 0:
                    print(
                        f"  Variable {self.mapeo_columnas.get(var_base)} tiene coeficiente {self.c[var_base]} en base")
                    self.tabla_fase2[-1, :] -= self.c[var_base] * self.tabla_fase2[i, :]

        print(f"\nTabla Fase 2 después de ajuste:")
        print(self.tabla_fase2)

        # Guardar tabla inicial Fase 2
        self.historial_tablas_fase2.append({
            'iteracion': 0,
            'tabla': self._crear_dataframe_tabla(self.tabla_fase2),
            'base': self.base.copy(),
            'variable_entra': None,
            'variable_sale': None
        })

        max_iteraciones = 1000

        while self.iteraciones_fase2 < max_iteraciones:
            col_pivote = self._encontrar_columna_pivote(self.tabla_fase2)

            if col_pivote == -1:
                print(f"\nNo hay más columnas negativas. Solución óptima encontrada.")
                self.es_optimo = True
                break

            fila_pivote = self._encontrar_fila_pivote(self.tabla_fase2, col_pivote)

            if fila_pivote == -1:
                print(f"\nNo hay fila pivote válida. Problema NO ACOTADO.")
                self.es_no_acotado = True
                break

            var_entra = self.mapeo_columnas.get(col_pivote, f"var{col_pivote}")
            var_sale = self.mapeo_columnas.get(self.base[fila_pivote], f"var{self.base[fila_pivote]}")

            print(f"\nIteración Fase 2 #{self.iteraciones_fase2 + 1}:")
            print(f"  Entra: {var_entra} (columna {col_pivote})")
            print(f"  Sale: {var_sale} (fila {fila_pivote})")

            self.base[fila_pivote] = col_pivote
            self._pivotear(self.tabla_fase2, fila_pivote, col_pivote)
            self.iteraciones_fase2 += 1

            print(f"  Base actual: {[self.mapeo_columnas.get(idx, f'var{idx}') for idx in self.base]}")

            self.historial_tablas_fase2.append({
                'iteracion': self.iteraciones_fase2,
                'tabla': self._crear_dataframe_tabla(self.tabla_fase2),
                'base': self.base.copy(),
                'variable_entra': var_entra,
                'variable_sale': var_sale
            })

    def _extraer_solucion(self):
        """Extrae la solución óptima"""
        print("\n" + "=" * 80)
        print("EXTRAYENDO SOLUCIÓN")
        print("=" * 80)

        self.solucion = np.zeros(self.n)

        print(f"\nVariables de decisión (primeras {self.n}):")
        for i, var_base in enumerate(self.base):
            if var_base < self.n:
                valor = self.tabla_fase2[i, -1]
                self.solucion[var_base] = valor
                print(f"  {self.nombres_vars[var_base]} = {valor}")

        # El valor en la tabla (RHS de fila de costo) es Z directamente
        valor_tabla = self.tabla_fase2[-1, -1]
        print(f"\nValor en tabla (posición RHS de Z): {valor_tabla}")

        # Si el tipo original es MAX, es directamente Z
        # Si el tipo original es MIN, es -Z (porque negamos c al inicio)
        if self.tipo == "max":
            self.valor_optimo = valor_tabla
            print(f"Tipo MAX: Z = {valor_tabla}")
        else:
            self.valor_optimo = -valor_tabla
            print(f"Tipo MIN: Z = -({valor_tabla}) = {self.valor_optimo}")

        # Asegurar que no sea None
        if self.valor_optimo is None:
            self.valor_optimo = 0.0

        print(f"\nSolución final: {self.solucion}")
        print(f"Valor óptimo: {self.valor_optimo}")

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el problema usando Dos Fases"""
        self._preparar_problema()

        es_factible = self._fase1()

        if not es_factible:
            print("\n" + "=" * 80)
            print("PROBLEMA INFACTIBLE - TERMINANDO")
            print("=" * 80)
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

        # Construcción de diccionarios de solución
        solucion_dict = {}
        for i in range(self.n):
            if self.solucion is not None:
                solucion_dict[self.nombres_vars[i]] = float(self.solucion[i])
            else:
                solucion_dict[self.nombres_vars[i]] = 0.0

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
        """Obtiene nombres de variables en la base"""
        if self.base is None:
            return []
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