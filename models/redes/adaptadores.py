import math

def red_a_matriz_distancias(red):
    """
    Convierte un objeto Red a una matriz de distancias
    para algoritmos como Dijkstra.
    """
    nodos = red.nodos
    n = len(nodos)

    indice = {nodo: i for i, nodo in enumerate(nodos)}
    inf = math.inf

    # matriz nxn
    matriz = [[inf] * n for _ in range(n)]

    # diagonal en 0
    for i in range(n):
        matriz[i][i] = 0

    # llenar arcos
    for arco in red.arcos:
        i = indice[arco["origen"]]
        j = indice[arco["destino"]]
        matriz[i][j] = arco["costo"]

    return matriz, nodos
