# GraphManager.py
import random
import networkx as nx

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node_id, label, color='skyblue'):
        self.graph.add_node(node_id, label=label, color=color)

    def add_edge(self, source, target, weight=1, color='black'):
        self.graph.add_edge(source, target, weight=weight, color=color)

    def remove_node(self, node_id):
        self.graph.remove_node(node_id)

    def remove_edge(self, source, target):
        self.graph.remove_edge(source, target)

    def generate_random_graph(self, num_nodes, num_edges):
        self.graph.clear()
        for i in range(num_nodes):
            self.add_node(i, f'Node {i}')
        while self.graph.number_of_edges() < num_edges:
            u = random.randint(0, num_nodes - 1)
            v = random.randint(0, num_nodes - 1)
            if u != v and not self.graph.has_edge(u, v):
                self.add_edge(u, v)

    def get_graph(self):
        return self.graph
