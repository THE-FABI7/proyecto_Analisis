import unittest

# Ajusta la ruta de importación según tu estructura de proyecto
from src.Probabilidades.PartitionGenerator import PartitionGenerator
from src.Probabilidades.ProbabilityDistribution import ProbabilityDistribution

class TestPartitionGenerator(unittest.TestCase):

    def setUp(self):
        # Configurar la distribución de probabilidades para los nodos A, B, C y D
        self.prob_dist = ProbabilityDistribution()
        self.partition_generator = PartitionGenerator(self.prob_dist)

    def test_mejor_particion(self):
        # Definir los conjuntos de nodos
        nodosG1 = ['A', 'B', 'C', 'D']
        nodosG2 = ['A\'', 'B\'', 'C\'', 'D\'']

        # Convertir los nodos de estado futuro
        aux2 = [nodo[:-1] for nodo in nodosG2]

        # Ejecutar la estrategia de dividir y vencer
        
        particion, valor = self.partition_generator.dividir_y_vencer(nodosG1, aux2)

        # Verificar la mejor partición y la diferencia
        self.assertEqual(particion, ([], ['A', 'B', 'C', 'D']))
        self.assertEqual(valor, 0)

if __name__ == '__main__':
    unittest.main()
