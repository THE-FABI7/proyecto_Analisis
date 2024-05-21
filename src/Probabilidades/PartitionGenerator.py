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
                particion1 = [list(c1), sorted(
                    list(set(tuple(conjunto1)) - set(tuple(c1))) + list(set(tuple(conjunto2))))]
                particiones.append(particion1)
        for i in range(len(conjunto2) + 1):
            combos2 = combinations(conjunto2, i)
            for c2 in combos2:
                particion2 = [list(c2), sorted(
                    list(set(tuple(conjunto2)) - set(tuple(c2))) + list(set(tuple(conjunto1))))]
                particiones.append(particion2)
        n = len(conjunto1)
        for i, particion in enumerate(particiones):
            particiones[i].append(tuple(j % 2 for j in range(n)))
        particiones = [tuple(p) for p in particiones if p[0] and p[1]]
        df = pd.DataFrame(particiones, columns=[
            'Conjunto 1', 'Conjunto 2', 'Estado'])
        return df, particiones

    def generar_combinaciones(self, c1, c2):
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

    def actualizar_tabla(self, indices, aux_nueva_lista, lista_nueva, num):
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

    def calcular_promedio(self, indices, lista_distribuida):
        """
        Calcula el promedio de una lista distribuida.

        Args:
            indices (dict): Diccionario de índices.
            lista_distribuida (list): Lista distribuida.

        Returns:
            list: Lista de promedios.
        """
        return [sum(lista_distribuida[1][j] for j in indices[i]) / len(indices[i]) if indices[i] else 0 for i in indices]

    def particiones(self, lista_distribuida, e_actual1, e_actual2, e_futuro1, e_futuro2):
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
            self.actualizar_tabla(i1, aux_nueva_tabla1, lista_nueva1, num)
            self.actualizar_tabla(i2, aux_nueva_tabla2, lista_nueva2, num)

        lista_aux1 = [p1] + self.calcular_promedio(i1, lista_distribuida)
        lista_aux2 = [p2] + self.calcular_promedio(i2, lista_distribuida)
        lista_salida1 = [['Key'] + lista_nueva1, lista_aux1]
        lista_salida2 = [['Key'] + lista_nueva2, lista_aux2]
        return lista_salida1, lista_salida2

    def generar_prob_particiones(self, distribuciones, combinaciones):
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
            lista = self.particiones(
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

    def generarEstadoTransicion(self, subconjuntos):
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

    def retornar_Futuros(self):
        datos = ProbabilityDistribution.datos_mt(self)
        resultado, estados = PartitionGenerator.generarEstadoTransicion(
            self, datos)
        # agregarle a cada valor de los estados una '
        for i in range(len(estados)):
            estados[i] = estados[i] + "'"

        return estados

    def retornar_Estados(self):
        datos = ProbabilityDistribution.datos_mt(self)
        resultado, estados = PartitionGenerator.generarEstadoTransicion(
            self, datos)
        return estados

    def retornarValorActual(self, c1):
        datos = ProbabilityDistribution.datos_mt(self)
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

    def retornarDistribucion(self, eActual, eFuturo, valorActual, st):
        matrices = ProbabilityDistribution.datos_mt(self)
        resultado, estados = PartitionGenerator.generarEstadoTransicion(
            self, matrices)
        datos = ProbabilityDistribution.generar_distribucion_probabilidades(self,
                                                                            matrices, eActual, eFuturo, valorActual, estados)
        lista = []
        lista.append(str(datos[0][0]))

        # lista.append(datos[0])
        for i in range(len(datos[0][1:])):
            lista.append(str(datos[0][1:][i]))

        df = pd.DataFrame(datos[1:], columns=lista)
        return df

    def retornarMejorParticion(self, c1, c2, estadoActual, nodes, edges, st):
        # df, particiones = self.generarParticiones(c1, c2)
        matrices = ProbabilityDistribution.datos_mt(self)
        resultado, estados = PartitionGenerator.generarEstadoTransicion(
            self, matrices)

        distribucionProbabilidad = ProbabilityDistribution.generar_distribucion_probabilidades(self,
                                                                                               matrices, c1, c2, estadoActual, estados)  # Original
        # Combinaciones de particiones posibles de la original
        combinaciones = PartitionGenerator.generar_combinaciones(self, c1, c2)
        particioness = PartitionGenerator.generar_particiones(self,
                                                              distribucionProbabilidad, combinaciones)

        menor = float('inf')
        particion = []
        particionesMenores = {}
        part = {}
        for i in particioness:

            particion1 = particioness[i][0][1][1:]
            particion2 = particioness[i][1][1][1:]
            prodTensor = self.producto_tensor(particion1, particion2)
            diferencia = min(self.calcularEMD(
                distribucionProbabilidad[1][1:], prodTensor))
            part[i] = diferencia

        for i in part:
            if part[i] < menor:
                menor = part[i]

        for i in part:
            if part[i] == menor:
                particionesMenores[i] = part[i]
        lista_particiones = []
        for particion, probabilidad in particionesMenores.items():
            partes = particion.split('-')
            particion1 = re.findall(r'\((.*?)\)', partes[0].strip())
            particion2 = re.findall(r'\((.*?)\)', partes[1].strip())
            particion1 = [list(p.split()) if p else [""] for p in particion1]
            particion2 = [list(p.split()) if p else [""] for p in particion2]
            lista_particiones.append([particion1, particion2, probabilidad])

        for i in range(len(lista_particiones)):
            # lista_particiones[i][0] = [sublist for sublist in lista_particiones[i][0] if sublist]
            # lista_particiones[i][1] = [sublist for sublist in lista_particiones[i][1] if sublist]

            if [] in lista_particiones[i][0]:
                lista_particiones[i][0].remove([])
                lista_particiones[i][0][0].append("")
                if len(lista_particiones[i][0]) > 1:
                    a = lista_particiones[i][0][1]
                    print(a)

            print(lista_particiones[i][0])
            a = lista_particiones[i][0][0]
            # print(a)
            # eliminar aristas de la particion
            for arista in edges:
                if arista.source in lista_particiones[i][0][0]:
                    arista.dashes = True
                    arista.color = 'rgba(254, 20, 56, 0.5)'

        # TODO: todavia hay errores
        # agraph(nodes=st.session_state.nodes,
               # edges=st.session_state.edges, config=)

        return particion, diferencia, nodes, edges
