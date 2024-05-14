import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

# Asumiendo que este módulo y método existen
from models.GraphManager import GraphManager


class StateGraph:
    def __init__(self, datos_json):
        self.grafo = nx.DiGraph()
        # Si GraphManager tiene métodos estáticos, se puede omitir la instanciación
        self.graph_manager = GraphManager()
        self.datos_json = datos_json
        # La matriz combinada de transición para A, B, y C con dimensiones 8x8
        self.transition_matrix_A = np.array([
            [1, 0],
            [1, 0],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [0, 1]
        ])
        self.transition_matrix_B = np.array([
            [1, 0],
            [1, 0],
            [1, 0],
            [1, 0],
            [1, 0],
            [0, 1],
            [1, 0],
            [0, 1]
        ])
        self.transition_matrix_C = np.array([
            [1, 0],
            [0, 1],
            [0, 1],
            [1, 0],
            [1, 0],
            [0, 1],
            [0, 1],
            [1, 0]
        ])

    def cargar_datos(self):
        with open(self.datos_json, 'r') as file:
            data = json.load(file)

        nodes = data['graph'][0]['data']
        for node in nodes:
            self.grafo.add_node(node['id'], label=node['label'])
            for link in node['linkedTo']:
                self.grafo.add_edge(
                    node['id'], link['nodeId'], weight=link['weight'])

    def plot_graph(self):
        # Generar una posición para todos los nodos
        pos = nx.spring_layout(self.grafo)
        nx.draw(self.grafo, pos, with_labels=True, node_color='lightblue')
        labels = nx.get_edge_attributes(self.grafo, 'weight')
        nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=labels)
        plt.show()

    def simular_transiciones(self, estado_actual):
        index = estado_actual[2] * 4 + estado_actual[1] * 2 + estado_actual[0]
        prob_a = self.transition_matrix_A[index]
        prob_b = self.transition_matrix_B[index]
        prob_c = self.transition_matrix_C[index]
        estado_futuro_a = 1 if prob_a[1] == 1 else 0
        estado_futuro_b = 1 if prob_b[1] == 1 else 0
        estado_futuro_c = 1 if prob_c[1] == 1 else 0
        return {
            'estado_actual': estado_actual,
            'estados_futuros': {
                'A': estado_futuro_a,
                'B': estado_futuro_b,
                'C': estado_futuro_c
            },
            'probabilidades': {
                'A': prob_a,
                'B': prob_b,
                'C': prob_c
            }
        }

    def obtener_estado_futuro_probabilidad(self, estado_actual):
        resultado = self.simular_transiciones(estado_actual)
    # Asegúrate de que la creación del DataFrame corresponde a los nombres de columna correctos
        df = pd.DataFrame({
            # Asegura que esto sea un iterable con un solo elemento
            'Estado Actual': [estado_actual],
            'Estado Futuro A': [resultado['estados_futuros']['A']],
            'Estado Futuro B': [resultado['estados_futuros']['B']],
            'Estado Futuro C': [resultado['estados_futuros']['C']],
            # Convertir array a string # Asumiendo que quieres el segundo elemento de la lista
            'Probabilidad A': [str(resultado['probabilidades']['A'])],
            'Probabilidad B': [str(resultado['probabilidades']['B'])],
            'Probabilidad C': [str(resultado['probabilidades']['C'])]
        })
        return df