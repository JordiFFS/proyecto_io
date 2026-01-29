# models/redes/red.py

class Red:
    def __init__(self, nodos):
        """
        nodos: lista de identificadores (int o str)
        """
        if not nodos or len(nodos) < 2:
            raise ValueError("La red debe tener al menos 2 nodos")

        self.nodos = list(nodos)
        self.arcos = []  # lista de dicts
        self.oferta_demanda = {n: 0 for n in self.nodos}

    # -----------------------------
    # ARCO
    # -----------------------------
    def agregar_arco(self, origen, destino, costo=0, capacidad=float("inf")):
        if origen not in self.nodos or destino not in self.nodos:
            raise ValueError(f"Arco inválido: {origen} -> {destino}")

        if capacidad < 0:
            raise ValueError("La capacidad no puede ser negativa")

        arco = {
            "origen": origen,
            "destino": destino,
            "costo": costo,
            "capacidad": capacidad
        }

        self.arcos.append(arco)

    # -----------------------------
    # OFERTA / DEMANDA
    # -----------------------------
    def set_oferta_demanda(self, nodo, valor):
        if nodo not in self.nodos:
            raise ValueError(f"Nodo inválido: {nodo}")

        self.oferta_demanda[nodo] = valor

    # -----------------------------
    # VALIDACIONES
    # -----------------------------
    def validar_balance(self):
        total = sum(self.oferta_demanda.values())
        if total != 0:
            raise ValueError(
                f"La red no está balanceada (suma = {total}). "
                "Oferta total debe ser igual a demanda total."
            )

    # -----------------------------
    # UTILIDADES
    # -----------------------------
    def obtener_vecinos(self, nodo):
        return [
            arco for arco in self.arcos
            if arco["origen"] == nodo
        ]

    def __repr__(self):
        return (
            f"Red(nodos={len(self.nodos)}, "
            f"arcos={len(self.arcos)})"
        )
