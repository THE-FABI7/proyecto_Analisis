import time
import numpy as np
from Data.datapb.NodeDataRetrieve import NodeDataRetriever
from scipy.stats import wasserstein_distance
import pandas as pd
from src.Probabilidades.Utilities import Utilities
import streamlit_agraph as stag
from Probabilidades.visualizer import Gui
from src.Probabilidades.ProbabilityDistribution import ProbabilityDistribution

class Estrategia:
    def __init__(self):
        self.prob_dist = ProbabilityDistribution()
        pass
    
    def datos_mt(self):
        matrices = NodeDataRetriever()
        return matrices.get_six_node_data()

    def retornar_particion_adecuada(self, conjunto1, conjunto2, estadoActual):
        matrices = self.datos_mt()
        resultado, estados = self.prob_dist.crear_estados_transicion(matrices)
        distribucion_particiones_original = self.prob_dist.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estadoActual, estados)
        particion, diferencia, lista = self.planteamiento_voraz(matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estadoActual)
        return particion, diferencia, lista

    @Utilities.medir_tiempo
    def planteamiento_voraz(self, matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estadoActual):
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
                distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estadoActual, estados)
                distribucion_der = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estadoActual, estados)
                p1 = distribucion_izq[1][1:]
                p2 = distribucion_der[1][1:]
                prodTensor = self.prob_dist.producto_tensor(p1, p2)
                diferencia = self.prob_dist.calcular_emd(distribucion_particiones_original[1][1:], prodTensor)
                fin = time.time()

                if c2_der == [] and c1_der == []:
                    continue
                    
                elif diferencia < menor_diferencia:
                    menor_diferencia = diferencia
                    mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]
                
                aux = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)]
                particiones_evaluadas.append(aux)

                print("--------------------")
                print("diferencia", diferencia)
                print("mejor_particion", mejor_particion)
                print("--------------------")
                
        return mejor_particion, menor_diferencia, particiones_evaluadas
    
    def divide_y_venceras(self, matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estado_actual):
        def merge_sort_partition(conjunto):
            if len(conjunto) <= 1:
                return conjunto
            mid = len(conjunto) // 2
            left_half = merge_sort_partition(conjunto[:mid])
            right_half = merge_sort_partition(conjunto[mid:])
            return left_half, right_half

        def evaluate_partitions(c1_izq, c1_der, c2_izq, c2_der):
            nonlocal menor_diferencia, mejor_particion
            distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estado_actual, estados)
            distribucion_der = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estado_actual, estados)
            p1 = distribucion_izq[1][1:]
            p2 = distribucion_der[1][1:]
            prod_tensor = self.prob_dist.producto_tensor(p1, p2)
            diferencia = self.prob_dist.calcular_emd(distribucion_particiones_original[1][1:], prod_tensor)

            if diferencia < menor_diferencia:
                menor_diferencia = diferencia
                mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]

            particiones_evaluadas.append([(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)])

        mejor_particion = []
        menor_diferencia = float('inf')
        particiones_evaluadas = []

        left_c1, right_c1 = merge_sort_partition(conjunto1)
        left_c2, right_c2 = merge_sort_partition(conjunto2)

        print("left_c1", left_c1)
        print("right_c1", right_c1)
        print("C", left_c2)
        print("right_c2", right_c2)

        left_c2_filtrado = [i[:-1] if "'" in i else i for i in left_c2]
        right_c2_filtrado = [i[:-1] if "'" in i else i for i in right_c2]

        if isinstance(right_c1, tuple):
            right_c1 = sum(right_c1, [])
        if isinstance(right_c2, tuple):
            right_c2 = sum(right_c2, [])

        for i in range(len(left_c1) + 1):
            c1_izq = left_c1[:i]
            c1_der = left_c1[i:] + right_c1
            for j in range(len(left_c2) + 1):
                c2_izq = left_c2[:j]
                c2_der = left_c2[j:] + right_c2
                evaluate_partitions(c1_izq, c1_der, c2_izq, c2_der)

        return mejor_particion, menor_diferencia, particiones_evaluadas
    
    def crear_particiones(self, conjunto1, conjunto2, estadoActual):
        matrices = self.datos_mt()
        particiones = []
        a, b, lista = self.retornar_particion_adecuada(conjunto1, conjunto2, estadoActual)
        df = pd.DataFrame(lista, columns=['Conjunto 1', 'Conjunto 2','Diferencia'])
        return df, particiones
    
    def retornar_distribuciones(self, eActual, eFuturo, valorActual, st):
        matrices = self.datos_mt()
        resultado, estados = self.prob_dist.crear_estados_transicion(matrices)
        datos = self.prob_dist.tabla_distribucion_probabilidades(matrices, eActual, eFuturo, valorActual, estados)
        lista = []
        lista.append(str(datos[0][0]))
            
        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))
        
        df = pd.DataFrame(datos[1:], columns=lista)
        return df
    
    def dibujar_grafo(self, conjunto1, conjunto2, estadoActual, nodes, edges, st):
        mP, a, b = self.retornar_particion_adecuada(conjunto1, conjunto2, estadoActual)
        p1, p2 = mP
        for i in p1[1]:
            if i not in p2[1]:
                for arista in edges:
                    if  arista.source == i and arista.to in p2[0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
        for i in p2[1]:
            if i not in p1[1]:
                for arista in edges:
                    if  arista.source == i and arista.to in p1[0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'

        graph = stag.agraph(nodes=nodes, edges=edges, config=Gui(True))
        return graph
