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
        return matrices.get_five_node_data()

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
   
    @Utilities.medir_tiempo
    def busqueda_divide_y_venceras(self, matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estado_actual):
        if len(conjunto1) == 0 or len(conjunto2) == 0:
            return [], float('inf'), []

        mejor_particion = []
        menor_diferencia = float('inf')
        particiones_evaluadas = []

        # Función auxiliar para dividir y evaluar particiones
        def divide_y_evaluar(c1, c2):
            nonlocal mejor_particion, menor_diferencia, particiones_evaluadas
            for i in range(len(c1)):
                c1_izq = c1[:i]
                c1_der = c1[i:]
                c2_izq = []
                c2_der = list(c2)

                for j in range(len(c2)):
                    c2_izq.append(c2_der.pop(0))

                    distribucion_izq = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estado_actual, estados)
                    distribucion_der = self.prob_dist.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estado_actual, estados)
                    p1 = distribucion_izq[1][1:]
                    p2 = distribucion_der[1][1:]
                    prod_tensor = self.prob_dist.producto_tensor(p1, p2)
                    diferencia = self.prob_dist.calcular_emd(distribucion_particiones_original[1][1:], prod_tensor)

                    if c2_der == [] and c1_der == []:
                        continue

                    elif diferencia < menor_diferencia:
                        menor_diferencia = diferencia
                        mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]

                    aux = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)]
                    particiones_evaluadas.append(aux)

        # Dividir los conjuntos en mitades y evaluar
        mid1 = len(conjunto1) // 2
        mid2 = len(conjunto2) // 2

        c1_izq = conjunto1[:mid1]
        c1_der = conjunto1[mid1:]
        c2_izq = conjunto2[:mid2]
        c2_der = conjunto2[mid2:]

        # Evaluar particiones de las mitades divididas
        divide_y_evaluar(c1_izq, c2_izq)
        divide_y_evaluar(c1_der, c2_der)

        # Evaluar particiones cruzadas
        divide_y_evaluar(c1_izq, c2_der)
        divide_y_evaluar(c1_der, c2_izq)

        # Convertir las tuplas a cadenas de texto
        df_lista_particiones = pd.DataFrame([
            {
                'Conjunto 1': str(particion[0]),
                'Conjunto 2': str(particion[1]),
                'Diferencia': particion[2]
            }
            for particion in particiones_evaluadas
        ])

        return mejor_particion, menor_diferencia, df_lista_particiones


    
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