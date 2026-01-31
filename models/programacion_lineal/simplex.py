import numpy as np
from typing import Tuple, List, Dict, Optional
import pandas as pd


class Simplex:
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
        self.historial_tablas = []
        self.historial_pasos = []
        self.variables_holgura = []

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

        # Guardar información de variables de holgura
        self.variables_holgura = [f"s{i+1}" for i in range(self.m)]

        return tabla

    def _encontrar_columna_pivote(self) -> int:
        """
        Encuentra la columna pivote (variable que entra en base)
        Usa regla de Dantzig: selecciona la columna con el coeficiente más negativo
        """
        fila_costo = self.tabla_simplex[-1, :-1]
        col_negativas = np.where(fila_costo < -1e-10)[0]

        if len(col_negativas) == 0:
            return -1  # Solución óptima encontrada

        # Regla de Dantzig: máximo coeficiente negativo (más negativo)
        idx_min = np.argmin(fila_costo[col_negativas])
        return col_negativas[idx_min]

    def _encontrar_fila_pivote(self, col_pivote: int) -> Tuple[int, np.ndarray]:
        """
        Encuentra la fila pivote (variable que sale de base)
        Usa método de razones mínimas
        Retorna: (fila_pivote, razones_calculadas)
        """
        col = self.tabla_simplex[:-1, col_pivote]
        b_vals = self.tabla_simplex[:-1, -1]

        # Calcular razones solo para elementos positivos
        razones = []
        razones_detalle = []
        for i in range(len(col)):
            if col[i] > 1e-10:  # Solo considerar elementos positivos
                razon = b_vals[i] / col[i]
                razones.append((razon, i))
                razones_detalle.append({
                    'fila': i,
                    'b_i': b_vals[i],
                    'a_ij': col[i],
                    'razon': razon
                })

        if not razones:
            return -1, np.array([])  # Problema no acotado

        # Seleccionar la razón mínima
        fila_minima = min(razones)[1]
        return fila_minima, np.array(razones_detalle)

    def _pivotear(self, fila_pivote: int, col_pivote: int) -> Dict:
        """
        Realiza la operación de pivoteo y retorna detalles del cálculo
        """
        detalles = {
            'fila_pivote': fila_pivote,
            'col_pivote': col_pivote,
            'elemento_pivote': float(self.tabla_simplex[fila_pivote, col_pivote]),
            'pasos': []
        }

        # Elemento pivote
        pivote = self.tabla_simplex[fila_pivote, col_pivote]

        if abs(pivote) < 1e-10:
            raise ValueError("Elemento pivote muy pequeño")

        # 1. Dividir la fila pivote por el elemento pivote
        tabla_antes = self.tabla_simplex.copy()
        self.tabla_simplex[fila_pivote, :] /= pivote

        detalles['pasos'].append({
            'paso': 'División de fila pivote',
            'descripcion': f'R{fila_pivote + 1} = R{fila_pivote + 1} / {pivote:.4f}',
            'tabla_estado': tabla_antes.copy()
        })

        # 2. Eliminación gaussiana: hacer ceros en el resto de la columna
        for i in range(self.tabla_simplex.shape[0]):
            if i != fila_pivote:
                factor = self.tabla_simplex[i, col_pivote]
                if abs(factor) > 1e-10:
                    tabla_antes = self.tabla_simplex.copy()
                    self.tabla_simplex[i, :] -= factor * self.tabla_simplex[fila_pivote, :]

                    detalles['pasos'].append({
                        'paso': 'Eliminación gaussiana',
                        'descripcion': f'R{i + 1} = R{i + 1} - ({factor:.4f}) * R{fila_pivote + 1}',
                        'tabla_estado': tabla_antes.copy()
                    })

        return detalles

    def _get_nombres_variables_tabla(self) -> List[str]:
        """Obtiene los nombres de todas las columnas de la tabla"""
        nombres = []
        # Variables de decisión
        nombres.extend(self.nombres_vars)
        # Variables de holgura
        nombres.extend(self.variables_holgura)
        return nombres

    def _crear_dataframe_tabla(self, tabla: np.ndarray) -> pd.DataFrame:
        """Crea un DataFrame a partir de la tabla"""
        nombres_cols = self._get_nombres_variables_tabla() + ["RHS"]

        nombres_filas = [
            self.nombres_vars[i] if i < self.n else self.variables_holgura[i - self.n]
            for i in self.base
        ] + ["Z"]

        return pd.DataFrame(tabla, columns=nombres_cols, index=nombres_filas)

    def resolver(self, verbose: bool = False) -> Dict:
        """
        Resuelve el problema de programación lineal con detalle completo
        """
        self.tabla_simplex = self._construir_tabla_inicial()

        # Inicializar base con variables de holgura
        self.base = list(range(self.n, self.n + self.m))

        # Guardar tabla inicial
        self.historial_tablas.append({
            'iteracion': 0,
            'tipo': 'inicial',
            'tabla': self._crear_dataframe_tabla(self.tabla_simplex.copy()),
            'base': self.base.copy(),
            'descripcion': 'Tabla Inicial con Variables de Holgura'
        })

        # Paso 1: Mostrar configuración inicial
        self.historial_pasos.append({
            'numero': 0,
            'tipo': 'inicializacion',
            'contenido': {
                'problema': {
                    'tipo_optimizacion': self.tipo.upper(),
                    'funcion_objetivo': dict(zip(self.nombres_vars, self.c_original.tolist())),
                    'numero_variables': self.n,
                    'numero_restricciones': self.m,
                    'numero_holguras': self.m
                },
                'variables_holgura': self.variables_holgura,
                'base_inicial': [
                    self.nombres_vars[i] if i < self.n else self.variables_holgura[i - self.n]
                    for i in self.base
                ]
            }
        })

        max_iteraciones = 1000

        while self.iteraciones < max_iteraciones:
            self.iteraciones += 1

            # Paso: Encontrar columna pivote
            col_pivote = self._encontrar_columna_pivote()

            fila_pivote_info = {
                'iteracion': self.iteraciones,
                'tipo': 'seleccion_pivote',
                'contenido': {
                    'tabla_actual': self._crear_dataframe_tabla(self.tabla_simplex.copy()),
                    'fila_costo': {
                        self._get_nombres_variables_tabla()[i]: float(self.tabla_simplex[-1, i])
                        for i in range(len(self._get_nombres_variables_tabla()))
                    }
                }
            }

            if col_pivote == -1:
                self.es_optimo = True
                fila_pivote_info['contenido']['optimalidad'] = 'SOLUCIÓN ÓPTIMA ENCONTRADA'
                fila_pivote_info['contenido']['razon'] = 'Todos los coeficientes de costo reducido son no negativos'
                self.historial_pasos.append(fila_pivote_info)
                break

            var_entra_nombre = self._get_nombres_variables_tabla()[col_pivote]
            fila_pivote_info['contenido']['variable_entra'] = var_entra_nombre
            fila_pivote_info['contenido']['coeficiente_costo'] = float(self.tabla_simplex[-1, col_pivote])

            # Paso: Encontrar fila pivote
            fila_pivote, razones = self._encontrar_fila_pivote(col_pivote)

            if fila_pivote == -1:
                return self._generar_resultado_error('no_acotado')

            var_sale_idx = self.base[fila_pivote]
            var_sale_nombre = (self.nombres_vars[var_sale_idx] if var_sale_idx < self.n
                             else self.variables_holgura[var_sale_idx - self.n])

            # Agregar detalles de razones mínimas
            razones_lista = []
            for razon_dict in razones:
                razones_lista.append({
                    'fila': razon_dict['fila'],
                    'variable_basica': (self.nombres_vars[self.base[int(razon_dict['fila'])]]
                                       if self.base[int(razon_dict['fila'])] < self.n
                                       else self.variables_holgura[self.base[int(razon_dict['fila'])] - self.n]),
                    'b_i': float(razon_dict['b_i']),
                    'a_ij': float(razon_dict['a_ij']),
                    'razon': float(razon_dict['razon']),
                    'es_minima': (razon_dict['fila'] == fila_pivote)
                })

            fila_pivote_info['contenido']['variable_sale'] = var_sale_nombre
            fila_pivote_info['contenido']['razones_minimas'] = razones_lista
            self.historial_pasos.append(fila_pivote_info)

            # Paso: Realizar pivoteo
            detalles_pivoteo = self._pivotear(fila_pivote, col_pivote)

            self.base[fila_pivote] = col_pivote

            # Guardar información de la iteración
            self.historial_tablas.append({
                'iteracion': self.iteraciones,
                'tipo': 'iteracion',
                'tabla': self._crear_dataframe_tabla(self.tabla_simplex.copy()),
                'base': self.base.copy(),
                'variable_entra': var_entra_nombre,
                'variable_sale': var_sale_nombre,
                'descripcion': f'Iteración {self.iteraciones}',
                'elemento_pivote': detalles_pivoteo['elemento_pivote'],
                'posicion_pivote': f"[{fila_pivote + 1}, {col_pivote + 1}]"
            })

            # Registrar paso de pivoteo
            self.historial_pasos.append({
                'numero': self.iteraciones,
                'tipo': 'pivoteo',
                'contenido': {
                    'variable_entra': var_entra_nombre,
                    'variable_sale': var_sale_nombre,
                    'elemento_pivote': detalles_pivoteo['elemento_pivote'],
                    'posicion_pivote': f"[{fila_pivote + 1}, {col_pivote + 1}]",
                    'pasos_calculo': detalles_pivoteo['pasos'],
                    'tabla_resultado': self._crear_dataframe_tabla(self.tabla_simplex.copy()),
                    'valor_z_actual': float(-self.tabla_simplex[-1, -1]) if self.tipo == "max" else float(self.tabla_simplex[-1, -1])
                }
            })

        if self.es_optimo:
            self._extraer_solucion()

        return self._generar_resultado()

    def _extraer_solucion(self):
        """Extrae la solución óptima de la tabla final"""
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
        """Genera el resultado final completo"""
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
            'solucion_holguras': {self.variables_holgura[i]: float(self.tabla_simplex[i, -1])
                                 for i in range(self.m)},
            'iteraciones': self.iteraciones,
            'tabla_final': self.tabla_simplex.tolist() if self.tabla_simplex is not None else None,
            'base_final': self._get_nombres_base(),
            'tipo_optimizacion': self.tipo,
            'historial_tablas': self.historial_tablas,
            'historial_pasos': self.historial_pasos
        }
        return resultado

    def _generar_resultado_error(self, tipo_error: str) -> Dict:
        """Genera resultado cuando hay error"""
        return {
            'exito': False,
            'valor_optimo': None,
            'solucion': None,
            'iteraciones': self.iteraciones,
            'tipo_error': tipo_error,
            'mensaje': 'Problema no acotado' if tipo_error == 'no_acotado' else 'Error desconocido',
            'historial_tablas': self.historial_tablas,
            'historial_pasos': self.historial_pasos
        }

    def _get_nombres_base(self) -> List[str]:
        """Obtiene los nombres de las variables en la base final"""
        nombres = []
        for i, var_idx in enumerate(self.base):
            if var_idx < self.n:
                nombres.append(self.nombres_vars[var_idx])
            else:
                nombres.append(f"s{var_idx - self.n + 1}")
        return nombres

    def obtener_tabla_pandas(self) -> Optional[pd.DataFrame]:
        """Retorna la tabla final en formato pandas"""
        if self.tabla_simplex is None:
            return None
        return self._crear_dataframe_tabla(self.tabla_simplex)