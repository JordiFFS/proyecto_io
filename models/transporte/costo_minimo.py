import numpy as np

def resolver_costo_minimo(costos, oferta, demanda):
    """
    Resuelve el problema de transporte usando el método del Costo Mínimo.
    
    Args:
        costos (list of lists): Matriz de costos unitarios de transporte.
        oferta (list): Lista de capacidades de suministro de cada origen.
        demanda (list): Lista de requerimientos de cada destino.
        
    Returns:
        dict: Diccionario con la matriz de asignación final y el costo total Z.
    """
    # Convertimos a arrays de numpy para facilitar el manejo matricial
    costos = np.array(costos, dtype=float)
    oferta = np.array(oferta, dtype=int)
    demanda = np.array(demanda, dtype=int)
    
    filas, columnas = costos.shape
    asignacion = np.zeros((filas, columnas), dtype=int)
    
    # Copias para no modificar los arreglos originales durante el cálculo
    oferta_restante = oferta.copy()
    demanda_restante = demanda.copy()
    
    # Creamos una máscara de costos donde marcaremos con infinito las celdas ya procesadas
    # para que no vuelvan a ser elegidas como el "mínimo".
    costos_temp = costos.copy()

    # El ciclo continúa mientras quede oferta y demanda por asignar
    while np.sum(oferta_restante) > 0 and np.sum(demanda_restante) > 0:
        
        # Encontramos la posición (i, j) del costo mínimo en la matriz actual
        # argmin devuelve el índice aplanado, unravel_index lo convierte a coordenadas (fila, col)
        min_idx = np.unravel_index(np.argmin(costos_temp), costos_temp.shape)
        i, j = min_idx
        
        # Determinamos cuánto podemos enviar: el mínimo entre lo que tiene el origen y lo que pide el destino
        cantidad = min(oferta_restante[i], demanda_restante[j])
        
        # Asignamos la cantidad
        asignacion[i, j] = cantidad
        oferta_restante[i] -= cantidad
        demanda_restante[j] -= cantidad
        
        # Actualizamos la matriz temporal para "tachar" filas o columnas agotadas
        # Si se agotó la oferta de la fila i, ponemos sus costos en infinito
        if oferta_restante[i] == 0:
            costos_temp[i, :] = np.inf
            
        # Si se agotó la demanda de la columna j, ponemos sus costos en infinito
        if demanda_restante[j] == 0:
            costos_temp[:, j] = np.inf

    # Calculamos el costo total (Z) multiplicando asignaciones por costos unitarios
    costo_total = np.sum(asignacion * costos)

    return {
        "asignacion": asignacion.tolist(),
        "costo_total": int(costo_total)
    }