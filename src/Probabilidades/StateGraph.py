import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json

from models.GraphManager import GraphManager  # Asumiendo que este módulo y método existen

class StateGraph:
    def __init__(self, datos_json):
        self.grafo = nx.DiGraph()
        self.graph_manager = GraphManager()  # Si GraphManager tiene métodos estáticos, se puede omitir la instanciación
        self.datos_json = datos_json
        # La matriz combinada de transición para A, B, y C con dimensiones 8x8
        self.transition_matrix = np.array([
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0]
        ])


    def cargar_datos(self):
        with open(self.datos_json, 'r') as file:
            data = json.load(file)

        nodes = data['graph'][0]['data']
        for node in nodes:
            self.grafo.add_node(node['id'], label=node['label'])
            for link in node['linkedTo']:
                self.grafo.add_edge(node['id'], link['nodeId'], weight=link['weight'])

    def plot_graph(self):
        pos = nx.spring_layout(self.grafo)  # Generar una posición para todos los nodos
        nx.draw(self.grafo, pos, with_labels=True, node_color='lightblue')
        labels = nx.get_edge_attributes(self.grafo, 'weight')
        nx.draw_networkx_edge_labels(self.grafo, pos, edge_labels=labels)
        plt.show()

    def simular_transiciones(self, estados_actuales):
        index = estados_actuales[0] * 4 + estados_actuales[1] * 2 + estados_actuales[2]
        probabilidades = self.transition_matrix[index]
        return probabilidades