from models.GraphManager import GraphManager


class Marginalizar:
    def __init__(self):
        self.particiones = []
        self.graph_manager = GraphManager()  # Create a single instance for reuse

    def load_data(self):
        """Loads graph data from a JSON file."""
        return self.graph_manager.cargarArchivo("Data/complete_biparite_grsph.json")

    def get_bipartite_sets(self, nodes, edges):
        """Obtains two disjoint sets from a bipartite graph."""
        return self.graph_manager.obtenerConjuntosGrafoBipartito(nodes, edges)

    def marginalize(self, nodes, edges, current_state, marginalize_flag):
        """Performs marginalization on the graph states based on the given flag."""
        matrices = self.datosMatrices()
        if len(current_state) == 1:
            return self.marginalize_single_state(matrices, current_state, marginalize_flag)

    def marginalize_single_state(self, matrices, current_state, marginalize_flag):
        """Helper method to marginalize a single state."""
        probability = {}
        keys_list = list(matrices.keys())

        def probability_calculator(matrix, states):
            """Calculates probability sums from matrix states."""
            total = [0, 0]
            for key, values in matrix.items():
                if all(key[i] == states[i] for i in range(len(states))):
                    total[0] += values[0] / 2
                    total[1] += values[1] / 2
            return total

        for index, key in enumerate(keys_list):
            matrix = matrices[keys_list[(index + 1) % len(keys_list)]]
            for key_pair in matrix:
                state1, state2 = key_pair[1], key_pair[2]
                probability[state1 +
                            state2] = probability_calculator(matrix, state2 + state1)
        return probability

    def calculate_graph_partitions(self, nodes, edges, current_state):
        """Calculates partitions of a bipartite graph."""
        set1, set2, _ = self.graph_manager.obtenerConjuntosGrafoBipartito(
            nodes, edges)
        return self.total_partitions(set1, set2)

    def total_partitions(self, set1, set2):
        """Generates all possible unique partitions of two sets."""
        partitions = {}
        unique_partitions = set()

        def backtrack(set1, set2, partition1, partition2):
            if not set1 and not set2:
                partition = ','.join(map(str, partition1 + partition2))
                if partition not in unique_partitions:
                    unique_partitions.add(partition)
                    partitions[partition] = (partition1, partition2)
            else:
                for i in range(len(set1)):
                    backtrack(set1[:i] + set1[i+1:], set2,
                              partition1 + [set1[i]], partition2)
                for i in range(len(set2)):
                    backtrack(set1, set2[:i] + set2[i+1:],
                              partition1, partition2 + [set2[i]])

        backtrack(list(set2), list(set1), [], [])
        return partitions
