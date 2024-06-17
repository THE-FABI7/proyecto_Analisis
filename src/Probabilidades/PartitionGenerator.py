from itertools import combinations
import pandas as pd
import numpy as np
from scipy.stats import wasserstein_distance
from Probabilidades.Utilities import Utilities

class PartitionGenerator:
    """
    Clase encargada de generar particiones y combinaciones de conjuntos de nodos.
    """

    def __init__(self, prob_dist, estadoActual):
        """
        Inicializa la clase con una distribución de probabilidades.

        Args:
            prob_dist (ProbabilityDistribution): Objeto de la clase ProbabilityDistribution.
        """
        self.prob_dist = prob_dist

    
    def crear_estados_transicion(self, subconjuntos):
        """
        Genera los estados de transición para un conjunto de nodos.
        matrices = ProbabilityDistribution.datos_mt()
        particiones = []
        a, b, c, lista = PartitionGenerator.retornar_mejor_particion(
            conjunto1, conjunto2, estadoActual)

        df = pd.DataFrame(lista, columns=[
                          'Conjunto 1', 'Conjunto 2', 'Diferencia', 'Tiempo de ejecución'])
        return df, particiones

    @staticmethod
    def generar_combinaciones(c1, c2):
        """
        Genera todas las posibles combinaciones de dos conjuntos.

        Args:
            subconjuntos (dict): Diccionario de subconjuntos.

        Returns:
            tuple: Diccionario de transiciones y lista de estados.
            list: Lista de combinaciones.
        """
        conjunto1 = [comb for i in range(len(c1) + 1)
                     for comb in combinations(range(len(c1)), i)]
        conjunto2 = [comb for i in range(len(c2) + 1)
                     for comb in combinations(range(len(c2)), i)]
        todas_las_combinaciones = [(cc1, cc2)
                                   for cc1 in conjunto1 for cc2 in conjunto2]
        lista_combinaciones = []
        for comb in todas_las_combinaciones:
            parte_contador = (tuple(
                set(range(len(c1))) - set(comb[0])), tuple(set(range(len(c2))) - set(comb[1])))
            if (parte_contador, comb) not in lista_combinaciones and (comb, parte_contador) not in lista_combinaciones:
                lista_combinaciones.append([comb, parte_contador])
        return lista_combinaciones

    @staticmethod
    def actualizar_tabla(indices, aux_nueva_lista, lista_nueva, num):
        """
        Actualiza una tabla con nuevos valores.

        Args:
            indices (dict): Diccionario de índices.
            aux_nueva_lista (tuple): Tupla de nuevos valores.
            lista_nueva (list): Lista de nuevos valores.
            num (int): Número de la fila.
        """
        if aux_nueva_lista not in indices:
            indices[aux_nueva_lista] = [num]
            lista_nueva.append(aux_nueva_lista)
        else:
            indices[aux_nueva_lista].append(num)

    @staticmethod
    def calcular_promedio(indices, lista_distribuida):
        """
        Calcula el promedio de una lista distribuida.

        Args:
            indices (dict): Diccionario de índices.
            lista_distribuida (list): Lista distribuida.

        Returns:
            list: Lista de promedios.
        """
        return [sum(lista_distribuida[1][j] for j in indices[i]) / len(indices[i]) if indices[i] else 0 for i in indices]

    @staticmethod
    def particiones(lista_distribuida, e_actual1, e_actual2, e_futuro1, e_futuro2):
        """
        Genera particiones de una lista distribuida basada en estados actuales y futuros.

        Args:
            lista_distribuida (list): Lista de distribuciones.
            e_actual1 (list): Estado actual 1.
            e_actual2 (list): Estado actual 2.
            e_futuro1 (list): Estado futuro 1.
            e_futuro2 (list): Estado futuro 2.

        Returns:
            tuple: Listas de salida de particiones.
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
        matrices = ProbabilityDistribution.datos_mt()

        # Generar todos los números binarios posibles según la longitud de c1
        # longitud = len(c1)
        # combinaciones_binarias = list(product([0, 1], repeat=longitud))

        # lista.extend(combinaciones_binarias)

        for j in matrices['1']:
            lista.append(j)

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
