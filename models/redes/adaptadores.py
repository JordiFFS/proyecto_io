"""
Adaptador para convertir la Red de Coca-Cola a matriz de distancias
para algoritmos como Dijkstra
"""

import math


def red_a_matriz_distancias(red):
    """
    Convierte un objeto Red a una matriz de distancias
    para algoritmos como Dijkstra.

    Args:
        red: Objeto Red con nodos y arcos

    Returns:
        matriz: Matriz n×n de distancias
        nodos: Lista de nodos en la red
    """
    nodos = red.nodos
    n = len(nodos)

    indice = {nodo: i for i, nodo in enumerate(nodos)}
    inf = math.inf

    # Crear matriz n×n
    matriz = [[inf] * n for _ in range(n)]

    # Diagonal en 0
    for i in range(n):
        matriz[i][i] = 0

    # Llenar arcos (usar distancia si existe, sino usar costo)
    for arco in red.arcos:
        i = indice[arco["origen"]]
        j = indice[arco["destino"]]

        # Usar distancia si está disponible, sino usar costo
        distancia = arco.get("distancia", arco.get("costo", 0))
        matriz[i][j] = distancia

    return matriz, nodos


def red_a_matriz_costos(red):
    """
    Convierte un objeto Red a una matriz de costos
    para problemas de costo mínimo.

    Args:
        red: Objeto Red con nodos y arcos

    Returns:
        matriz: Matriz n×n de costos
        nodos: Lista de nodos en la red
    """
    nodos = red.nodos
    n = len(nodos)

    indice = {nodo: i for i, nodo in enumerate(nodos)}
    inf = math.inf

    # Crear matriz n×n
    matriz = [[inf] * n for _ in range(n)]

    # Diagonal en 0
    for i in range(n):
        matriz[i][i] = 0

    # Llenar arcos (usar costo)
    for arco in red.arcos:
        i = indice[arco["origen"]]
        j = indice[arco["destino"]]
        matriz[i][j] = arco.get("costo", 0)

    return matriz, nodos


def obtener_info_nodo(red, nodo):
    """
    Obtiene información completa de un nodo
    """
    tipo = red.tipos_nodo.get(nodo, "desconocido")
    oferta_demanda = red.oferta_demanda.get(nodo, 0)

    return {
        "nombre": nodo,
        "tipo": tipo,
        "oferta_demanda": oferta_demanda
    }


def obtener_arcos_desde(red, nodo):
    """
    Obtiene todos los arcos que salen de un nodo
    """
    return [arco for arco in red.arcos if arco["origen"] == nodo]


def obtener_arcos_hacia(red, nodo):
    """
    Obtiene todos los arcos que llegan a un nodo
    """
    return [arco for arco in red.arcos if arco["destino"] == nodo]