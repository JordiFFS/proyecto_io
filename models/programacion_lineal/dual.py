import numpy as np
from typing import List, Dict, Optional
import pandas as pd
from .dos_fases import DosFases


class Dual:
    """
    Método de Dualidad que usa DosFases para resolver correctamente
    problemas con restricciones mixtas (<=, >=, =)
    """

    def __init__(self, c: List[float], A: List[List[float]], b: List[float],
                 signos: List[str] = None, tipo: str = "max",
                 nombres_vars: List[str] = None, nombres_restricciones: List[str] = None):
        self.c_primal_original = np.array(c, dtype=float)
        self.A_primal_original = np.array(A, dtype=float)
        self.b_primal_original = np.array(b, dtype=float)
        self.tipo_primal_original = tipo.lower()

        self.m, self.n = self.A_primal_original.shape

        self.nombres_vars_primal = nombres_vars or [f"x{i + 1}" for i in range(self.n)]
        self.nombres_restricciones = nombres_restricciones or [f"R{i + 1}" for i in range(self.m)]

        if signos is None:
            self.signos_primal_original = ["<="] * self.m
        else:
            self.signos_primal_original = signos

        self.c_dual = None
        self.A_dual = None
        self.b_dual = None
        self.signos_dual = None
        self.nombres_vars_dual = None
        self.tipo_dual_teorico = None

        self.solucion_primal = None
        self.solucion_dual = None
        self.valor_optimo_primal = None
        self.valor_optimo_dual = None

        self.es_optimo_primal = False
        self.es_optimo_dual = False

    def _construir_dual_teorico(self):
        """Construye el dual TEÓRICO"""
        print("\n" + "=" * 80)
        print("CONSTRUYENDO DUAL TEÓRICO")
        print("=" * 80)

        self.nombres_vars_dual = [f"y{i + 1}" for i in range(self.m)]
        self.c_dual = self.b_primal_original.copy()
        self.A_dual = self.A_primal_original.T.copy()
        self.b_dual = self.c_primal_original.copy()

        print(f"\nPRIMAL {self.tipo_primal_original.upper()}:")
        print(f"  c = {self.c_primal_original}")
        print(f"  A = {self.A_primal_original}")
        print(f"  b = {self.b_primal_original}")
        print(f"  Signos: {self.signos_primal_original}")
        print(f"  Variables: {self.nombres_vars_primal}")

        if self.tipo_primal_original == "min":
            # MIN primal => MAX dual
            self.tipo_dual_teorico = "max"
            # MIN con <= => MAX con >=
            # MIN con >= => MAX con <=
            # MIN con = => MAX con =
            self.signos_dual = []
            for signo in self.signos_primal_original:
                if signo == "<=":
                    self.signos_dual.append(">=")
                elif signo == ">=":
                    self.signos_dual.append("<=")
                else:
                    self.signos_dual.append("=")
        else:
            # MAX primal => MIN dual
            self.tipo_dual_teorico = "min"
            # MAX con <= => MIN con <=
            # MAX con >= => MIN con >=
            # MAX con = => MIN con =
            self.signos_dual = list(self.signos_primal_original)

        print(f"\nDUAL {self.tipo_dual_teorico.upper()}:")
        print(f"  c = {self.c_dual}")
        print(f"  A = {self.A_dual}")
        print(f"  b = {self.b_dual}")
        print(f"  Signos: {self.signos_dual}")
        print(f"  Variables: {self.nombres_vars_dual}")

    def _resolver_con_dos_fases(self, c, A, b, signos, tipo, nombres, nombre_problema):
        """Resuelve usando DosFases"""
        print(f"\n{'-' * 80}")
        print(f"RESOLVIENDO {nombre_problema}")
        print(f"{'-' * 80}")

        try:
            # Usar DosFases
            dos_fases = DosFases(c, A, b, signos, tipo=tipo, nombres_vars=nombres)
            resultado = dos_fases.resolver(verbose=False)

            if resultado['exito']:
                print(f"✓ Óptimo encontrado")
                print(f"  Z = {resultado['valor_optimo']}")

                valores = [resultado['solucion_variables'].get(n, 0.0) for n in nombres]
                print(f"  Solución: {dict(zip(nombres, valores))}")
                print(f"  Iteraciones Fase 1: {resultado['iteraciones_fase1']}")
                print(f"  Iteraciones Fase 2: {resultado['iteraciones_fase2']}")

                return True, np.array(valores), resultado['valor_optimo']
            else:
                print(f"✗ {resultado['estado']}")
                print(f"  Infactible: {resultado['es_infactible']}")
                print(f"  No acotado: {resultado['es_no_acotado']}")
                return False, None, None

        except Exception as e:
            print(f"Error en resolución: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None

    def resolver(self, verbose: bool = False) -> Dict:
        """Resuelve el primal y el dual"""
        self._construir_dual_teorico()

        # RESOLVER PRIMAL usando DosFases
        es_opt_p, sol_p, z_p = self._resolver_con_dos_fases(
            self.c_primal_original.tolist(),
            self.A_primal_original.tolist(),
            self.b_primal_original.tolist(),
            self.signos_primal_original,
            self.tipo_primal_original,
            self.nombres_vars_primal,
            "PRIMAL"
        )

        self.es_optimo_primal = es_opt_p
        self.solucion_primal = sol_p if sol_p is not None else np.zeros(self.n)
        self.valor_optimo_primal = z_p

        # RESOLVER DUAL usando DosFases
        es_opt_d, sol_d, z_d = self._resolver_con_dos_fases(
            self.c_dual.tolist(),
            self.A_dual.tolist(),
            self.b_dual.tolist(),
            self.signos_dual,
            self.tipo_dual_teorico,
            self.nombres_vars_dual,
            "DUAL"
        )

        self.es_optimo_dual = es_opt_d
        self.solucion_dual = sol_d if sol_d is not None else np.zeros(self.m)
        self.valor_optimo_dual = z_d

        # VERIFICAR DUALIDAD FUERTE
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DUALIDAD FUERTE")
        print("=" * 80)

        dualidad_fuerte = False
        diferencia = None

        if (self.es_optimo_primal and self.es_optimo_dual and
                self.valor_optimo_primal is not None and self.valor_optimo_dual is not None):
            diferencia = abs(self.valor_optimo_primal - self.valor_optimo_dual)
            dualidad_fuerte = diferencia < 1e-3

            print(f"Z_primal = {self.valor_optimo_primal}")
            print(f"Z_dual = {self.valor_optimo_dual}")
            print(f"Diferencia = {diferencia}")
            print(f"Dualidad fuerte: {'✓ VERIFICADA' if dualidad_fuerte else '✗ NO VERIFICADA'}")
        else:
            print(f"No se puede verificar dualidad fuerte:")
            print(f"  Primal óptimo: {self.es_optimo_primal} (valor: {self.valor_optimo_primal})")
            print(f"  Dual óptimo: {self.es_optimo_dual} (valor: {self.valor_optimo_dual})")

        # Construir soluciones con datos de resultado original
        resultado_primal = {
            'tipo': 'PRIMAL',
            'exito': self.es_optimo_primal,
            'valor_optimo': self.valor_optimo_primal,
            'solucion': {self.nombres_vars_primal[i]: float(self.solucion_primal[i])
                         for i in range(min(len(self.nombres_vars_primal), len(self.solucion_primal)))},
            'iteraciones': 0,
            'es_optimo': self.es_optimo_primal,
            'es_no_acotado': False,
            'es_infactible': not self.es_optimo_primal
        }

        resultado_dual = {
            'tipo': 'DUAL',
            'exito': self.es_optimo_dual,
            'valor_optimo': self.valor_optimo_dual,
            'solucion': {self.nombres_vars_dual[i]: float(self.solucion_dual[i])
                         for i in range(min(len(self.nombres_vars_dual), len(self.solucion_dual)))},
            'iteraciones': 0,
            'es_optimo': self.es_optimo_dual,
            'es_no_acotado': False,
            'es_infactible': not self.es_optimo_dual
        }

        resultado_final = {
            'primal': resultado_primal,
            'dual': resultado_dual,
            'dualidad_fuerte': dualidad_fuerte,
            'diferencia_valores_optimos': float(diferencia) if diferencia is not None else None,
            'tipo_primal_original': self.tipo_primal_original,
            'tipo_dual': self.tipo_dual_teorico,
            'nombres_vars_primal': self.nombres_vars_primal,
            'nombres_vars_dual': self.nombres_vars_dual,
        }

        print("\n" + "=" * 80)
        print("RESULTADO FINAL")
        print("=" * 80)
        print(f"Primal: {resultado_final['primal']['exito']} (Z={resultado_final['primal']['valor_optimo']})")
        print(f"Dual: {resultado_final['dual']['exito']} (Z={resultado_final['dual']['valor_optimo']})")
        print(f"Dualidad fuerte: {resultado_final['dualidad_fuerte']}")

        return resultado_final

    def obtener_comparacion_problemas(self) -> pd.DataFrame:
        """Retorna comparación de primal vs dual"""
        comparacion = {
            'Aspecto': ['Tipo Optimización', 'Variables', 'Restricciones'],
            'Primal': [
                self.tipo_primal_original.upper(),
                f"{self.n}: {', '.join(self.nombres_vars_primal)}",
                f"{self.m}",
            ],
            'Dual': [
                self.tipo_dual_teorico.upper(),
                f"{self.m}: {', '.join(self.nombres_vars_dual)}",
                f"{self.n}",
            ]
        }
        return pd.DataFrame(comparacion)