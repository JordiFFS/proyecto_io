import math
import heapq
from copy import deepcopy


class FlujoCostoMinimo:
    """
    Implementación del método de Flujo de Costo Mínimo
    por rutas de menor costo sucesivas.
    """

    def __init__(self, nodos):
        self.nodos = nodos
        self.arcos = []
        self.iteraciones = []

    # -------------------------------------------------
    # DEFINICIÓN DE ARCO
    # -------------------------------------------------
    def agregar_arco(self, origen, destino, capacidad, costo):
        self.arcos.append({
            "origen": origen,
            "destino": destino,
            "capacidad": capacidad,
            "costo": costo
        })

    # -------------------------------------------------
    # MÉTODO PRINCIPAL
    # -------------------------------------------------
    def resolver(self, origen, destino, flujo_requerido):
        flujo_restante = flujo_requerido
        costo_total = 0

        # grafo residual
        residual = deepcopy(self.arcos)

        while flujo_restante > 0:
            ruta, costo_ruta = self._ruta_mas_barata(residual, origen, destino)

            if not ruta:
                raise ValueError("No existe ruta suficiente para enviar todo el flujo")

            # capacidad mínima de la ruta
            capacidad_ruta = min(
                arco["capacidad"] for arco in ruta
            )

            flujo_enviado = min(capacidad_ruta, flujo_restante)
            flujo_restante -= flujo_enviado
            costo_total += flujo_enviado * costo_ruta

            # guardar iteración
            self.iteraciones.append({
                "ruta": [(a["origen"], a["destino"]) for a in ruta],
                "costo_ruta": costo_ruta,
                "flujo_enviado": flujo_enviado,
                "flujo_restante": flujo_restante,
                "costo_acumulado": costo_total
            })

            # actualizar capacidades
            for arco in ruta:
                arco["capacidad"] -= flujo_enviado

        return {
            "costo_total": costo_total,
            "iteraciones": self.iteraciones
        }

    # -------------------------------------------------
    # RUTA MÁS BARATA (DIJKSTRA SOBRE CAPACIDAD > 0)
    # -------------------------------------------------
    def _ruta_mas_barata(self, arcos, origen, destino):
        nodos = self.nodos
        dist = {n: math.inf for n in nodos}
        prev = {n: None for n in nodos}
        dist[origen] = 0

        cola = [(0, origen)]

        while cola:
            d, u = heapq.heappop(cola)
            if u == destino:
                break

            for arco in arcos:
                if arco["origen"] == u and arco["capacidad"] > 0:
                    v = arco["destino"]
                    nd = d + arco["costo"]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = arco
                        heapq.heappush(cola, (nd, v))

        if dist[destino] == math.inf:
            return None, None

        # reconstruir ruta
        ruta = []
        actual = destino
        while actual != origen:
            arco = prev[actual]
            ruta.insert(0, arco)
            actual = arco["origen"]

        return ruta, dist[destino]
