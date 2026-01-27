import numpy as np

class EsquinaNoreste:
    def __init__(self, costos, oferta, demanda):
        self.costos = np.array(costos)
        self.oferta = list(oferta)  # Trabajamos con listas para manejar índices dinámicos si fuera necesario
        self.demanda = list(demanda)
        self.filas = len(oferta)
        self.columnas = len(demanda)

    def resolver(self):
        """
        Ejecuta el algoritmo de la Esquina Noroeste.
        Returns:
            dict: { 'asignacion': list, 'costo_total': float }
        """
        # Copias para no afectar los atributos originales
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()
        
        asignacion = np.zeros((self.filas, self.columnas), dtype=int)
        
        i = 0
        j = 0
        
        while i < self.filas and j < self.columnas:
            cantidad = min(oferta_restante[i], demanda_restante[j])
            
            asignacion[i, j] = cantidad
            oferta_restante[i] -= cantidad
            demanda_restante[j] -= cantidad
            
            if oferta_restante[i] == 0:
                i += 1
            else:
                j += 1
                
        costo_total = np.sum(asignacion * self.costos)

        return {
            "asignacion": asignacion.tolist(),
            "costo_total": float(costo_total)
        }