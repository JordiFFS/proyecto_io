from collections import deque, defaultdict
import math


class FlujoMaximo:
    def __init__(self, nodos):
        self.nodos = nodos
        self.capacidad = defaultdict(dict)

    def agregar_arco(self, u, v, cap):
        # arco directo
        self.capacidad[u][v] = cap
        # arco residual inverso
        if u not in self.capacidad[v]:
            self.capacidad[v][u] = 0

    def bfs(self, origen, destino, padre):
        visitado = {n: False for n in self.nodos}
        cola = deque([origen])
        visitado[origen] = True
        padre.clear()

        while cola:
            u = cola.popleft()
            for v, cap in self.capacidad[u].items():
                if not visitado[v] and cap > 0:
                    visitado[v] = True
                    padre[v] = u
                    cola.append(v)
                    if v == destino:
                        return True
        return False

    def resolver(self, origen, destino):
        padre = {}
        flujo_maximo = 0
        iteraciones = []

        while self.bfs(origen, destino, padre):
            # cuello de botella
            flujo_camino = math.inf
            v = destino
            ruta = []

            while v != origen:
                u = padre[v]
                flujo_camino = min(flujo_camino, self.capacidad[u][v])
                ruta.append((u, v))
                v = u

            ruta.reverse()

            # actualizar red residual
            for u, v in ruta:
                self.capacidad[u][v] -= flujo_camino
                self.capacidad[v][u] += flujo_camino

            flujo_maximo += flujo_camino

            iteraciones.append({
                "ruta": ruta,
                "flujo_enviado": flujo_camino,
                "flujo_acumulado": flujo_maximo
            })

        return {
            "flujo_maximo": flujo_maximo,
            "iteraciones": iteraciones
        }
