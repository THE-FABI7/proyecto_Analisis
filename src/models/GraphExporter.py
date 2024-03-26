import json
from turtle import pd

from matplotlib import pyplot as plt
import networkx as nx


class GraphExporter:
    @staticmethod
    def export_to_excel(graph_manager, file_path):
        nodes = pd.DataFrame(graph_manager.get_nodes(), columns=['ID', 'Attributes'])
        edges = pd.DataFrame(graph_manager.get_edges(), columns=['Source', 'Target', 'Attributes'])
        with pd.ExcelWriter(file_path) as writer:
            nodes.to_excel(writer, sheet_name='Nodos')
            edges.to_excel(writer, sheet_name='Aristas')
        # Implementar lógica de exportación a Excel basada en graph_manager.nodes y graph_manager.edges

    @staticmethod
    def export_to_image(graph_manager, file_path):
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(graph_manager.graph)
        nx.draw(graph_manager.graph, pos, with_labels=True, node_color='skyblue', edge_color='k')
        plt.savefig(file_path)
        plt.close()
        # Implementar lógica de exportación a imagen utilizando graph_manager.graph
        pass

    @staticmethod
    def export_to_json(graph_manager, file_path):
        data = {
            "nodes": list(graph_manager.get_nodes()),
            "edges": list(graph_manager.get_edges())
        }
        with open(file_path, 'w') as f:
            json.dump(data, f)