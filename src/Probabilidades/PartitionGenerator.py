from itertools import combinations
import re
import time
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

from Probabilidades.ProbabilityDistribution import ProbabilityDistribution


class PartitionGenerator:
    """
    Clase encargada de generar particiones y combinaciones de conjuntos de nodos.
    """

    @staticmethod
    def generar_particiones(conjunto1, conjunto2, estadoActual):
        """
        Genera todas las posibles particiones de dos conjuntos.

        Args:
            conjunto1 (list): Primer conjunto.
            conjunto2 (list): Segundo conjunto.

        Returns:
            tuple: DataFrame y lista de particiones.
        """
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
            c1 (list): Primer conjunto.
            c2 (list): Segundo conjunto.

        Returns:
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
        p1 = tuple(lista_distribuida[1][0][i]
                   for i in e_actual1 if i < len(lista_distribuida[1][0]))
        p2 = tuple(lista_distribuida[1][0][i]
                   for i in e_actual2 if i < len(lista_distribuida[1][0]))
        lista_nueva1 = []
        lista_nueva2 = []
        i1 = {}
        i2 = {}
        for num, fila in enumerate(lista_distribuida[0][1:], start=1):
            aux_nueva_tabla1 = tuple(fila[i - 1] for i in e_futuro1)
            aux_nueva_tabla2 = tuple(fila[i - 1] for i in e_futuro2)
            PartitionGenerator.actualizar_tabla(
                i1, aux_nueva_tabla1, lista_nueva1, num)
            PartitionGenerator.actualizar_tabla(
                i2, aux_nueva_tabla2, lista_nueva2, num)

        lista_aux1 = [p1] + \
            PartitionGenerator.calcular_promedio(i1, lista_distribuida)
        lista_aux2 = [p2] + \
            PartitionGenerator.calcular_promedio(i2, lista_distribuida)
        lista_salida1 = [['Key'] + lista_nueva1, lista_aux1]
        lista_salida2 = [['Key'] + lista_nueva2, lista_aux2]
        return lista_salida1, lista_salida2

    @staticmethod
    def generar_prob_particiones(distribuciones, combinaciones):
        """
        Genera las probabilidades de particiones basadas en distribuciones y combinaciones.

        Args:
            distribuciones (list): Lista de distribuciones.
            combinaciones (list): Lista de combinaciones.

        Returns:
            dict: Diccionario de probabilidades de particiones.
        """
        tabla_de_particiones = {}
        cadena = distribuciones[0][0]
        lista1, lista2 = [eval(subcadena) for subcadena in cadena.split('|')]
        for i in combinaciones[1:]:
            lista = PartitionGenerator.particiones(
                distribuciones, i[0][0], i[1][0], i[0][1], i[1][1])
            nombre = "("
            for j in i[0][0]:
                if j < len(lista1):
                    nombre += f" {lista1[j]}"
            nombre += " ) ("
            for j in i[0][1]:
                if j < len(lista2):
                    nombre += f" {lista2[j]}"
            nombre += " ) - ("
            for j in i[1][0]:
                if j < len(lista1):
                    nombre += f" {lista1[j]}"
            nombre += " ) ("
            for j in i[1][1]:
                if j < len(lista2):
                    nombre += f" {lista2[j]}"
            nombre += " )"
            tabla_de_particiones[nombre] = lista
        return tabla_de_particiones

    @staticmethod
    def generar_estado_transicion(subconjuntos):
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def aux(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(
                    subconjuntos[estado][estado_actual_tuple] for estado in estados)
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                aux(i + 1)
                estado_actual[i] = 1
                aux(i + 1)

        aux(0)
        return transiciones, estados

    @staticmethod
    def retornar_futuros():
        datos = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(
            datos)
        # agregarle a cada valor de los estados una '
        for i in range(len(estados)):
            estados[i] = estados[i] + "'"
        return estados

    @staticmethod
    def retornar_estados():
        datos = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(
            datos)
        return estados

    @staticmethod
    def retornar_valor_actual(self, c1, c2):
        lista = []
        matrices = ProbabilityDistribution.datos_mt()

        # Generar todos los números binarios posibles según la longitud de c1
        # longitud = len(c1)
        # combinaciones_binarias = list(product([0, 1], repeat=longitud))

        # lista.extend(combinaciones_binarias)

        for j in matrices['1']:
            lista.append(j)

        return lista

    @staticmethod
    def retornar_distribucion(e_actual, e_futuro, valor_actual, st):
        matrices = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(
            matrices)
        datos = ProbabilityDistribution.generar_distribucion_probabilidades(
            matrices, e_actual, e_futuro, valor_actual, estados)
        lista = []
        lista.append(str(datos[0][0]))

        # lista.append(datos[0])
        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))

        df = pd.DataFrame(datos[1:], columns=lista)
        return df

    @staticmethod
    def retornar_mejor_particion(c1, c2, estado_actual):
        matrices = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(
            matrices)

        distribucion_probabilidad = ProbabilityDistribution.generar_distribucion_probabilidades(
            matrices, c1, c2, estado_actual, estados)  # Original

        lista = []

        particion, diferencia, tiempo, lista = PartitionGenerator.busqueda_voraz(
            matrices, estados, distribucion_probabilidad, c1, c2, estado_actual)
        return particion, diferencia, tiempo, lista

    def busqueda_voraz( matrices, estados, distribucionProbabilidadOriginal, c1, c2, estadoActual):
        mejor_particion = []
        menor_diferencia = float('inf')
        listaParticionesEvaluadas = []
        for i in range(len(c1)):
            c1_izq = c1[:i]
            c1_der = c1[i:]
            c2_izq = []
            c2_der = list(c2)

            for j in range(len(c2)):
                c2_izq.append(c2_der.pop(0))

                inicio = time.time()
                distribucion_izq = ProbabilityDistribution.generar_distribucion_probabilidades(
                    matrices, c1_izq, c2_izq, estadoActual, estados)
                distribucion_der = ProbabilityDistribution.generar_distribucion_probabilidades(
                    matrices, c1_der, c2_der, estadoActual, estados)
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
                    mejor_particion = [
                        (tuple(c2_izq), (tuple(c1_izq))), (tuple(c2_der), tuple(c1_der))]
                aux = [(tuple(c2_izq), (tuple(c1_izq))), (tuple(c2_der),
                                                          tuple(c1_der)), str(diferencia), str(tiempoEjecucion)]
                listaParticionesEvaluadas.append(aux)
        return mejor_particion, menor_diferencia, tiempoEjecucion, listaParticionesEvaluadas
    
    
    def convertir_a_listas(self, datos):
        lineas = datos.split('\n')
        listas = []
        for linea in lineas:
            grupos = linea.split(' - ')
            grupos_listas = []
            for grupo in grupos:
                subgrupos = grupo.split(') (')
                subgrupos = [subgrupo.replace("(", "").replace(")", "").strip() for subgrupo in subgrupos]
                subgrupos_listas = [subgrupo.split() if subgrupo else [] for subgrupo in subgrupos]
                grupos_listas.append(subgrupos_listas)
            listas.append(grupos_listas)
        return listas
