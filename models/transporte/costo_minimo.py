import numpy as np

class CostoMinimo:
    def __init__(self, costos, oferta, demanda):
        self.costos = np.array(costos, dtype=float)
        self.oferta = np.array(oferta, dtype=int)
        self.demanda = np.array(demanda, dtype=int)
        self.filas = len(oferta)
        self.columnas = len(demanda)

    def resolver(self):
        """
        Ejecuta el algoritmo de Costo Mínimo.
        Returns:
            dict: { 'asignacion': list, 'costo_total': float }
        """
        asignacion = np.zeros((self.filas, self.columnas), dtype=int)
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()
        
        # Copia de costos para enmascarar con infinito los usados
        costos_temp = self.costos.copy()

        while np.sum(oferta_restante) > 0 and np.sum(demanda_restante) > 0:
            # Encontrar el mínimo costo disponible
            min_idx = np.unravel_index(np.argmin(costos_temp), costos_temp.shape)
            i, j = min_idx
            
            cantidad = min(oferta_restante[i], demanda_restante[j])
            
            asignacion[i, j] = cantidad
            oferta_restante[i] -= cantidad
            demanda_restante[j] -= cantidad
            
            # Tachar filas o columnas agotadas
            if oferta_restante[i] == 0:
                costos_temp[i, :] = np.inf
            if demanda_restante[j] == 0:
                costos_temp[:, j] = np.inf

        costo_total = np.sum(asignacion * self.costos)

        return {
            "asignacion": asignacion.tolist(),
            "costo_total": float(costo_total)
        }