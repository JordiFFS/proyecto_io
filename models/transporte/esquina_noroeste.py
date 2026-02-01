"""
models/transporte/esquina_noroeste.py
Modelo de Esquina Noroeste adaptado para Coca-Cola
"""

import numpy as np


class EsquinaNoreste:
    def __init__(self, costos, oferta, demanda):
        self.costos = np.array(costos, dtype=float)
        self.oferta = list(oferta)
        self.demanda = list(demanda)
        self.filas = len(oferta)
        self.columnas = len(demanda)
        self.pasos = []
        self.asignacion = None

    def resolver(self):
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()

        asignacion = np.zeros((self.filas, self.columnas), dtype=int)

        i = 0
        j = 0
        iteracion = 0

        while i < self.filas and j < self.columnas:
            iteracion += 1
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
                'matriz': asignacion.copy().astype(int).tolist()
            }
            self.pasos.append(paso)

            if oferta_restante[i] == 0:
                i += 1
            else:
                j += 1

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
        return self.asignacion.astype(int).tolist()

    def obtener_pasos(self):
        return self.pasos