from Probabilidades.PartitionGenerator import PartitionGenerator
from Probabilidades.ProbabilityDistribution import ProbabilityDistribution
import pandas as pd
import streamlit_agraph as stag
from Probabilidades.visualizer import Gui
import networkx as nx

class Estrategia02:
    def estrategia2(self, c1, c2, estadoActual, edges):
        self.prob_dist = ProbabilityDistribution()
        matrices = self.prob_dist.datos_mt()
        self.prob_gen = PartitionGenerator(self.prob_dist)
        resultado, estados = self.prob_gen.crear_estados_transicion(matrices)
        
        distribucionProbabilidadOriginal = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1, c2, estadoActual, estados)
        
        mejor_particion = []
        menor_diferencia = float('inf')
        listaParticionesEvaluadas = []
        eliminadas = []
        tiempoEjecucion = 0

        perdidas_aristas = {
            arista: self.calcular_perdida(matrices, estados, distribucionProbabilidadOriginal, c1.copy(), c2.copy(), estadoActual, arista)
            for arista in edges
        }

        aristas_con_perdida = [arista for arista, perdida in perdidas_aristas.items() if perdida != 0]

        if not aristas_con_perdida:
            mejor_particion = [(tuple(c2), ()), ((), tuple(c1))]
            distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, (), tuple(c2), estadoActual, estados)
            distribucion_der = self.prob_dist.tabla_distribucion_probabilidades(matrices, tuple(c1), (), estadoActual, estados)
            p1 = distribucion_izq[1][1:]
            p2 = distribucion_der[1][1:]
            prodTensor = self.prob_dist.producto_tensor(p1, p2)
            diferencia = self.prob_dist.calcular_emd(distribucionProbabilidadOriginal[1][1:], prodTensor)
            aux = [(tuple(c2), ()), ((), tuple(c1)), str(diferencia), str(tiempoEjecucion)]
            listaParticionesEvaluadas.append(aux)
            return mejor_particion, tiempoEjecucion, listaParticionesEvaluadas, eliminadas

        aristas_con_perdida.sort(key=lambda arista: perdidas_aristas[arista])

        while aristas_con_perdida:
            arista_min_perdida = aristas_con_perdida.pop(0)
            eliminadas.append(arista_min_perdida)

            c1_izq = []
            c1_der = list(c1)
            c2_izq = []
            c2_der = list(c2)

            if arista_min_perdida.source in c1_der:
                c1_der.remove(arista_min_perdida.source)
                c1_izq.append(arista_min_perdida.source)
            if arista_min_perdida.to in c2_der:
                c2_der.remove(arista_min_perdida.to)
                c2_izq.append(arista_min_perdida.to)

            distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, tuple(c1_izq), tuple(c2_izq), estadoActual, estados)
            distribucion_der = self.prob_dist.tabla_distribucion_probabilidades(matrices, tuple(c1_der), tuple(c2_der), estadoActual, estados)
            p1 = distribucion_izq[1][1:]
            p2 = distribucion_der[1][1:]
            prodTensor = self.prob_dist.producto_tensor(p1, p2)
            diferencia = self.prob_dist.calcular_emd(distribucionProbabilidadOriginal[1][1:], prodTensor)
    
            for diff in diferencia:
                if diff < menor_diferencia:
                    menor_diferencia = diff
                    mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]

            aux = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia), str(tiempoEjecucion)]
            listaParticionesEvaluadas.append(aux)

        return mejor_particion, menor_diferencia, tiempoEjecucion, listaParticionesEvaluadas, eliminadas

    def calcular_perdida(self, matrices, estados, distribucionProbabilidadOriginal, c1, c2, estadoActual, arista):
        c1_copy = c1.copy()
        c2_copy = c2.copy()

        if arista.source in c1_copy and arista.to in c2_copy:
            c1_copy.remove(arista.source)
            c2_copy.remove(arista.to)
        elif arista.source in c2_copy and arista.to in c1_copy:
            c2_copy.remove(arista.source)
            c1_copy.remove(arista.to)
        else:
            return float('inf')

        distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_copy, c2_copy, estadoActual, estados)
        prodTensor = self.prob_dist.producto_tensor(distribucion_izq[1][1:], distribucion_izq[1][1:])
        diferencia = self.prob_dist.calcular_emd(distribucionProbabilidadOriginal[1][1:], prodTensor)
        return diferencia

    def generarParticiones(self, c1, c2, estadoActual, edges):
        particiones = []
        mejor_particion, menor_diferencia, tiempoEjecucion, listaParticionesEvaluadas, eliminadas = self.estrategia2(c1, c2, estadoActual, edges)
        df = pd.DataFrame(listaParticionesEvaluadas, columns=['Conjunto 1', 'Conjunto 2', 'Diferencia', 'Tiempo de ejecución'])
        return df, particiones

    def dibujar_Grafo(self, c1, c2, estadoActual, nodes, edges, Node, Edge):
        self.prob_dist = ProbabilityDistribution()
        matrices = self.prob_dist.datos_mt()
        self.prob_gen = PartitionGenerator(self.prob_dist)
        transiciones, estados = self.prob_gen.crear_estados_transicion(matrices)

        distribucionProbabilidadOriginal = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1, c2, estadoActual, estados)

        aristas_eliminadas_perdida_cero = set()
        arista_minima_perdida = None
        minima_perdida = float('inf')

        for arista in edges:
            perdida = self.calcular_perdida(matrices, estados, distribucionProbabilidadOriginal, c1.copy(), c2.copy(), estadoActual, arista)
            if perdida == 0:
                aristas_eliminadas_perdida_cero.add((arista.source, arista.to))
            elif perdida < minima_perdida:
                arista_minima_perdida = (arista.source, arista.to)
                minima_perdida = perdida

        mejor_particion, _, _, _, _ = self.estrategia2(c1, c2, estadoActual, edges)
        p1, p2 = mejor_particion

        # Crear un grafo bipartito
        G = nx.Graph()
        G.add_nodes_from(c1, bipartite=0)
        G.add_nodes_from(c2, bipartite=1)
        G.add_edges_from([(n1, n2) for n1 in c1 for n2 in c2])

        # Definir las posiciones de los nodos en dos columnas verticales
        pos = {}
        espacio_vertical = 1000 / (max(len(c1), len(c2)) + 1)
        for i, nodo in enumerate(c1, start=1):
            pos[nodo] = [500, i * espacio_vertical]  # Columna izquierda
        for i, nodo in enumerate(c2, start=1):
            pos[nodo] = [900, i * espacio_vertical]  # Columna derecha

        # Crear una lista de nodos con las nuevas coordenadas
        st_nodes = [Node(id=str(nodo), 
                        label=str(nodo),
                        shape=None,
                        x=pos[nodo][0],  # Coordenada x asignada
                        y=pos[nodo][1],  # Coordenada y asignada
                        color='pink' if nodo in c1 else 'lightblue')  # Color de nodo
                    for nodo in G.nodes()]

        # Crear una lista de aristas
        st_edges = [Edge(source=str(u), target=str(v), type="CURVE_SMOOTH", width=3, directed=True)
                    for u, v in G.edges()]

        # Borrar aristas según la partición
        for arista in st_edges:
            if (arista.source, arista.to) in aristas_eliminadas_perdida_cero:
                arista.color = 'yellow'
                arista.dashes = True
            elif (arista.source, arista.to) == arista_minima_perdida:
                arista.color = 'violet'
                arista.dashes = True

        for i in p1[1]:
            if i not in p2[1]:
                for arista in st_edges:
                    if arista.source == str(i) and arista.to in map(str, p2[0]):
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
        for i in p2[1]:
            if i not in p1[1]:
                for arista in st_edges:
                    if arista.source == str(i) and arista.to in map(str, p1[0]):
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'

        config = stag.Config(width=750, height=750, directed=False, physics=False)
        return stag.agraph(nodes=st_nodes, edges=st_edges, config=config)
