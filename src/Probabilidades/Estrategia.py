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
        self.distribucion_prob = ProbabilityDistribution()
    
    def obtener_matrices(self):
        recuperador = NodeDataRetriever()
        return recuperador.get_six_node_data()

    def retornar_particion_adecuada(self, conjunto1, conjunto2, estado_actual):
        matrices = self.obtener_matrices()
        resultado, estados = self.distribucion_prob.crear_estados_transicion(matrices)
        distribucion_original = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estado_actual, estados)
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
        matrices = self.obtener_matrices()
        particiones = []
        particion, diferencia, lista = self.retornar_particion_adecuada(conjunto1, conjunto2, estado_actual)
        df = pd.DataFrame(lista, columns=['Conjunto 1', 'Conjunto 2', 'Diferencia'])
        return df, particiones
    
    def retornar_distribuciones(self, estado_actual, estado_futuro, valor_actual, st):
        matrices = self.obtener_matrices()
        resultado, estados = self.distribucion_prob.crear_estados_transicion(matrices)
        datos = self.distribucion_prob.tabla_distribucion_probabilidades(matrices, estado_actual, estado_futuro, valor_actual, estados)
        lista = [str(datos[0][0])]
            
        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))
        
        df = pd.DataFrame(datos[1:], columns=lista)
        return df
    
    def dibujar_grafo(self, conjunto1, conjunto2, estado_actual, nodos, aristas, st):
        mejor_particion, _, _ = self.retornar_particion_adecuada(conjunto1, conjunto2, estado_actual)
        particion1, particion2 = mejor_particion
        for nodo in particion1[1]:
            if nodo not in particion2[1]:
                for arista in aristas:
                    if arista.source == nodo and arista.to in particion2[0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
        for nodo in particion2[1]:
            if nodo not in particion1[1]:
                for arista in aristas:
                    if arista.source == nodo and arista.to in particion1[0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'

        grafo = stag.agraph(nodes=nodos, edges=aristas, config=Gui(True))
        return grafo
