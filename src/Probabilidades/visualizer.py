from streamlit_agraph import agraph, Node, Edge, Config
import re
import streamlit_agraph as stag

from Probabilidades.PartitionGenerator import PartitionGenerator


class Visualizer:
    """
    Clase encargada de visualizar las mejores particiones utilizando Streamlit y AGraph.
    """

    def __init__(self, st):
        self.st = st

    def visualizar_mejor_particion(self, particiones_menores, nodes, edges):
        """
        Visualiza la mejor partición basada en las probabilidades calculadas.

        Args:
            particiones_menores (dict): Diccionario de particiones con sus probabilidades.
            nodes (list): Lista de nodos.
            edges (list): Lista de aristas.
        """
        for particion, probabilidad in particiones_menores.items():
            partes = particion.split('-')
            particion1 = re.findall(r'\((.*?)\)', partes[0].strip())
            particion2 = re.findall(r'\((.*?)\)', partes[1].strip())
            particion1 = [list(p.split()) if p else [""] for p in particion1]
            particion2 = [list(p.split()) if p else [""] for p in particion2]

            for i in range(len(particion1)):
                if [] in particion1[i]:
                    particion1[i].remove([])
                    particion1[i][0].append("")

                for arista in edges:
                    if arista.source in particion1[i][0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'

        agraph(nodes=self.st.session_state.nodes, edges=self.st.session_state.edges, config=Config(width=900, height=900, directed=False,
                                                                                                   nodeHighlightBehavior=True, physics=False))

    def pintarGrafoGenerado(self, c1, c2, estadoActual, nodes, edges, st):
        mP, _, _, _ = PartitionGenerator.retornar_mejor_particion(
            c1, c2, estadoActual)
        p1, p2 = mP
        for i in p1:
            for j in range(len(i)):
                if i[j] not in p2[0]:
                    for arista in edges:
                        if p2[0] and arista.source == i[j] and arista.to in p2[0]:
                            arista.dashes = True
                            arista.color = 'rgba(254, 20, 56, 0.5)'
        for i in p2[1]:
            if i not in p1[0]:
                for arista in edges:
                    if arista.source == i and arista.to in p1[0]:
                        arista.dashes = True
                        arista.color = 'rgba(254, 20, 56, 0.5)'
        
        config=Config(width=900, height=900, directed=False,
              nodeHighlightBehavior=True, physics=False)
        
        graph = stag.agraph(nodes=nodes, edges=edges, config = config)