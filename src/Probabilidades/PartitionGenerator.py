from itertools import combinations
import pandas as pd
import numpy as np
from scipy.stats import wasserstein_distance
from Probabilidades.Utilities import Utilities

class PartitionGenerator:
    """
    Clase encargada de generar particiones y combinaciones de conjuntos de nodos.
    """

    def __init__(self, prob_dist):
        """
        Inicializa la clase con una distribución de probabilidades.

        Args:
            prob_dist (ProbabilityDistribution): Objeto de la clase ProbabilityDistribution.
        """
        self.prob_dist = prob_dist

    
    def crear_estados_transicion(self, subconjuntos):
        """
        Genera los estados de transición para un conjunto de nodos.

        Args:
            subconjuntos (dict): Diccionario de subconjuntos.

        Returns:
            tuple: Diccionario de transiciones y lista de estados.
        """
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def aux(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(subconjuntos[estado][estado_actual_tuple] for estado in estados)
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                aux(i + 1)
                estado_actual[i] = 1
                aux(i + 1)

        aux(0)
        return transiciones, estados
    
    def retornar_futuros(self):
        """
        Retorna los estados futuros del sistema.

        Returns:
            list: Lista de estados futuros.
        """
        datos = self.prob_dist.datos_mt()
        resultado, estados = self.crear_estados_transicion(datos)
        for i in range(len(estados)):
            estados[i] = estados[i] + "'"
        return estados
    
    def retornar_estados(self):
        """
        Retorna los estados del sistema.

        Returns:
            list: Lista de estados.
        """
        datos = self.prob_dist.datos_mt()
        resultado, estados = self.crear_estados_transicion(datos)
        return estados

    def retornar_valor_actual(self, conjunto1):
        """
        Retorna los valores actuales del sistema basados en los conjuntos dados.

        Args:
            conjunto1 (list): Conjunto de nodos.

        Returns:
            list: Lista de valores actuales.
        """
        datos = self.prob_dist.datos_mt()
        lista = []
        if len(conjunto1) == 1:
            lista.append((0))
            lista.append((1))
        elif len(conjunto1) == 2:
            lista.append((0, 0))
            lista.append((0, 1))
            lista.append((1, 0))
            lista.append((1, 1))
        elif len(conjunto1) == 3:
            lista.append((0, 0, 0))
            lista.append((0, 0, 1))
            lista.append((0, 1, 0))
            lista.append((0, 1, 1))
            lista.append((1, 0, 0))
            lista.append((1, 0, 1))
            lista.append((1, 1, 0))
            lista.append((1, 1, 1))
        elif len(conjunto1) == 4:
            lista.append((0, 0, 0, 0))
            lista.append((0, 0, 0, 1))
            lista.append((0, 0, 1, 0))
            lista.append((0, 0, 1, 1))
            lista.append((0, 1, 0, 0))
            lista.append((0, 1, 0, 1))
            lista.append((0, 1, 1, 0))
            lista.append((0, 1, 1, 1))
            lista.append((1, 0, 0, 0))
            lista.append((1, 0, 0, 1))
            lista.append((1, 0, 1, 0))
            lista.append((1, 0, 1, 1))
            lista.append((1, 1, 0, 0))
            lista.append((1, 1, 0, 1))
            lista.append((1, 1, 1, 0))
            lista.append((1, 1, 1, 1))
        elif len(conjunto1) == 5:
            lista.append((0, 0, 0, 0, 0))
            lista.append((0, 0, 0, 0, 1))
            lista.append((0, 0, 0, 1, 0))
            lista.append((0, 0, 0, 1, 1))
            lista.append((0, 0, 1, 0, 0))
            lista.append((0, 0, 1, 0, 1))
            lista.append((0, 0, 1, 1, 0))
            lista.append((0, 0, 1, 1, 1))
            lista.append((0, 1, 0, 0, 0))
            lista.append((0, 1, 0, 0, 1))
            lista.append((0, 1, 0, 1, 0))
            lista.append((0, 1, 0, 1, 1))
            lista.append((0, 1, 1, 0, 0))
            lista.append((0, 1, 1, 0, 1))
            lista.append((0, 1, 1, 1, 0))
            lista.append((0, 1, 1, 1, 1))
            lista.append((1, 0, 0, 0, 0))
            lista.append((1, 0, 0, 0, 1))
            lista.append((1, 0, 0, 1, 0))
            lista.append((1, 0, 0, 1, 1))
            lista.append((1, 0, 1, 0, 0))
            lista.append((1, 0, 1, 0, 1))
            lista.append((1, 0, 1, 1, 0))
            lista.append((1, 0, 1, 1, 1))
            lista.append((1, 1, 0, 0, 0))
            lista.append((1, 1, 0, 0, 1))
            lista.append((1, 1, 0, 1, 0))
            lista.append((1, 1, 0, 1, 1))
            lista.append((1, 1, 1, 0, 0))
            lista.append((1, 1, 1, 0, 1))
            lista.append((1, 1, 1, 1, 0))
            lista.append((1, 1, 1, 1, 1))
        elif len(conjunto1) == 6:
            lista.append((0, 0, 0, 0, 0, 0))
            lista.append((0, 0, 0, 0, 0, 1))
            lista.append((0, 0, 0, 0, 1, 0))
            lista.append((0, 0, 0, 0, 1, 1))
            lista.append((0, 0, 0, 1, 0, 0))
            lista.append((0, 0, 0, 1, 0, 1))
            lista.append((0, 0, 0, 1, 1, 0))
            lista.append((0, 0, 0, 1, 1, 1))
            lista.append((0, 0, 1, 0, 0, 0))
            lista.append((0, 0, 1, 0, 0, 1))
            lista.append((0, 0, 1, 0, 1, 0))
            lista.append((0, 0, 1, 0, 1, 1))
            lista.append((0, 0, 1, 1, 0, 0))
            lista.append((0, 0, 1, 1, 0, 1))
            lista.append((0, 0, 1, 1, 1, 0))
            lista.append((0, 0, 1, 1, 1, 1))
            lista.append((0, 1, 0, 0, 0, 0))
            lista.append((0, 1, 0, 0, 0, 1))
            lista.append((0, 1, 0, 0, 1, 0))
            lista.append((0, 1, 0, 0, 1, 1))
            lista.append((0, 1, 0, 1, 0, 0))
            lista.append((0, 1, 0, 1, 0, 1))
            lista.append((0, 1, 0, 1, 1, 0))
            lista.append((0, 1, 0, 1, 1, 1))
            lista.append((0, 1, 1, 0, 0, 0))
            lista.append((0, 1, 1, 0, 0, 1))
            lista.append((0, 1, 1, 0, 1, 0))
            lista.append((0, 1, 1, 0, 1, 1))
            lista.append((0, 1, 1, 1, 0, 0))
            lista.append((0, 1, 1, 1, 0, 1))
            lista.append((0, 1, 1, 1, 1, 0))
            lista.append((0, 1, 1, 1, 1, 1))
            lista.append((1, 0, 0, 0, 0, 0))
            lista.append((1, 0, 0, 0, 0, 1))
            lista.append((1, 0, 0, 0, 1, 0))
            lista.append((1, 0, 0, 0, 1, 1))
            lista.append((1, 0, 0, 1, 0, 0))
            lista.append((1, 0, 0, 1, 0, 1))
            lista.append((1, 0, 0, 1, 1, 0))
            lista.append((1, 0, 0, 1, 1, 1))
            lista.append((1, 0, 1, 0, 0, 0))
            lista.append((1, 0, 1, 0, 0, 1))
            lista.append((1, 0, 1, 0, 1, 0))
            lista.append((1, 0, 1, 0, 1, 1))
            lista.append((1, 0, 1, 1, 0, 0))
            lista.append((1, 0, 1, 1, 0, 1))
            lista.append((1, 0, 1, 1, 1, 0))
            lista.append((1, 0, 1, 1, 1, 1))
            lista.append((1, 1, 0, 0, 0, 0))
            lista.append((1, 1, 0, 0, 0, 1))
            lista.append((1, 1, 0, 0, 1, 0))
            lista.append((1, 1, 0, 0, 1, 1))
            lista.append((1, 1, 0, 1, 0, 0))
            lista.append((1, 1, 0, 1, 0, 1))
            lista.append((1, 1, 0, 1, 1, 0))
            lista.append((1, 1, 0, 1, 1, 1))
            lista.append((1, 1, 1, 0, 0, 0))
            lista.append((1, 1, 1, 0, 0, 1))
            lista.append((1, 1, 1, 0, 1, 0))
            lista.append((1, 1, 1, 0, 1, 1))
            lista.append((1, 1, 1, 1, 0, 0))
            lista.append((1, 1, 1, 1, 0, 1))
            lista.append((1, 1, 1, 1, 1, 0))
            lista.append((1, 1, 1, 1, 1, 1))
        else:
            for k, v in datos.items():
                for k2, v2 in v.items():
                    lista.append(k2)
                break
        return lista
    
    def retornar_distribucion(self, estado_actual, estado_futuro, valor_actual):
        """
        Retorna la distribución de probabilidades para los estados actuales y futuros.

        Args:
            estado_actual (list): Estado actual.
            estado_futuro (list): Estado futuro.
            valor_actual (tuple): Valor actual.

        Returns:
            DataFrame: DataFrame con la distribución de probabilidades.
        """

        matrices = self.prob_dist.datos_mt()
        resultado, estados = self.crear_estados_transicion(matrices)


        datos = self.prob_dist.tabla_distribucion_probabilidades(
            matrices, estado_actual, estado_futuro, valor_actual, estados)
        lista = []
        lista.append(str(datos[0][0]))

        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))

        df = pd.DataFrame(datos[1:], columns=lista)
        return df
