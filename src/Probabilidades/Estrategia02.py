from Probabilidades.ProbabilityDistribution import ProbabilityDistribution
import pandas as pd
import streamlit_agraph as stag
import networkx as nx
import numpy as np

class Estrategia02:
    def estrategia2(self, conjunto1, conjunto2, estado_actual, aristas):
        prob_dist = ProbabilityDistribution()
        matrices = prob_dist.datos_mt()
        _, estados = prob_dist.crear_estados_transicion(matrices)
        distribucion_probabilidad_original = prob_dist.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estado_actual, estados)
        mejor_particion = []
        menor_diferencia = float('inf')
        particiones_evaluadas = []
        aristas_eliminadas = []
        tiempo_ejecucion = 0

        perdidas_aristas = {arista: self.calcular_perdida(matrices, estados, distribucion_probabilidad_original, conjunto1.copy(), conjunto2.copy(), estado_actual, arista, prob_dist) for arista in aristas}

        aristas_con_perdida = [arista for arista, perdida in perdidas_aristas.items() if perdida != 0]

        if not aristas_con_perdida:
            mejor_particion = [(tuple(conjunto2), ()), ((), tuple(conjunto1))]
            distribucion_izquierda = prob_dist.tabla_distribucion_probabilidades(matrices, (), tuple(conjunto2), estado_actual, estados)
            distribucion_derecha = prob_dist.tabla_distribucion_probabilidades(matrices, tuple(conjunto1), (), estado_actual, estados)
            p1 = distribucion_izquierda[1][1:]
            p2 = distribucion_derecha[1][1:]
            prod_tensor = prob_dist.producto_tensor(p1, p2)
            diferencia = prob_dist.calcular_emd(distribucion_probabilidad_original[1][1:], prod_tensor)
            particion = [(tuple(conjunto2), ()), ((), tuple(conjunto1)), str(diferencia), str(tiempo_ejecucion)]
            particiones_evaluadas.append(particion)
            return mejor_particion, diferencia, tiempo_ejecucion, particiones_evaluadas, aristas_eliminadas

        aristas_con_perdida.sort(key=lambda arista: perdidas_aristas[arista])

        while aristas_con_perdida:
            arista_minima_perdida = aristas_con_perdida.pop(0)
            aristas_eliminadas.append(arista_minima_perdida)

            conjunto1_izquierda, conjunto1_derecha = self.actualizar_conjuntos(conjunto1, arista_minima_perdida, 'source')
            conjunto2_izquierda, conjunto2_derecha = self.actualizar_conjuntos(conjunto2, arista_minima_perdida, 'to')

            distribucion_izquierda = prob_dist.tabla_distribucion_probabilidades(matrices, tuple(conjunto1_izquierda), tuple(conjunto2_izquierda), estado_actual, estados)
            distribucion_derecha = prob_dist.tabla_distribucion_probabilidades(matrices, tuple(conjunto1_derecha), tuple(conjunto2_derecha), estado_actual, estados)
            p1 = distribucion_izquierda[1][1:]
            p2 = distribucion_derecha[1][1:]
            prod_tensor = prob_dist.producto_tensor(p1, p2)
            diferencia = prob_dist.calcular_emd(distribucion_probabilidad_original[1][1:], prod_tensor)

            if diferencia < menor_diferencia:
                menor_diferencia = diferencia
                mejor_particion = [(tuple(conjunto2_izquierda), tuple(conjunto1_izquierda)), (tuple(conjunto2_derecha), tuple(conjunto1_derecha))]

            particion = [(tuple(conjunto2_izquierda), tuple(conjunto1_izquierda)), (tuple(conjunto2_derecha), tuple(conjunto1_derecha)), str(diferencia), str(tiempo_ejecucion)]
            particiones_evaluadas.append(particion)

        return mejor_particion, menor_diferencia, particiones_evaluadas, aristas_eliminadas

    def actualizar_conjuntos(self, conjunto, arista, atributo):
        izquierda = []
        derecha = list(conjunto)
        if getattr(arista, atributo) in derecha:
            derecha.remove(getattr(arista, atributo))
            izquierda.append(getattr(arista, atributo))
        return izquierda, derecha

    def calcular_perdida(self, matrices, estados, distribucion_probabilidad_original, conjunto1, conjunto2, estado_actual, arista, prob_dist):
        conjunto1_copy = conjunto1.copy()
        conjunto2_copy = conjunto2.copy()

        if arista.source in conjunto1_copy and arista.to in conjunto2_copy:
            conjunto1_copy.remove(arista.source)
            conjunto2_copy.remove(arista.to)
        elif arista.source in conjunto2_copy and arista.to in conjunto1_copy:
            conjunto2_copy.remove(arista.source)
            conjunto1_copy.remove(arista.to)
        else:
            return float('inf')

        distribucion_izquierda = prob_dist.tabla_distribucion_probabilidades(matrices, conjunto1_copy, conjunto2_copy, estado_actual, estados)
        prod_tensor = prob_dist.producto_tensor(distribucion_izquierda[1][1:], distribucion_izquierda[1][1:])
        diferencia = prob_dist.calcular_emd(distribucion_probabilidad_original[1][1:], prod_tensor)
        return diferencia

    def crear_particiones(self, conjunto1, conjunto2, estado_actual, aristas):
        particiones = []
        _, _, particiones_evaluadas, _ = self.estrategia2(conjunto1, conjunto2, estado_actual, aristas)
        df = pd.DataFrame(particiones_evaluadas, columns=['Conjunto 1', 'Conjunto 2', 'Diferencia', ''])
        return df, particiones

    def dibujar_grafo(self, conjunto1, conjunto2, estado_actual, nodos, aristas, Node, Edge):
        prob_dist = ProbabilityDistribution()
        matrices = prob_dist.datos_mt()
        _, estados = prob_dist.crear_estados_transicion(matrices)

        distribucion_probabilidad_original = prob_dist.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estado_actual, estados)

        aristas_eliminadas_perdida_cero = set()
        arista_minima_perdida = None
        minima_perdida = float('inf')

        for arista in aristas:
            perdida = self.calcular_perdida(matrices, estados, distribucion_probabilidad_original, conjunto1.copy(), conjunto2.copy(), estado_actual, arista, prob_dist)
            if perdida == 0:
                aristas_eliminadas_perdida_cero.add((arista.source, arista.to))
            elif perdida < minima_perdida:
                arista_minima_perdida = (arista.source, arista.to)
                minima_perdida = perdida

        mejor_particion, _, _, _, _ = self.estrategia2(conjunto1, conjunto2, estado_actual, aristas)
        particion_izquierda, particion_derecha = mejor_particion

        G = nx.Graph()
        G.add_nodes_from(conjunto1, bipartite=0)
        G.add_nodes_from(conjunto2, bipartite=1)
        G.add_edges_from([(nodo1, nodo2) for nodo1 in conjunto1 for nodo2 in conjunto2])

        pos = self.calcular_posiciones(conjunto1, conjunto2)

        nodos_st = [Node(id=str(nodo), 
                        label=str(nodo),
                        shape=None,
                        x=pos[nodo][0],
                        y=pos[nodo][1],
                        color='pink' if nodo in conjunto1 else 'lightblue')
                    for nodo in G.nodes()]

        aristas_st = [Edge(source=str(nodo1), target=str(nodo2), type="CURVE_SMOOTH", width=3, directed=True)
                    for nodo1, nodo2 in G.edges()]

        for arista in aristas_st:
            if (arista.source, arista.target) in aristas_eliminadas_perdida_cero:
                arista.color = 'yellow'
                arista.dashes = True
            elif (arista.source, arista.target) == arista_minima_perdida:
                arista.color = 'violet'
                arista.dashes = True

        self.actualizar_colores_aristas(aristas_st, particion_izquierda, particion_derecha)

        config = stag.Config(width=750, height=750, directed=False, physics=False)
        return stag.agraph(nodes=nodos_st, edges=aristas_st, config=config)

    def calcular_posiciones(self, conjunto1, conjunto2):
        pos = {}
        espacio_vertical = 1000 / (max(len(conjunto1), len(conjunto2)) + 1)
        for i, nodo in enumerate(conjunto1, start=1):
            pos[nodo] = [500, i * espacio_vertical]
        for i, nodo in enumerate(conjunto2, start=1):
            pos[nodo] = [900, i * espacio_vertical]
        return pos

    def actualizar_colores_aristas(self, aristas_st, particion_izquierda, particion_derecha):
        for nodo in particion_izquierda[1]:
            if nodo not in particion_derecha[1]:
                for arista in aristas_st:
                    if arista.source == str(nodo) and arista.target in map(str, particion_derecha[0]):
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
        for nodo in particion_derecha[1]:
            if nodo not in particion_izquierda[1]:
                for arista in aristas_st:
                    if arista.source == str(nodo) and arista.target in map(str, particion_izquierda[0]):
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
