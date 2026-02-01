"""
models/transporte/vogel.py
Método de Vogel adaptado para Coca-Cola
"""


class MetodoVogel:
    def __init__(self, costos, oferta, demanda):
        self.costos = costos
        self.oferta = list(oferta)
        self.demanda = list(demanda)
        self.filas = len(oferta)
        self.cols = len(demanda)
        self.asignacion = [[0 for _ in range(self.cols)] for _ in range(self.filas)]
        # AQUÍ GUARDAMOS LA HISTORIA PASO A PASO
        self.pasos = []

    def resolver(self):
        fila_agotada = [False] * self.filas
        col_agotada = [False] * self.cols
        contador = 0
        total_necesario = self.filas + self.cols - 1

        while contador < total_necesario:
            paso_info = {"iteracion": contador + 1}

            # 1. Calcular penalizaciones Fila
            penal_f = []
            info_penal_f = []  # Solo para mostrar en el log
            for i in range(self.filas):
                if not fila_agotada[i]:
                    validos = [self.costos[i][j] for j in range(self.cols) if not col_agotada[j]]
                    if len(validos) >= 2:
                        validos.sort()
                        penal_f.append((validos[1] - validos[0], i))
                        info_penal_f.append(f"F{i + 1}: {validos[1]}-{validos[0]} = {validos[1] - validos[0]}")
                    elif len(validos) == 1:
                        penal_f.append((validos[0], i))
                        info_penal_f.append(f"F{i + 1}: {validos[0]} (Único)")

            # 2. Calcular penalizaciones Columna
            penal_c = []
            info_penal_c = []  # Solo para mostrar en el log
            for j in range(self.cols):
                if not col_agotada[j]:
                    validos = [self.costos[i][j] for i in range(self.filas) if not fila_agotada[i]]
                    if len(validos) >= 2:
                        validos.sort()
                        penal_c.append((validos[1] - validos[0], j))
                        info_penal_c.append(f"D{j + 1}: {validos[1]}-{validos[0]} = {validos[1] - validos[0]}")
                    elif len(validos) == 1:
                        penal_c.append((validos[0], j))
                        info_penal_c.append(f"D{j + 1}: {validos[0]} (Único)")

            if not penal_f and not penal_c:
                break

            # Guardar info del paso
            paso_info["penal_filas_txt"] = info_penal_f
            paso_info["penal_cols_txt"] = info_penal_c

            # 3. Seleccionar mayor penalización
            max_f = max(penal_f, key=lambda x: x[0]) if penal_f else (-1, -1)
            max_c = max(penal_c, key=lambda x: x[0]) if penal_c else (-1, -1)

            f_sel, c_sel = -1, -1

            if max_f[0] >= max_c[0]:
                f_sel = max_f[1]
                paso_info["decision"] = f"🔎 Mayor penalización en Fila {f_sel + 1} (Valor: {max_f[0]})"
                min_cost = float('inf')
                for j in range(self.cols):
                    if not col_agotada[j] and self.costos[f_sel][j] < min_cost:
                        min_cost = self.costos[f_sel][j]
                        c_sel = j
            else:
                c_sel = max_c[1]
                paso_info["decision"] = f"🔎 Mayor penalización en Columna {c_sel + 1} (Valor: {max_c[0]})"
                min_cost = float('inf')
                for i in range(self.filas):
                    if not fila_agotada[i] and self.costos[i][c_sel] < min_cost:
                        min_cost = self.costos[i][c_sel]
                        f_sel = i

            # 4. Asignar
            qty = min(self.oferta[f_sel], self.demanda[c_sel])
            self.asignacion[f_sel][c_sel] = qty
            self.oferta[f_sel] -= qty
            self.demanda[c_sel] -= qty

            paso_info[
                "asignacion"] = f"✏️ Asignamos {qty} unidades a la celda más barata (F{f_sel + 1}, D{c_sel + 1}) [Costo: {self.costos[f_sel][c_sel]}]"

            # ⭐ AGREGAR INFORMACIÓN DE LA CELDA
            paso_info["celda"] = (f_sel, c_sel)
            paso_info["cantidad"] = qty
            paso_info["costo_unitario"] = self.costos[f_sel][c_sel]

            # Guardamos una COPIA de la matriz actual
            paso_info["matriz"] = [fila[:] for fila in self.asignacion]
            self.pasos.append(paso_info)

            if self.oferta[f_sel] == 0:
                fila_agotada[f_sel] = True
            else:
                col_agotada[c_sel] = True

            contador += 1

        return self.asignacion

    def obtener_costo_total(self):
        """
        Calcula el costo total de la solución actual.
        Multiplica cada asignación por su costo unitario correspondiente.

        Returns:
            float: El costo total de transporte
        """
        costo_total = 0
        for i in range(self.filas):
            for j in range(self.cols):
                costo_total += self.asignacion[i][j] * self.costos[i][j]
        return costo_total

    def obtener_asignacion(self):
        """
        Retorna la matriz de asignación actual.

        Returns:
            list: Matriz de asignaciones
        """
        return self.asignacion

    def obtener_pasos(self):
        """
        Retorna todos los pasos del proceso de solución.

        Returns:
            list: Lista de diccionarios con información de cada paso
        """
        return self.pasos