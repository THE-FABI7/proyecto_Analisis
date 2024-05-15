from models.GraphManager import GraphManager

class Marginalizar:
    def __init__(self):
        self.particiones = []

    def dataM(self):
        data = GraphManager().cargarArchivo("Data/complete_biparite_grsph.json")
        return data

    def datos(self, nodes, edges):
        con1, con2, edges = GraphManager.obtenerConjuntosGrafoBipartito(
            nodes, edges)
        return con1, con2

    def marginalizar(self, nodes, edges, estadoActual, marginalizar):
        matrices = self.datosMatrices()
        if len(estadoActual) == 1:  # puede ser 1 o 0
            return self.marginalizarUnEstado(matrices, estadoActual, marginalizar)

    def marginalizarUnEstado(self, matrices, estadoActual, marginalizar):
        probabilidad = {}
        lista = list(matrices.keys())

        def calcularProbabilidad(matriz, estados):
            suma = [0, 0]
            for key2 in matriz:
                if all(key2[i] == estados[i] for i in range(len(estados))):
                    suma[0] += matriz[key2][0]/2
                    suma[1] += matriz[key2][1]/2
            return suma

        for k, key in enumerate(lista):
            matriz = matrices[lista[(k+1) % len(lista)]]  # obtenemos la matriz
            for key in matriz:
                estado1, estado2 = key[1], key[2]
                probabilidad[estado1 +
                             estado2] = calcularProbabilidad(matriz, estado2+estado1)
        return probabilidad

    def calcularParticionesDelGrafo(self, nodes, edges, estadoActual):
        conjunto1, conjunto2, aristas = GraphManager(
        ).obtenerConjuntosGrafoBipartito(nodes, edges)
        particiones = self.posiblesParticiones(conjunto1, conjunto2)
        return particiones

    def posiblesParticiones(self, c1, c2):
        c1 = list(c1)  # Convertir el conjunto c1 a lista
        c2 = list(c2)  # Convertir el conjunto c2 a lista
        particiones = {}  # Diccionario para almacenar las particiones
        particiones_set = set()  # Conjunto para almacenar particiones únicas

        def backtrack(conjunto1, conjunto2, particion1, particion2):
            if not conjunto1 and not conjunto2:
                particion = ''.join(map(str, particion1)) + \
                    ',' + ''.join(map(str, particion2))
                if particion not in particiones_set:
                    particiones_set.add(particion)
                    particiones[particion] = (particion1, particion2)
            else:
                if conjunto1:
                    for i in range(len(conjunto1)):
                        backtrack(conjunto1[:i] + conjunto1[i+1:], conjunto2,
                                  particion1 + [conjunto1[i]], particion2)
                if conjunto2:
                    for i in range(len(conjunto2)):
                        backtrack(
                            conjunto1, conjunto2[:i] + conjunto2[i+1:], particion1, particion2 + [conjunto2[i]])

        backtrack(c2, c1, [], [])
        return particiones
