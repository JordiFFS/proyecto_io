import numpy as np
from typing import List, Dict, Tuple
import pandas as pd
from .dos_fases import DosFases


class Dual:
    """
    Análisis de Dualidad - Resuelve el Primal y construye/resuelve el Dual teórico
    Usa DosFases para resolver ambos problemas de forma robusta
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str] = None, tipo: str = "max",
                 nombres_vars: List[str] = None):
        """
        Inicializa el problema Primal

        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de restricciones
            b: RHS de las restricciones
            signos: Signos de las restricciones (<=, >=, =)
            tipo: Tipo de optimización (max o min)
            nombres_vars: Nombres de las variables
        """
        self.c_primal = np.array(c, dtype=float)
        self.A_primal = np.array(A, dtype=float)
        self.b_primal = np.array(b, dtype=float)
        self.tipo_primal = tipo.lower()

        self.m, self.n = self.A_primal.shape  # m restricciones, n variables

        self.signos_primal = signos if signos else ["<="] * self.m
        self.nombres_vars_primal = nombres_vars or [f"x{i + 1}" for i in range(self.n)]

        # Construcción del Dual
        self._construir_dual()

        # Resultados
        self.resultado_primal = None
        self.resultado_dual = None

    def _construir_dual(self):
        """Construye el problema DUAL teórico"""
        print("\n" + "=" * 80)
        print("CONSTRUYENDO PROBLEMA DUAL")
        print("=" * 80)

        # El DUAL siempre tiene:
        # - Variables: una por cada restricción del primal
        # - Restricciones: una por cada variable del primal
        self.nombres_vars_dual = [f"y{i + 1}" for i in range(self.m)]

        # Coeficientes del Dual = RHS del Primal
        self.c_dual = self.b_primal.copy()

        # Matriz del Dual = Transpuesta de la matriz del Primal
        self.A_dual = self.A_primal.T.copy()

        # RHS del Dual = Coeficientes del Primal
        self.b_dual = self.c_primal.copy()

        # Signos del Dual (transformación)
        if self.tipo_primal == "min":
            # MIN Primal => MAX Dual
            self.tipo_dual = "max"
            self.signos_dual = []
            for signo in self.signos_primal:
                if signo == "<=":
                    self.signos_dual.append(">=")
                elif signo == ">=":
                    self.signos_dual.append("<=")
                else:
                    self.signos_dual.append("=")
        else:
            # MAX Primal => MIN Dual
            self.tipo_dual = "min"
            self.signos_dual = list(self.signos_primal)

        # Mostrar problemas construidos
        print(f"\nPRIMAL ({self.tipo_primal.upper()}):")
        print(f"  Variables: {self.nombres_vars_primal}")
        print(f"  c = {self.c_primal}")
        print(f"  A shape = {self.A_primal.shape}")
        print(f"  b = {self.b_primal}")
        print(f"  Signos = {self.signos_primal}")

        print(f"\nDUAL ({self.tipo_dual.upper()}):")
        print(f"  Variables: {self.nombres_vars_dual}")
        print(f"  c = {self.c_dual}")
        print(f"  A shape = {self.A_dual.shape}")
        print(f"  b = {self.b_dual}")
        print(f"  Signos = {self.signos_dual}")

    def _resolver_problema(self, c: List[float], A: List[List[float]],
                           b: List[float], signos: List[str],
                           tipo: str, nombres: List[str],
                           nombre_problema: str) -> Dict:
        """
        Resuelve un problema usando DosFases

        Returns:
            Dict con los resultados del problema
        """
        print(f"\n{'-' * 80}")
        print(f"RESOLVIENDO {nombre_problema}")
        print(f"{'-' * 80}")

        try:
            # Crear instancia de DosFases
            dos_fases = DosFases(
                c, A, b, signos,
                tipo=tipo,
                nombres_vars=nombres
            )

            # Resolver
            resultado = dos_fases.resolver(verbose=False)

            # Extraer información clave
            if resultado['exito']:
                print(f"✓ {nombre_problema} resuelto exitosamente")
                print(f"  Z = {resultado['valor_optimo']}")
                print(f"  Iteraciones: {resultado['iteraciones_fase1'] + resultado['iteraciones_fase2']}")
            else:
                print(f"✗ {nombre_problema} no pudo ser resuelto")
                print(f"  Estado: {resultado.get('estado', 'Desconocido')}")

            return resultado

        except Exception as e:
            print(f"Error al resolver {nombre_problema}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def resolver(self) -> Dict:
        """
        Resuelve el Primal y el Dual
        Verifica la dualidad fuerte

        Returns:
            Dict con resultados del análisis primal-dual
        """
        # RESOLVER PRIMAL
        self.resultado_primal = self._resolver_problema(
            self.c_primal.tolist(),
            self.A_primal.tolist(),
            self.b_primal.tolist(),
            self.signos_primal,
            self.tipo_primal,
            self.nombres_vars_primal,
            "PRIMAL"
        )

        # RESOLVER DUAL
        self.resultado_dual = self._resolver_problema(
            self.c_dual.tolist(),
            self.A_dual.tolist(),
            self.b_dual.tolist(),
            self.signos_dual,
            self.tipo_dual,
            self.nombres_vars_dual,
            "DUAL"
        )

        # VERIFICAR DUALIDAD FUERTE
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DUALIDAD FUERTE")
        print("=" * 80)

        z_primal = None
        z_dual = None
        dualidad_fuerte = False
        diferencia = None

        if (self.resultado_primal and self.resultado_dual and
                self.resultado_primal.get('exito') and self.resultado_dual.get('exito')):

            z_primal = self.resultado_primal['valor_optimo']
            z_dual = self.resultado_dual['valor_optimo']
            diferencia = abs(z_primal - z_dual)
            dualidad_fuerte = diferencia < 1e-3

            print(f"Z_primal = {z_primal}")
            print(f"Z_dual   = {z_dual}")
            print(f"Diferencia = {diferencia:.2e}")
            print(f"\nDualidad Fuerte: {'✓ VERIFICADA' if dualidad_fuerte else '✗ NO VERIFICADA'}")
        else:
            print("No se puede verificar dualidad fuerte (uno de los problemas no se resolvió)")

        # CONSTRUIR RESULTADO FINAL
        resultado_final = {
            'primal': {
                'exito': self.resultado_primal['exito'] if self.resultado_primal else False,
                'valor_optimo': z_primal,
                'solucion': self._extraer_solucion_primal() if self.resultado_primal else {},
                'iteraciones': (self.resultado_primal['iteraciones_fase1'] +
                                self.resultado_primal['iteraciones_fase2']) if self.resultado_primal else 0,
            },
            'dual': {
                'exito': self.resultado_dual['exito'] if self.resultado_dual else False,
                'valor_optimo': z_dual,
                'solucion': self._extraer_solucion_dual() if self.resultado_dual else {},
                'iteraciones': (self.resultado_dual['iteraciones_fase1'] +
                                self.resultado_dual['iteraciones_fase2']) if self.resultado_dual else 0,
            },
            'dualidad_fuerte': dualidad_fuerte,
            'diferencia_valores_optimos': float(diferencia) if diferencia is not None else None,
            'tipo_primal_original': self.tipo_primal,
            'tipo_dual': self.tipo_dual,
            'nombres_vars_primal': self.nombres_vars_primal,
            'nombres_vars_dual': self.nombres_vars_dual,
        }

        print("\n" + "=" * 80)
        print("RESULTADO FINAL")
        print("=" * 80)
        print(f"Primal: {resultado_final['primal']['exito']} (Z={resultado_final['primal']['valor_optimo']})")
        print(f"Dual:   {resultado_final['dual']['exito']} (Z={resultado_final['dual']['valor_optimo']})")
        print(f"Dualidad Fuerte: {resultado_final['dualidad_fuerte']}")

        return resultado_final

    def _extraer_solucion_primal(self) -> Dict[str, float]:
        """Extrae la solución del PRIMAL en formato dict"""
        solucion = {}
        if self.resultado_primal:
            for var in self.nombres_vars_primal:
                solucion[var] = self.resultado_primal['solucion_variables'].get(var, 0.0)
        return solucion

    def _extraer_solucion_dual(self) -> Dict[str, float]:
        """Extrae la solución del DUAL en formato dict"""
        solucion = {}
        if self.resultado_dual:
            for var in self.nombres_vars_dual:
                solucion[var] = self.resultado_dual['solucion_variables'].get(var, 0.0)
        return solucion