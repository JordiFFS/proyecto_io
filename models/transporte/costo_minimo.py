"""
models/transporte/costo_minimo.py
Modelo de Costo Mínimo adaptado para Coca-Cola
"""

import numpy as np
import copy


class CostoMinimo:
    def __init__(self, costos, oferta, demanda):
        self.costos = np.array(costos, dtype=float)
        self.oferta = np.array(oferta, dtype=int)
        self.demanda = np.array(demanda, dtype=int)
        self.filas = len(oferta)
        self.columnas = len(demanda)
        self.pasos = []
        self.asignacion = None

    def resolver(self):
        asignacion = np.zeros((self.filas, self.columnas), dtype=int)
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()

        costos_temp = self.costos.copy()
        iteracion = 0

        while np.sum(oferta_restante) > 0 and np.sum(demanda_restante) > 0:
            iteracion += 1

            min_idx = np.unravel_index(np.argmin(costos_temp), costos_temp.shape)
            i, j = min_idx

            cantidad = min(oferta_restante[i], demanda_restante[j])

            asignacion[i, j] = cantidad
            oferta_restante[i] -= cantidad
            demanda_restante[j] -= cantidad

            paso = {
                'iteracion': iteracion,
                'celda': (i, j),
                'costo_unitario': float(self.costos[i, j]),
                'cantidad': int(cantidad),
                'costo_celda': float(self.costos[i, j] * cantidad),
                'oferta_restante': int(oferta_restante[i]),
                'demanda_restante': int(demanda_restante[j]),
                'matriz': asignacion.copy().tolist()
            }
            self.pasos.append(paso)

            if oferta_restante[i] == 0:
                costos_temp[i, :] = np.inf
            if demanda_restante[j] == 0:
                costos_temp[:, j] = np.inf

        self.asignacion = asignacion
        costo_total = float(np.sum(asignacion * self.costos))

        return {
            "asignacion": asignacion.tolist(),
            "costo_total": costo_total
        }

    def obtener_costo_total(self):
        if self.asignacion is None:
            return 0
        return float(np.sum(self.asignacion * self.costos))

    def obtener_asignacion(self):
        if self.asignacion is None:
            return None
        return self.asignacion.tolist()

    def obtener_pasos(self):
        return self.pasos