import heapq
import math

class RutaMasCorta:
    def __init__(self, matriz_distancias, nodos):
        self.matriz = matriz_distancias
        self.nodos = nodos
        self.n = len(nodos)

        self.dist = [math.inf] * self.n
        self.pred = [-1] * self.n
        self.visitados = set()

        # HISTORIAL PARA MOSTRAR TODO
        self.iteraciones = []

    def resolver(self, origen_idx):
        self.dist[origen_idx] = 0
        cola = [(0, origen_idx)]

        # Estado inicial
        self._guardar_iteracion(
            nodo_fijado=None,
            relajaciones=[]
        )

        while cola:
            _, u = heapq.heappop(cola)
            if u in self.visitados:
                continue

            self.visitados.add(u)
            relajaciones = []

            # Relajar aristas u -> v
            for v in range(self.n):
                costo = self.matriz[u][v]
                if costo == math.inf or v in self.visitados:
                    continue

                antes = self.dist[v]
                nueva = self.dist[u] + costo

                # GUARDAMOS DATOS (DINÁMICOS)
                relajaciones.append({
                    "desde": self.nodos[u],
                    "hacia": self.nodos[v],
                    "dist_u": self.dist[u],
                    "costo": costo,
                    "nueva": nueva,
                    "antes": antes,
                    "mejora": nueva < antes
                })

                if nueva < self.dist[v]:
                    self.dist[v] = nueva
                    self.pred[v] = u
                    heapq.heappush(cola, (nueva, v))

            self._guardar_iteracion(
                nodo_fijado=self.nodos[u],
                relajaciones=relajaciones
            )

        return self._resultado_final(origen_idx)

    def _guardar_iteracion(self, nodo_fijado, relajaciones):
        self.iteraciones.append({
            "nodo_fijado": nodo_fijado,
            "distancias": {
                self.nodos[i]: (self.dist[i] if self.dist[i] != math.inf else "∞")
                for i in range(self.n)
            },
            "predecesores": {
                self.nodos[i]: (self.nodos[self.pred[i]] if self.pred[i] != -1 else None)
                for i in range(self.n)
            },
            "relajaciones": relajaciones
        })

    def _resultado_final(self, origen_idx):
        rutas = []
        for i in range(self.n):
            ruta = self._reconstruir(i)
            rutas.append({
                "destino": self.nodos[i],
                "distancia": self.dist[i] if self.dist[i] != math.inf else "∞",
                "ruta": " → ".join(self.nodos[j] for j in ruta)
            })

        return {
            "origen": self.nodos[origen_idx],
            "predecesores": {
                self.nodos[i]: (self.nodos[self.pred[i]] if self.pred[i] != -1 else None)
                for i in range(self.n)
            },
            "rutas": rutas
        }

    def _reconstruir(self, i):
        r = []
        while i != -1:
            r.append(i)
            i = self.pred[i]
        return r[::-1]
