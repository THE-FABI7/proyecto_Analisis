import time
import numpy as np
from Data.datapb.NodeDataRetrieve import NodeDataRetriever
from scipy.stats import wasserstein_distance
import pandas as pd
import streamlit_agraph as stag
from Probabilidades.visualizer import Gui

class Estrategia:
    def __init__(self):
        pass
    
    def datos_mt(self):
        matrices = NodeDataRetriever()
        return matrices.get_six_node_data()

    def retornar_particion_adecuada(self, conjunto1, conjunto2, estadoActual):
        matrices = self.datos_mt()
        resultado, estados = self.genera_estados_transicion(matrices)
        distribucion_particiones_original = self.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estadoActual, estados)
        particion, diferencia, lista = self.planteamiento_voraz(matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estadoActual)
        return particion, diferencia, lista

    def genera_estados_transicion(self, subconjuntos):
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)
        return transiciones, estados
    
    def producto_tensor(self, p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)
        return np.outer(p1, p2).flatten()
    
    def calcular_emd(self, p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)

        if p1.ndim != 1 or p2.ndim != 1:
            raise ValueError("p1 y p2 deben ser arrays unidimensionales")

        if len(p1) != len(p2):
            p2 = np.interp(np.linspace(0, 1, len(p1)), np.linspace(0, 1, len(p2)), p2)
        
        cost_matrix = np.abs(np.subtract.outer(p1, p2))
        salida = np.sum(np.min(cost_matrix, axis=1) * p1)
        return salida

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
                distribucion_izq = self.tabla_distribucion_probabilidades(matrices, c1_izq, c2_izq, estadoActual, estados)
                distribucion_der = self.tabla_distribucion_probabilidades(matrices, c1_der, c2_der, estadoActual, estados)
                p1 = distribucion_izq[1][1:]
                p2 = distribucion_der[1][1:]
                prodTensor = self.producto_tensor(p1, p2)
                diferencia = self.calcular_emd(distribucion_particiones_original[1][1:], prodTensor)
                fin = time.time()

                print("--------------------")
                print("diferencia", diferencia)
                print("mejor_particion", mejor_particion)
                print("--------------------")

                if c2_der == [] and c1_der == []:
                    continue
                    
                elif diferencia < menor_diferencia:
                    menor_diferencia = diferencia
                    mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]
                
                aux = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia)]
                particiones_evaluadas.append(aux)
                
        return mejor_particion, menor_diferencia, particiones_evaluadas
    
    def busqueda_divide_y_venceras(self, matrices, estados, distribucion_particiones_original, conjunto1, conjunto2, estadoActual):
        if len(conjunto1) == 0 or len(conjunto2) == 0:
            return [], float('inf'), []

        if len(conjunto1) == 1 and len(conjunto2) == 1:
            distribucion = self.tabla_distribucion_probabilidades(matrices, conjunto1, conjunto2, estadoActual, estados)
            p1 = distribucion[1][1:]
            prodTensor = self.producto_tensor(p1, p1)
            diferencia = self.calcular_emd(distribucion_particiones_original[1][1:], prodTensor)
            return [(tuple(conjunto2), tuple(conjunto1))], diferencia, [(tuple(conjunto2), tuple(conjunto1), str(diferencia))]

        mid1 = len(conjunto1) // 2
        mid2 = len(conjunto2) // 2

        c1_izq = conjunto1[:mid1]
        c1_der = conjunto1[mid1:]
        c2_izq = conjunto2[:mid2]
        c2_der = conjunto2[mid2:]

        mejor_particion_izq, menor_diferencia_izq, lista_izq = self.busqueda_divide_y_venceras(matrices, estados, distribucion_particiones_original, c1_izq, c2_izq, estadoActual)
        mejor_particion_der, menor_diferencia_der, lista_der = self.busqueda_divide_y_venceras(matrices, estados, distribucion_particiones_original, c1_der, c2_der, estadoActual)

        if menor_diferencia_izq < menor_diferencia_der:
            mejor_particion = mejor_particion_izq
            menor_diferencia = menor_diferencia_izq
            lista_particiones = lista_izq
        else:
            mejor_particion = mejor_particion_der
            menor_diferencia = menor_diferencia_der
            lista_particiones = lista_der

        inicio = time.time()
        distribucion_izq_der = self.tabla_distribucion_probabilidades(matrices, c1_izq, c2_der, estadoActual, estados)
        distribucion_der_izq = self.tabla_distribucion_probabilidades(matrices, c1_der, c2_izq, estadoActual, estados)
        p1 = distribucion_izq_der[1][1:]
        p2 = distribucion_der_izq[1][1:]
        prodTensor = self.producto_tensor(p1, p2)
        diferencia_cruzada = self.calcular_emd(distribucion_particiones_original[1][1:], prodTensor)
        fin = time.time()

        if diferencia_cruzada < menor_diferencia:
            menor_diferencia = diferencia_cruzada
            mejor_particion = [(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der))]
            lista_particiones.append([(tuple(c2_izq), tuple(c1_izq)), (tuple(c2_der), tuple(c1_der)), str(diferencia_cruzada), str(fin - inicio)])

        return mejor_particion, menor_diferencia, lista_particiones

    def tabla_distribucion_probabilidades(self, tabla, estadoActual, estadoFuturo, num, estados):
        indice = [estados.index(i) for i in estadoActual]
        prob_distribuidas = []
        for i in estadoFuturo:
            if "'" in i:
                i = i[:-1]
            nuevaTabla = self.crear_tabla_comparativa(tabla[i])
            filtro2 = self.porcentajes_distribuciones(nuevaTabla, indice, num)
            prob_distribuidas.append(filtro2)
        tabla = self.crear_tabla(prob_distribuidas, num)
        tabla[0] = [[estadoFuturo, estadoActual]] + tabla[0]
        tabla[1] = [num] + tabla[1]
        return tabla

    def crear_tabla_comparativa(self, diccionario):
        lista = [['key', (1,), (0,)]]
        for k, v in diccionario.items():
            lista.append([k, v, 1 - v])
        return lista
    
    def porcentajes_distribuciones(self, tabla, indice, num):
        tablaNueva = [tabla[0]]
        fila = None
        try:
            tabla1 = [fila for fila in tabla[1:] if all(i < len(num) and pos < len(fila[0]) and fila[0][pos] == num[i] for i, pos in enumerate(indice))]
        except IndexError as e:
            print(f"IndexError: {e}")
            raise

        nuevosValores = [0, 0]
        for i in tabla1:
            nuevosValores[0] += i[1]
            nuevosValores[1] += i[2]

        total = sum(nuevosValores)
        nuevosValores = [v / total if total != 0 else v for v in nuevosValores]
        nuevaFila = [num, *nuevosValores]
        tablaNueva.append(nuevaFila)
        return tablaNueva
    
    def crear_tabla(self, distribucion, num, i=0, numBinario ='', nuevoValor=1):
        if i == len(distribucion):
            numBinario = '0' * (len(distribucion)-len(numBinario)) + numBinario
            nuevoDato = tuple(int(bit) for bit in numBinario)
            return [[nuevoDato], [nuevoValor]]
        else:
            tabla = self.crear_tabla(distribucion, num, i+1, numBinario+'0', nuevoValor*distribucion[i][1][2])
            tabla2 = self.crear_tabla(distribucion, num, i+1, numBinario+'1', nuevoValor*distribucion[i][1][1])
            return [tabla[0]+tabla2[0], tabla[1]+tabla2[1]]

    def retornarValorActual(self, conjunto1, conjunto2):
        lista = []
        matrices = self.datos_mt()
        
        for j in matrices['A']:
            lista.append(j)
        
        return lista
    
    def crear_particiones(self, conjunto1, conjunto2, estadoActual):
        matrices = self.datos_mt()
        particiones = []
        a, b, lista = self.retornar_particion_adecuada(conjunto1, conjunto2, estadoActual)
        df = pd.DataFrame(lista, columns=['Conjunto 1', 'Conjunto 2','Diferencia'])
        return df, particiones
    
    def retornar_distribuciones(self, eActual, eFuturo, valorActual, st):
        matrices = self.datos_mt()
        resultado, estados = self.genera_estados_transicion(matrices)
        datos = self.tabla_distribucion_probabilidades(matrices, eActual, eFuturo, valorActual, estados)
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
