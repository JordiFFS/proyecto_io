import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import heapq


class RutaMasCorta:
    """
    Implementación del algoritmo de Dijkstra para encontrar la ruta más corta
    en una red desde un nodo origen a todos los demás nodos.
    """

    def __init__(self, matriz_distancias: List[List[float]],
                 nodos: List[str] = None):
        """
        Parámetros:
        - matriz_distancias: matriz de adyacencia con distancias
                            (usar np.inf para aristas no existentes)
        - nodos: nombres de los nodos (opcional)
        """
        self.matriz_distancias = np.array(matriz_distancias, dtype=float)
        self.n = len(self.matriz_distancias)
        self.nodos = nodos or [f"N{i + 1}" for i in range(self.n)]

        # Crear lista de adyacencia
        self.adyacencia = self._construir_adyacencia()

        self.distancias = None
        self.predecesores = None
        self.rutas = None

    def _construir_adyacencia(self) -> List[List[Tuple[int, float]]]:
        """Construye lista de adyacencia desde matriz de distancias"""
        adyacencia = [[] for _ in range(self.n)]

        for i in range(self.n):
            for j in range(self.n):
                if i != j and not np.isinf(self.matriz_distancias[i, j]):
                    adyacencia[i].append((j, self.matriz_distancias[i, j]))

        return adyacencia

    def resolver(self, nodo_origen: int = 0) -> Dict:
        """
        Ejecuta el algoritmo de Dijkstra desde un nodo origen

        Parámetro:
        - nodo_origen: índice del nodo de partida
        """
        self.distancias = [np.inf] * self.n
        self.predecesores = [-1] * self.n
        visitados = set()

        # Distancia del origen a sí mismo es 0
        self.distancias[nodo_origen] = 0

        # Cola de prioridad: (distancia, nodo)
        cola = [(0, nodo_origen)]

        while cola:
            dist_actual, u = heapq.heappop(cola)

            if u in visitados:
                continue

            visitados.add(u)

            # Si la distancia almacenada es menor, continuar
            if dist_actual > self.distancias[u]:
                continue

            # Revisar vecinos
            for v, peso in self.adyacencia[u]:
                if v not in visitados:
                    nueva_dist = self.distancias[u] + peso

                    if nueva_dist < self.distancias[v]:
                        self.distancias[v] = nueva_dist
                        self.predecesores[v] = u
                        heapq.heappush(cola, (nueva_dist, v))

        return self._generar_resultado(nodo_origen)

    def _obtener_ruta(self, nodo_destino: int) -> List[int]:
        """Reconstruye la ruta desde origen a destino"""
        ruta = []
        actual = nodo_destino

        while actual != -1:
            ruta.append(actual)
            actual = self.predecesores[actual]

        ruta.reverse()
        return ruta

    def _generar_resultado(self, nodo_origen: int) -> Dict:
        """Genera el resultado del algoritmo"""
        self.rutas = {}

        rutas_detalladas = []
        for i in range(self.n):
            ruta = self._obtener_ruta(i)
            self.rutas[i] = ruta

            ruta_str = " → ".join([self.nodos[j] for j in ruta])

            rutas_detalladas.append({
                'destino': self.nodos[i],
                'distancia': float(self.distancias[i]),
                'ruta': ruta_str,
                'ruta_indices': ruta
            })

        resultado = {
            'algoritmo': 'Dijkstra',
            'nodo_origen': self.nodos[nodo_origen],
            'nodo_origen_idx': nodo_origen,
            'rutas': rutas_detalladas,
            'distancias': {self.nodos[i]: float(self.distancias[i])
                           for i in range(self.n)},
            'predecesores': {self.nodos[i]: self.nodos[self.predecesores[i]]
            if self.predecesores[i] != -1 else None
                             for i in range(self.n)}
        }

        return resultado

    def obtener_tabla_resultados(self) -> pd.DataFrame:
        """Retorna tabla con resultados ordenados"""
        if self.rutas is None:
            return None

        datos = []
        for i in range(self.n):
            ruta = " → ".join([self.nodos[j] for j in self.rutas[i]])
            datos.append({
                'Destino': self.nodos[i],
                'Distancia': float(self.distancias[i]),
                'Ruta': ruta
            })

        df = pd.DataFrame(datos)
        return df.sort_values('Distancia')


class RutaMasOscura(RutaMasCorta):
    """
    Variante para encontrar la ruta más larga (menos oscura)
    Implementación del algoritmo de Bellman-Ford modificado
    """

    def resolver_bellman_ford(self, nodo_origen: int = 0) -> Dict:
        """Implementa Bellman-Ford para detectar ciclos negativos"""
        distancias = [np.inf] * self.n
        predecesores = [-1] * self.n

        distancias[nodo_origen] = 0

        # Relajar aristas |V|-1 veces
        for _ in range(self.n - 1):
            for u in range(self.n):
                if distancias[u] != np.inf:
                    for v, peso in self.adyacencia[u]:
                        if distancias[u] + peso < distancias[v]:
                            distancias[v] = distancias[u] + peso
                            predecesores[v] = u

        # Verificar ciclos negativos
        ciclo_negativo = False
        for u in range(self.n):
            if distancias[u] != np.inf:
                for v, peso in self.adyacencia[u]:
                    if distancias[u] + peso < distancias[v]:
                        ciclo_negativo = True
                        break

        self.distancias = distancias
        self.predecesores = predecesores

        resultado = self._generar_resultado(nodo_origen)
        resultado['ciclo_negativo_detectado'] = ciclo_negativo

        return resultado


# Ejemplo de uso
if __name__ == "__main__":
    # Matriz de distancias (usar np.inf para aristas no existentes)
    inf = np.inf
    distancias = [
        [0, 4, 2, inf, inf, inf],  # A
        [inf, 0, 1, 5, inf, inf],  # B
        [inf, inf, 0, 8, 10, inf],  # C
        [inf, inf, inf, 0, 2, 6],  # D
        [inf, inf, inf, inf, 0, 3],  # E
        [inf, inf, inf, inf, inf, 0]  # F
    ]

    nodos = ['A', 'B', 'C', 'D', 'E', 'F']

    dijkstra = RutaMasCorta(distancias, nodos)
    resultado = dijkstra.resolver(nodo_origen=0)

    print("\n=== RESULTADO RUTA MÁS CORTA (DIJKSTRA) ===")
    print(f"Nodo Origen: {resultado['nodo_origen']}")
    print("\nDistancias Mínimas:")
    for dest, dist in resultado['distancias'].items():
        print(f"  {resultado['nodo_origen']} → {dest}: {dist}")

    print("\nTabla de Resultados:")
    print(dijkstra.obtener_tabla_resultados())