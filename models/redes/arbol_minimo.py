class ArbolMinimo:
    def __init__(self, nodos):
        self.nodos = nodos
        self.aristas = []

    def agregar_arista(self, u, v, costo):
        self.aristas.append((costo, u, v))

    # ---------------------------
    # Union-Find
    # ---------------------------
    def encontrar(self, padre, i):
        if padre[i] != i:
            padre[i] = self.encontrar(padre, padre[i])
        return padre[i]

    def unir(self, padre, rango, x, y):
        rx = self.encontrar(padre, x)
        ry = self.encontrar(padre, y)

        if rx != ry:
            if rango[rx] < rango[ry]:
                padre[rx] = ry
            elif rango[rx] > rango[ry]:
                padre[ry] = rx
            else:
                padre[ry] = rx
                rango[rx] += 1

    # ---------------------------
    # KRUSKAL
    # ---------------------------
    def resolver(self):
        self.aristas.sort()  # por costo

        padre = {n: n for n in self.nodos}
        rango = {n: 0 for n in self.nodos}

        arbol = []
        costo_total = 0
        iteraciones = []

        for costo, u, v in self.aristas:
            ru = self.encontrar(padre, u)
            rv = self.encontrar(padre, v)

            if ru != rv:
                self.unir(padre, rango, ru, rv)
                arbol.append((u, v, costo))
                costo_total += costo

                iteraciones.append({
                    "arista": f"{u} → {v}",
                    "costo": costo,
                    "costo_acumulado": costo_total
                })

            if len(arbol) == len(self.nodos) - 1:
                break

        return {
            "arbol": arbol,
            "costo_total": costo_total,
            "iteraciones": iteraciones
        }
