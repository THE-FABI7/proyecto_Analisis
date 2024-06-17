import time

import pandas as pd
from Probabilidades.ProbabilityDistribution import ProbabilityDistribution
from models.GraphManager import GraphManager
import numpy as np
from itertools import chain, combinations
import networkx as nx
import random
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt


class estrategia2:
    def estrategia2(self, c1, c2, estadoActual, edges):
        p = ProbabilityDistribution()
        matrices = ProbabilityDistribution.datos_mt()
        resultado, estados = ProbabilityDistribution.generarEstadoTransicion(self,
            matrices)
        distribucionProbabilidadOriginal = ProbabilityDistribution.generar_distribucion_probabilidades(
            matrices, c1, c2, estadoActual, estados)
        mejor_particion = []
        menor_diferencia = float('inf')
        listaParticionesEvaluadas = []
        eliminadas = []

        edges = [arista for arista in edges if estrategia2.calcular_perdida(self,
            matrices, estados, distribucionProbabilidadOriginal, c1.copy(), c2.copy(), estadoActual, arista, p) != 0]

        while edges:
            inicio = time.time()
            edges.sort(key=lambda arista: self.calcular_perdida(self,
                matrices, estados, distribucionProbabilidadOriginal, c1.copy(), c2.copy(), estadoActual, arista, p))
            arista_min_perdida = edges.pop(0)

            if self.calcular_perdida(self, matrices, estados, distribucionProbabilidadOriginal, c1.copy(), c2.copy(), estadoActual, arista_min_perdida, p) == 0:
                eliminadas.append(arista_min_perdida)
                continue

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

            distribucion_izq = ProbabilityDistribution.generar_distribucion_probabilidades(
                matrices, tuple(c1_izq), tuple(c2_izq), estadoActual, estados)
            distribucion_der = ProbabilityDistribution.generar_distribucion_probabilidades(
                matrices, tuple(c1_der), tuple(c2_der), estadoActual, estados)
            p1 = distribucion_izq[1][1:]
            p2 = distribucion_der[1][1:]

            prodTensor = ProbabilityDistribution.producto_tensor(p1, p2)
            diferencia = ProbabilityDistribution.calcular_emd(
                distribucionProbabilidadOriginal[1][1:], prodTensor)
            fin = time.time()
            tiempoEjecucion = fin - inicio

            aux = []
            if c2_der == [] and c1_der == []:
                continue
            elif diferencia < menor_diferencia:
                menor_diferencia = diferencia
                mejor_particion = [(tuple(c2_izq), tuple(
                    c1_izq)), (tuple(c2_der), tuple(c1_der))]

            aux = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der),
                                                    tuple(c1_der)), str(diferencia), str(tiempoEjecucion)]
            listaParticionesEvaluadas.append(aux)
            eliminadas.append(arista_min_perdida)
        return mejor_particion, menor_diferencia, tiempoEjecucion, listaParticionesEvaluadas

   
    def calcular_perdida(self, matrices, estados, distribucionProbabilidadOriginal, c1, c2, estadoActual, arista, p):
        if arista.source in c1:
            c1.remove(arista.source)
            if arista.to in c2:
                c2.remove(arista.to)
        elif arista.source in c2:
            c2.remove(arista.source)
            if arista.to in c1:
                c1.remove(arista.to)
        else:
            return float('inf')
        
        
        distribucion_izq = ProbabilityDistribution.generar_distribucion_probabilidades(matrices, c1, c2, estadoActual, estados)
        prodTensor = ProbabilityDistribution.producto_tensor(distribucion_izq[1][1:], distribucion_izq[1][1:])
        diferencia = ProbabilityDistribution.calcular_emd(distribucionProbabilidadOriginal[1][1:], prodTensor)
        return diferencia
    
    def generarParticiones(self, c1, c2, estadoActual, edges):
        
        particiones = []
        a, b,c, lista = self.estrategia2(c1, c2, estadoActual, edges)
        #print(lista)
        df = pd.DataFrame(lista, columns=['Conjunto 1', 'Conjunto 2','Diferencia', 'Tiempo de ejecución'])
        return df, particiones