import re
from streamlit_agraph import Config

def Gui(directed: bool):
    return Config(width=1000,
                height=1000,
                directed=directed,
                physics=False,
                nodeHighlightBehavior=False, 
                highlightColor="#F7A7A6", # or "blue"
                collapsible=False,
                node={'labelProperty':'label'},
                )

def visualizar_mejor_particion(self, particiones_menores, nodes, edges, st):
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

        st.agraph(nodes=self.st.session_state.nodes, edges=self.st.session_state.edges, config=Config(width=900, height=900, directed=False,
                                                                                                   nodeHighlightBehavior=True, physics=False))