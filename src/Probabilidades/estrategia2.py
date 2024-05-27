from models.GraphManager import GraphManager
import numpy as np
from itertools import chain, combinations
import networkx as nx
import random
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt


class estrategia2:
    def conjunto(self, listaNodos: List[Any]) -> chain:
        """Genera todas las combinaciones posibles de un conjunto de nodos."""
        s = list(listaNodos)
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))
    
    def generarConjuntosConPeso(self, nodes: List[Any], edges: List[Any]) -> List[Tuple[Tuple[set, set], float, List[str]]]:
        """Genera todas las particiones posibles de los nodos y calcula el peso total de las aristas entre las particiones."""
        todas_las_particiones = []
        n = len(nodes)
        
        for i in range(1, 2**n // 2):
            S1, S2 = estrategia2.obtener_subconjuntos(self,nodes, i, n)
            total_weight, aristasEliminadas = estrategia2.calcular_peso_total(self,S1, S2, edges)
            todas_las_particiones.append(((S1, S2), total_weight, aristasEliminadas))
        
        return todas_las_particiones
    
    def obtener_subconjuntos(self, nodes: List[Any], i: int, n: int) -> Tuple[set, set]:
        """Obtiene los subconjuntos S1 y S2 a partir del índice i."""
        indicesS1 = [j for j in range(n) if (i >> j) & 1]
        S1 = set([nodes[idx] for idx in indicesS1])
        S2 = set(nodes) - S1
        return S1, S2

    def calcular_peso_total(self, S1: set, S2: set, edges: List[Any]) -> Tuple[float, List[str]]:
        """Calcula el peso total de las aristas entre dos subconjuntos S1 y S2."""
        s11 = [nodo.id for nodo in S1]
        s22 = [nodo.id for nodo in S2]
        ss1 = [str(nodo.id) for nodo in S1]
        ss2 = [str(nodo.id) for nodo in S2]
        aristasEliminadas = []
        total_weight = 0
        
        for edge in edges:
            if ((edge.source in s11 and edge.to in s22) or 
                (edge.source in s22 and edge.to in s11) or 
                (edge.source in ss1 and edge.to in ss2) or 
                (edge.source in ss2 and edge.to in ss1)):
                total_weight += float(edge.weight)
                aristasEliminadas.append(f"{edge.source} => {edge.to}")
        
        return total_weight, aristasEliminadas
    
    def mostrarParticiones(self, numNodosConjunto1, numNodosConjunto2, Node, Edge):
        """Muestra todas las particiones posibles y encuentra la partición con el menor peso."""
        nodes, edges = GraphManager.generar_grafo_bipartito(self,numNodosConjunto1, numNodosConjunto2, Node, Edge)
        todas_las_particiones = estrategia2.generarConjuntosConPeso(self,nodes, edges)
        resultados = estrategia2.procesar_particiones(self,todas_las_particiones)
        return nodes, edges, resultados
    
    def mostrarParticiones2(self, nodes: List[Any], edges: List[Any]) -> Dict[str, Any]:
        """Muestra todas las particiones posibles y encuentra la partición con el menor peso, sin generar un grafo bipartito."""
        todas_las_particiones = estrategia2.generarConjuntosConPeso(self,nodes, edges)
        resultados = estrategia2.procesar_particiones(self,todas_las_particiones)
        return resultados
    
    def procesar_particiones(self, particiones: List[Tuple[Tuple[set, set], float, List[str]]]) -> Dict[str, Any]:
        """Procesa todas las particiones posibles y encuentra la partición con el menor peso."""
        peso_menor = float('inf')
        resultados = {
            "subgrafos": [],
            "mejorSubGrafo": {},
            "AristasNoConsideradas": {}
        }
        
        for particion, peso_total, listaAristas in particiones:
            datosSubgrafos = {
                "G1": [nodo.id for nodo in particion[0]],
                "G2": [nodo.id for nodo in particion[1]],
                "peso_minimo_aristas_eliminadas": peso_total,
                "AristasNoConsideradas": listaAristas
            }
            resultados["subgrafos"].append(datosSubgrafos)
            if peso_total < peso_menor:
                peso_menor = peso_total
                resultados["mejorSubGrafo"] = datosSubgrafos
        
        return resultados
    
    def mostrarParticiones3(self, nodes: List[Any], edges: List[Any], st: Any) -> None:
        """Genera particiones y visualiza los grafos resultantes en Streamlit."""
        todas_las_particiones = estrategia2.generarConjuntosConPeso(self,nodes, edges)
        for particion, peso_total, listaAristas in todas_las_particiones:
            G = nx.Graph()
            G.add_nodes_from([nodo.id for nodo in particion[0]], label="Conjunto 1")
            G.add_nodes_from([nodo.id for nodo in particion[1]], label="Conjunto 2")
            for arista in listaAristas:
                nodo1, nodo2 = arista.split(" => ")
                G.add_edge(nodo1.strip(), nodo2.strip())
            
            pos = nx.spring_layout(G)
            nx.draw_networkx_nodes(G, pos, nodelist=[nodo.id for nodo in particion[0]], node_color="r", label="Conjunto 1")
            nx.draw_networkx_nodes(G, pos, nodelist=[nodo.id for nodo in particion[1]], node_color="b", label="Conjunto 2")
            nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=1.0, alpha=0.5)
            nx.draw_networkx_labels(G, pos, font_size=8)
            plt.title("Subgrafo")
            plt.axis("off")
            plt.legend()
            st.pyplot(plt)
   
   

   
   

   
   