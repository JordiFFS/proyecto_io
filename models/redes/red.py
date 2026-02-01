"""
Red de distribución Coca-Cola
Adapta la clase Red para manejar plantas, centros de distribución y puntos de venta
"""


class Red:
    def __init__(self, nodos):
        if not nodos or len(nodos) < 2:
            raise ValueError("La red debe tener al menos 2 nodos")

        self.nodos = list(nodos)
        self.arcos = []
        self.oferta_demanda = {n: 0 for n in self.nodos}
        self.tipos_nodo = {}  # Para clasificar nodos: 'planta', 'distribucion', 'venta'

    def agregar_arco(self, origen, destino, costo=0, capacidad=float("inf"), distancia=0):
        if origen not in self.nodos or destino not in self.nodos:
            raise ValueError(f"Arco inválido: {origen} -> {destino}")

        if capacidad < 0:
            raise ValueError("La capacidad no puede ser negativa")

        arco = {
            "origen": origen,
            "destino": destino,
            "costo": costo,
            "capacidad": capacidad,
            "distancia": distancia
        }

        self.arcos.append(arco)

    def set_oferta_demanda(self, nodo, valor):
        if nodo not in self.nodos:
            raise ValueError(f"Nodo inválido: {nodo}")

        self.oferta_demanda[nodo] = valor

    def set_tipo_nodo(self, nodo, tipo):
        """Clasifica el tipo de nodo: 'planta', 'distribucion', 'venta'"""
        if nodo not in self.nodos:
            raise ValueError(f"Nodo inválido: {nodo}")

        self.tipos_nodo[nodo] = tipo

    def validar_balance(self):
        total = sum(self.oferta_demanda.values())
        if total != 0:
            raise ValueError(
                f"La red no está balanceada (suma = {total}). "
                "Oferta total debe ser igual a demanda total."
            )

    def obtener_vecinos(self, nodo):
        return [
            arco for arco in self.arcos
            if arco["origen"] == nodo
        ]

    def obtener_arco(self, origen, destino):
        for arco in self.arcos:
            if arco["origen"] == origen and arco["destino"] == destino:
                return arco
        return None

    def __repr__(self):
        return (
            f"Red(nodos={len(self.nodos)}, "
            f"arcos={len(self.arcos)})"
        )