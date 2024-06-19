import time
import numpy as np
from Data.datapb.NodeDataRetrieve import NodeDataRetriever
from scipy.stats import wasserstein_distance
import pandas as pd
from src.Probabilidades.Utilities import Utilities
import streamlit_agraph as stag
from Probabilidades.visualizer import Gui
from src.Probabilidades.ProbabilityDistribution import ProbabilityDistribution
import networkx as nx

class Estrategia:
    def __init__(self):
        self.distribucion_prob = ProbabilityDistribution()

    def retornar_particion_adecuada(self, conjunto1, conjunto2, estado_actual):

        matrices = self.distribucion_prob.datos_mt()
        resultado, estados = self.distribucion_prob.crear_estados_transicion(matrices)
        distribucion_original = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estado_actual, estados)
        #Puede cambiar la estrategia de particionamiento
        particion, diferencia, lista = self.planteamiento_voraz(matrices, estados, distribucion_original, conjunto1, conjunto2, estado_actual)
        return particion, diferencia, lista

    @Utilities.medir_tiempo
    def planteamiento_voraz(self, matrices, estados, distribucion_original, conjunto1, conjunto2, estado_actual):
        mejor_particion = []
        menor_diferencia = float('inf')
        particiones_evaluadas = []

        for i in range(len(conjunto1)):
            c1_izq = conjunto1[:i]
            c1_der = conjunto1[i:]
            c2_izq = []
            c2_der = list(conjunto2)

            for j in range(len(conjunto2)):
                c2_izq.append(c2_der.pop(0))

                inicio = time.time()
                distribucion_izq = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estado_actual, estados)
                distribucion_der = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estado_actual, estados)
                prob1 = distribucion_izq[1][1:]
                prob2 = distribucion_der[1][1:]
                producto_tensor = self.distribucion_prob.producto_tensor(prob1, prob2)
                diferencia = self.distribucion_prob.calcular_emd(distribucion_original[1][1:], producto_tensor)
                fin = time.time()

                if not c2_der and not c1_der:
                    continue
                    
                elif diferencia < menor_diferencia:
                    menor_diferencia = diferencia
                    mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]
                
                particion_evaluada = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)]
                particiones_evaluadas.append(particion_evaluada)

                print("--------------------")
                print("diferencia", diferencia)
                print("mejor_particion", mejor_particion)
                print("--------------------")
                
        return mejor_particion, menor_diferencia, particiones_evaluadas
   
    @Utilities.medir_tiempo
    def busqueda_divide_y_venceras(self, matrices, estados, distribucion_original, conjunto1, conjunto2, estado_actual):
        if not conjunto1 or not conjunto2:
            return [], float('inf'), []

        mejor_particion = []
        menor_diferencia = float('inf')
        particiones_evaluadas = []

        def dividir_y_evaluar(c1, c2):
            nonlocal mejor_particion, menor_diferencia, particiones_evaluadas
            for i in range(len(c1)):
                c1_izq = c1[:i]
                c1_der = c1[i:]
                c2_izq = []
                c2_der = list(c2)

                for j in range(len(c2)):
                    c2_izq.append(c2_der.pop(0))

                    distribucion_izq = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estado_actual, estados)
                    distribucion_der = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estado_actual, estados)
                    prob1 = distribucion_izq[1][1:]
                    prob2 = distribucion_der[1][1:]
                    producto_tensor = self.distribucion_prob.producto_tensor(prob1, prob2)
                    diferencia = self.distribucion_prob.calcular_emd(distribucion_original[1][1:], producto_tensor)

                    if not c2_der and not c1_der:
                        continue

                    elif diferencia < menor_diferencia:
                        menor_diferencia = diferencia
                        mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]

                    particion_evaluada = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)]
                    particiones_evaluadas.append(particion_evaluada)

        mid1 = len(conjunto1) // 2
        mid2 = len(conjunto2) // 2

        c1_izq = conjunto1[:mid1]
        c1_der = conjunto1[mid1:]
        c2_izq = conjunto2[:mid2]
        c2_der = conjunto2[mid2:]

        dividir_y_evaluar(c1_izq, c2_izq)
        dividir_y_evaluar(c1_der, c2_der)
        dividir_y_evaluar(c1_izq, c2_der)
        dividir_y_evaluar(c1_der, c2_izq)

        df_lista_particiones = pd.DataFrame([
            {
                'Conjunto 1': str(particion[0]),
                'Conjunto 2': str(particion[1]),
                'Diferencia': particion[2]
            }
            for particion in particiones_evaluadas
        ])

        return mejor_particion, menor_diferencia, df_lista_particiones

    def crear_particiones(self, conjunto1, conjunto2, estado_actual):
        matrices = self.distribucion_prob.datos_mt()
        particiones = []
        particion, diferencia, lista = self.retornar_particion_adecuada(conjunto1, conjunto2, estado_actual)
        df = pd.DataFrame(lista, columns=['Conjunto 1', 'Conjunto 2', 'Diferencia'])
        return df, particiones
    
    def retornar_distribuciones(self, estado_actual, estado_futuro, valor_actual, st):
        matrices = self.distribucion_prob.datos_mt()
        resultado, estados = self.distribucion_prob.crear_estados_transicion(matrices)
        datos = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, estado_actual, estado_futuro, valor_actual, estados)
        lista = [str(datos[0][0])]
            
        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))
        
        df = pd.DataFrame(datos[1:], columns=lista)
        return df
    
    def dibujar_grafo(self, conjunto1, conjunto2, estado_actual, nodos, aristas, st):
        mejor_particion, _, _ = self.retornar_particion_adecuada(conjunto1, conjunto2, estado_actual)
        if not mejor_particion:
            return stag.agraph(nodes=nodos, edges=aristas, config=Gui(directed=False))
        particion1, particion2 = mejor_particion

        # Crear el grafo con NetworkX
        G = nx.Graph()
        G.add_nodes_from(conjunto1, bipartite=0)
        G.add_nodes_from(conjunto2, bipartite=1)
        G.add_edges_from([(arista.source, arista.to) for arista in aristas])

        # Posiciones de los nodos para mantener la estructura bipartita
        pos = {}
        
        # Ajusta estos valores para cambiar la posición horizontal
        x_conjunto1 = 250 
        x_conjunto2 = 250  # Ajusta este valor para cambiar la posición horizontal

        # Ajusta este valor para cambiar el espacio vertical
        espacio_vertical = 500 / (max(len(conjunto1), len(conjunto2)) + 1)

        # Colocar los nodos del conjunto1 (izquierda)
        for i, nodo in enumerate(conjunto1, start=1):
            pos[nodo] = [x_conjunto1, i * espacio_vertical]

        # Filtrar apóstrofes de los nodos en conjunto2 y mantener el mapeo original
        conjunto2_sin_apostrofe = {nodo: nodo.rstrip("'") for nodo in conjunto2}

        # Colocar los nodos del conjunto2 (derecha)
        for i, nodo in enumerate(conjunto2, start=1):
            pos[conjunto2_sin_apostrofe[nodo]] = [x_conjunto2, i * espacio_vertical]

        # Definir los nodos con su estilo
        nodos_st = [stag.Node(id=str(nodo), 
                            label=str(nodo),
                            x=pos[nodo.rstrip("'")][0],
                            y=pos[nodo.rstrip("'")][1],
                            color='pink' if nodo in conjunto1 else 'lightblue')
                    for nodo in G.nodes()]

        # Definir las aristas con su estilo
        aristas_st = [stag.Edge(source=str(arista.source), target=str(arista.to), type="CURVE_SMOOTH", width=3, directed=False)
                    for arista in aristas]

        # Actualizar colores de las aristas según la partición
        for arista in aristas_st:
            if (arista.source in particion1[1] and arista.to in particion2[0]) or (arista.source in particion2[1] and arista.to in particion1[0]):
                arista.dashes = True
                arista.color = 'rgba(254, 20, 56, 0.5)'

        #config = stag.Config(width=1000, height=1000, directed=False, physics=False)
        return stag.agraph(nodes=nodos_st, edges=aristas_st, config=Gui(directed=True))







