import numpy as np
import pandas as pd
from typing import Tuple, List, Dict


class EsquinaNoreste:
    """
    Método de la Esquina Noroeste para obtener una solución inicial viable
    en problemas de transporte.
    """

    def __init__(self, costos: List[List[float]], oferta: List[float],
                 demanda: List[float], nombres_origenes: List[str] = None,
                 nombres_destinos: List[str] = None):
        """
        Parámetros:
        - costos: matriz de costos (m x n)
        - oferta: vector de oferta (m elementos)
        - demanda: vector de demanda (n elementos)
        - nombres_origenes: nombres de orígenes (opcional)
        - nombres_destinos: nombres de destinos (opcional)
        """
        self.costos = np.array(costos, dtype=float)
        self.oferta = np.array(oferta, dtype=float)
        self.demanda = np.array(demanda, dtype=float)

        self.m, self.n = self.costos.shape

        # Verificar que oferta = demanda
        if not np.isclose(self.oferta.sum(), self.demanda.sum()):
            # Agregar origen o destino ficticio
            diferencia = self.demanda.sum() - self.oferta.sum()
            if diferencia > 0:  # Demanda > Oferta
                self.oferta = np.append(self.oferta, diferencia)
                self.costos = np.vstack([self.costos, np.zeros(self.n)])
                self.m += 1
            else:  # Oferta > Demanda
                self.demanda = np.append(self.demanda, -diferencia)
                self.costos = np.hstack([self.costos, np.zeros((self.m, 1))])
                self.n += 1

        self.nombres_origenes = nombres_origenes or [f"O{i + 1}" for i in range(self.m)]
        self.nombres_destinos = nombres_destinos or [f"D{i + 1}" for i in range(self.n)]

        self.asignacion = np.zeros((self.m, self.n))
        self.costo_total = 0
        self.variables_basicas = 0

    def resolver(self) -> Dict:
        """Aplica el método de esquina noroeste"""
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()

        i, j = 0, 0  # Empezar desde esquina noroeste

        while i < self.m and j < self.n:
            # Asignar la cantidad mínima
            cantidad = min(oferta_restante[i], demanda_restante[j])

            self.asignacion[i, j] = cantidad
            self.costo_total += cantidad * self.costos[i, j]

            oferta_restante[i] -= cantidad
            demanda_restante[j] -= cantidad

            # Mover a la siguiente posición
            if np.isclose(oferta_restante[i], 0):
                i += 1
            if np.isclose(demanda_restante[j], 0):
                j += 1

            if cantidad > 0:
                self.variables_basicas += 1

        return self._generar_resultado()

    def _generar_resultado(self) -> Dict:
        """Genera el resultado de la solución inicial"""
        # Detalles de asignaciones
        asignaciones_detalladas = []
        for i in range(self.m):
            for j in range(self.n):
                if self.asignacion[i, j] > 0:
                    asignaciones_detalladas.append({
                        'origen': self.nombres_origenes[i],
                        'destino': self.nombres_destinos[j],
                        'cantidad': float(self.asignacion[i, j]),
                        'costo_unitario': float(self.costos[i, j]),
                        'costo_total': float(self.asignacion[i, j] * self.costos[i, j])
                    })

        resultado = {
            'metodo': 'Esquina Noroeste',
            'costo_total': float(self.costo_total),
            'asignacion_matriz': self.asignacion.tolist(),
            'asignaciones_detalladas': asignaciones_detalladas,
            'variables_basicas': self.variables_basicas,
            'variables_no_basicas': (self.m * self.n) - self.variables_basicas,
            'es_viable': self.variables_basicas == self.m + self.n - 1
        }
        return resultado

    def obtener_tabla_asignacion(self) -> pd.DataFrame:
        """Retorna la matriz de asignación en formato pandas"""
        return pd.DataFrame(
            self.asignacion,
            index=self.nombres_origenes,
            columns=self.nombres_destinos
        )

    def obtener_tabla_costos(self) -> pd.DataFrame:
        """Retorna la matriz de costos"""
        return pd.DataFrame(
            self.costos,
            index=self.nombres_origenes,
            columns=self.nombres_destinos
        )


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo: 3 orígenes, 4 destinos
    costos = [
        [2, 3, 1, 5],
        [6, 5, 3, 2],
        [1, 2, 5, 4]
    ]

    oferta = [50, 60, 40]
    demanda = [30, 40, 35, 45]

    esquina = EsquinaNoreste(costos, oferta, demanda)
    resultado = esquina.resolver()

    print("\n=== RESULTADO ESQUINA NOROESTE ===")
    print(f"Costo Total: ${resultado['costo_total']:.2f}")
    print(f"Variables Básicas: {resultado['variables_basicas']}")
    print(f"\nMatriz de Asignación:")
    print(esquina.obtener_tabla_asignacion())

    print("\n\nDetalles de Asignaciones:")
    for asig in resultado['asignaciones_detalladas']:
        print(f"{asig['origen']} → {asig['destino']}: {asig['cantidad']} unidades "
              f"@ ${asig['costo_unitario']} = ${asig['costo_total']:.2f}")