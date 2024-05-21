from itertools import combinations
import re
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

from Probabilidades.ProbabilityDistribution import ProbabilityDistribution

class PartitionGenerator:
    """
    Clase encargada de generar particiones y combinaciones de conjuntos de nodos.
    """

    def generar_particiones(self, conjunto1, conjunto2):
        particiones = []
        for i in range(len(conjunto1) + 1):
            combos1 = combinations(conjunto1, i)
            for c1 in combos1:
                particion1 = [list(c1), sorted(list(set(conjunto1) - set(c1)) + list(conjunto2))]
                particiones.append(particion1)
        for i in range(len(conjunto2) + 1):
            combos2 = combinations(conjunto2, i)
            for c2 in combos2:
                particion2 = [list(c2), sorted(list(set(conjunto2) - set(c2)) + list(conjunto1))]
                particiones.append(particion2)
        n = len(conjunto1)
        for i, particion in enumerate(particiones):
            particiones[i].append(tuple(j % 2 for j in range(n)))

        # Convertir las listas internas a tuplas para hacerlas hasheables
        particiones = [tuple(tuple(x) for x in p) for p in particiones if p[0] and p[1]]
        df = pd.DataFrame(particiones, columns=['Conjunto 1', 'Conjunto 2', 'Estado'])
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
        conjunto1 = [comb for i in range(len(c1) + 1) for comb in combinations(range(len(c1)), i)]
        conjunto2 = [comb for i in range(len(c2) + 1) for comb in combinations(range(len(c2)), i)]
        todas_las_combinaciones = [(cc1, cc2) for cc1 in conjunto1 for cc2 in conjunto2]
        lista_combinaciones = []
        for comb in todas_las_combinaciones:
            parte_contador = (tuple(set(range(len(c1))) - set(comb[0])), tuple(set(range(len(c2))) - set(comb[1])))
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
        p1 = tuple(lista_distribuida[1][0][i] for i in e_actual1 if i < len(lista_distribuida[1][0]))
        p2 = tuple(lista_distribuida[1][0][i] for i in e_actual2 if i < len(lista_distribuida[1][0]))
        lista_nueva1 = []
        lista_nueva2 = []
        i1 = {}
        i2 = {}
        for num, fila in enumerate(lista_distribuida[0][1:], start=1):
            aux_nueva_tabla1 = tuple(fila[i - 1] for i in e_futuro1)
            aux_nueva_tabla2 = tuple(fila[i - 1] for i in e_futuro2)
            PartitionGenerator.actualizar_tabla(i1, aux_nueva_tabla1, lista_nueva1, num)
            PartitionGenerator.actualizar_tabla(i2, aux_nueva_tabla2, lista_nueva2, num)

        lista_aux1 = [p1] + PartitionGenerator.calcular_promedio(i1, lista_distribuida)
        lista_aux2 = [p2] + PartitionGenerator.calcular_promedio(i2, lista_distribuida)
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
            lista = PartitionGenerator.particiones(distribuciones, i[0][0], i[1][0], i[0][1], i[1][1])
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
                estado_futuro = tuple(subconjuntos[estado][estado_actual_tuple] for estado in estados)
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
        resultado, estados = PartitionGenerator.generar_estado_transicion(datos)
        # agregarle a cada valor de los estados una '
        for i in range(len(estados)):
            estados[i] = estados[i] + "'"
        return estados

    @staticmethod
    def retornar_estados():
        datos = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(datos)
        return estados

    @staticmethod
    def retornar_valor_actual(c1):
        datos = ProbabilityDistribution.datos_mt()
        lista = []
        if len(c1) == 1:
            lista.append((0,))
            lista.append((1,))
        elif len(c1) == 2:
            lista.append((0, 0))
            lista.append((0, 1))
            lista.append((1, 0))
            lista.append((1, 1))
        else:
            for k, v in datos.items():
                for k2, v2 in v.items():
                    lista.append(k2)
                break
        return lista

    @staticmethod
    def retornar_distribucion(e_actual, e_futuro, valor_actual, st):
        matrices = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(matrices)
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
    def retornar_mejor_particion(c1, c2, estado_actual, nodes, edges, st):
        matrices = ProbabilityDistribution.datos_mt()
        resultado, estados = PartitionGenerator.generar_estado_transicion(matrices)

        distribucion_probabilidad = ProbabilityDistribution.generar_distribucion_probabilidades(
            matrices, c1, c2, estado_actual, estados)  # Original

        combinaciones = PartitionGenerator.generar_combinaciones(c1, c2)
        particiones_df, particiones_lista = PartitionGenerator.generar_particiones(c1, c2)

        def convertir_a_numerico(item):
            if item == 'A':
                return 1
            elif item == 'B':
                return 2
            elif item == 'C':
                return 3
            else:
                return float(item)  # Convertir a float si ya es un número

        menor = float('inf')
        particion = []
        particiones_menores = {}
        part = {}

        for particion in particiones_lista:
            particion1 = [convertir_a_numerico(item) for item in particion[0]]  # Convertir directamente los elementos
            particion2 = [convertir_a_numerico(item) for item in particion[1]]  # Convertir directamente los elementos
            prod_tensor = ProbabilityDistribution.producto_tensor(particion1, particion2)
            diferencia = min(ProbabilityDistribution.calcular_emd(
                distribucion_probabilidad[1][1:], prod_tensor))
            part[particion] = diferencia

        for particion in part:
            if part[particion] < menor:
                menor = part[particion]

        for particion in part:
            if part[particion] == menor:
                particiones_menores[particion] = part[particion]
        lista_particiones = []
        for particion, probabilidad in particiones_menores.items():
            particion1 = [list(map(convertir_a_numerico, p)) for p in particion[0]]
            particion2 = [list(map(convertir_a_numerico, p)) for p in particion[1]]
            lista_particiones.append([particion1, particion2, probabilidad])

        for i in range(len(lista_particiones)):
            if [] in lista_particiones[i][0]:
                lista_particiones[i][0].remove([])
                lista_particiones[i][0][0].append("")
                if len(lista_particiones[i][0]) > 1:
                    a = lista_particiones[i][0][1]
                    print(a)

            print(lista_particiones[i][0])
            a = lista_particiones[i][0][0]
            for arista in edges:
                if arista.source in lista_particiones[i][0][0]:
                    arista.dashes = True
                    arista.color = 'rgba(254, 20, 56, 0.5)'

        return particion, menor, nodes, edges



