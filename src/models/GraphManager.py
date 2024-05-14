# GraphManager.py
import pandas as pd
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
from streamlit_agraph import agraph, Node, Edge, Config
import random
import networkx as nx
import io
from networkx.algorithms.components import is_connected

from .NodeManager import NodeManager
from .EdgeManager import EdgeManager


class GraphManager:
    def __init__(self):
        # Asegurar la inicialización de 'graph' en st.session_state
        if 'graph' not in st.session_state:
            st.session_state['graph'] = nx.Graph()
        self.graph = st.session_state['graph']
        self.node_manager = NodeManager(self.graph)
        self.edge_manager = EdgeManager(self.graph)

    def actualizar_estado_session(self):
        # Actualiza st.session_state con la información actual del grafo
        st.session_state.nodes = [
            {'id': n, 'label': st.session_state.graph.nodes[n]['label']} for n in st.session_state.graph.nodes]
        st.session_state.edges = [
            {'source': u, 'target': v, 'weight': st.session_state.graph.edges[u, v]['weight']} for u, v in st.session_state.graph.edges]

    # dibuja el grafo dependiendo los valores que el usuario ingresa
    def draw_graph(self, G):
        nx.draw(G, with_labels=True)
        st.pyplot()

    def draw_graph(self, G, node_color='yellow'):
        nx.draw(G, with_labels=True, node_color=node_color)
        st.pyplot()

    # TODO: hay un problema a el momento de actulizar un nodo, se desaparecen las aristas relacionadas
    # Metodo para crear un grafo personalizado

    def grafo_personalizado(self):
        st.sidebar.title("Crear nuevo grafo")
        node_id = st.sidebar.text_input("ID del nodo")
        node_label = st.sidebar.text_input("Etiqueta del nodo")
        node_color = st.sidebar.color_picker("Color del nodo")
        add_node_button = st.sidebar.button("Agregar nodo")

        edge_start = st.sidebar.text_input(
            "ID del nodo de inicio de la arista")
        edge_end = st.sidebar.text_input("ID del nodo final de la arista")
        edge_weight = st.sidebar.text_input("Peso de la arista")
        edge_color = st.sidebar.color_picker("Color de la arista")
        add_edge_button = st.sidebar.button("Agregar arista")

        # El código verifica si la clave 'nodos' no está presente en el diccionario `st.session_state` en
        # Python. Si la clave 'nodos' no está presente, el código ejecutará el bloque de código indicado
        # por `

        if 'personalizado_nodes' not in st.session_state:
            st.session_state['personalizado_nodes'] = []
        if 'personalizado_edges' not in st.session_state:
            st.session_state['personalizado_edges'] = []
        if 'personalizado_id_map' not in st.session_state:
            st.session_state['personalizado_id_map'] = {}

        if add_node_button:
            # condicion para que no se agreguen nodos sin id y sin etiqueta
            if node_id == "" or node_label == "":
                st.error("El ID y la etiqueta del nodo son obligatorios.")
                return None
            st.session_state['personalizado_nodes'].append(
                Node(id=node_id, label=node_label, color=node_color, font={"color": "white"}))
            st.session_state['personalizado_id_map'][node_id] = node_id
            self.graph.add_node(node_id, label=node_label, color=node_color)
            self.actualizar_estado_session()

        if add_edge_button:
            node_ids = [
                node.id for node in st.session_state['personalizado_nodes']]
            if edge_start in node_ids and edge_end in node_ids:
                st.session_state['personalizado_edges'].append(Edge(
                    source=st.session_state['personalizado_id_map'][edge_start], target=st.session_state['personalizado_id_map'][edge_end], label=edge_weight, color=edge_color,  width=3.0))
                self.graph.add_edge(edge_start, edge_end,
                                    weight=edge_weight, color=edge_color)
                self.actualizar_estado_session()

            else:
                st.error(
                    "Los nodos de inicio y fin deben existir antes de agregar una arista.")

        selected_node_id = st.sidebar.selectbox("Selecciona un nodo para editar", options=[
                                                node.id for node in st.session_state['personalizado_nodes']])
        new_node_id = st.sidebar.text_input("Nuevo ID del nodo")
        new_node_label = st.sidebar.text_input("Nueva etiqueta del nodo")
        new_node_color = st.sidebar.color_picker("Nuevo color del nodo")
        edit_node_button = st.sidebar.button("Editar nodo")

        if edit_node_button:
            for node in st.session_state['personalizado_nodes']:
                if node.id == selected_node_id:
                    if new_node_id != "":
                        st.session_state['personalizado_id_map'][selected_node_id] = new_node_id
                        node.id = new_node_id
                    if new_node_label != "":
                        node.label = new_node_label
                    if new_node_color != "":
                        node.color = new_node_color
        # boton para editar aristas
        edge_delete = st.sidebar.selectbox("arista a editar", [(
            edge.source, edge.to) for edge in st.session_state['personalizado_edges']])
        actual_edge = next(
            (edge for edge in st.session_state['personalizado_edges']
             if edge.source == edge_delete[0] and edge.to == edge_delete[1]), None,)

        selected_weight = st.sidebar.number_input(
            "Nuevo Peso", min_value=1, max_value=1000, value=1)
        new_edge_color = st.sidebar.color_picker("Nuevo color de la arista")
        edit_edge_button = st.sidebar.button("Editar arista")
        if edit_edge_button:
            actual_edge.weight = selected_weight
            actual_edge.label = str(selected_weight)
            actual_edge.color = new_edge_color

        selected_node_id = st.sidebar.selectbox("Selecciona un nodo para eliminar", options=[
            node.id for node in st.session_state['personalizado_nodes']])
        delete_node_button = st.sidebar.button("Eliminar nodo")
        if delete_node_button:
            st.session_state['personalizado_nodes'] = [
                node for node in st.session_state['personalizado_nodes'] if node.id != selected_node_id]
            st.session_state['personalizado_id_map'].pop(
                selected_node_id, None)

        edge_delete = st.sidebar.selectbox("Seleccione la arista", [(
            edge.source, edge.to) for edge in st.session_state['personalizado_edges']])
        actuaal_edge = next(
            (edge for edge in st.session_state['personalizado_edges']
             if edge.source == edge_delete[0] and edge.to == edge_delete[1]), None, )
        delete_arista_button = st.sidebar.button("Eliminar arista")
        if delete_arista_button:
            if actuaal_edge is not None:
                actuaal_edge.dashes = True
                # Encuentra la arista correspondiente en el gráfico y cambia su color y ancho
                for u, v, data in self.graph.edges(data=True):
                    if u == actuaal_edge.source and v == actuaal_edge.to:
                        data['color'] = actuaal_edge.color
                        data['width'] = actuaal_edge.width
                st.warning('Esta arista ya fue eliminada anteriormente')
                st.session_state["last_action"] = "Delete edge"
            else:
                st.error('No se encontró ninguna arista para eliminar.')

        config = Config(width=900, height=900, directed=False,
                        nodeHighlightBehavior=True,  physics=False)
        agraph(nodes=st.session_state['personalizado_nodes'],
               edges=st.session_state['personalizado_edges'], config=config)

    def nuevo_grafo_personalizado2(self, st):
        # Usar node_manager y edge_manager para gestionar nodos y aristas
        self.node_manager.gestionar_nodos(st)
        self.edge_manager.gestionar_aristas()
        self._dibujar_grafo()

    def _dibujar_grafo(self):
        # Dibuja el grafo utilizando los nodos y aristas gestionados por las clases auxiliares.
        if 'nodes' in st.session_state and 'edges' in st.session_state:
            agraph(nodes=st.session_state['nodes'], edges=st.session_state['edges'],
                   config=Config(width=900, height=900, directed=False,
                                 nodeHighlightBehavior=True, physics=False))

    # Metoddo para abrir el grafo
    def abrir_grafo(self):
        uploaded_file = st.file_uploader("Elige un archivo .json", type="json")
        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name,
                            "FileType": uploaded_file.type}
            st.write(file_details)
            json_data = json.load(uploaded_file)

            nodes = []
            edges = []

            if "graph" in json_data:
                for nodeData in json_data["graph"][0]["data"]:
                    node_id = nodeData["id"]
                    nodes.append(Node(id=node_id, size=nodeData["radius"],
                                      label=nodeData["label"],
                                      type=nodeData["type"], data=nodeData["data"], color="green", shape=None))

                for nodeData in json_data["graph"][0]["data"]:
                    node_id = nodeData["id"]
                    for link in nodeData["linkedTo"]:
                        linked_node_id = link["nodeId"]
                        edge_color = EdgeManager.asignarColorArista(
                            link["weight"])
                        edges.append(Edge(source=node_id, target=linked_node_id,
                                          weight=link["weight"], label=str(
                                              link["weight"]),
                                          width=3, color=edge_color))
                        if not any(node.id == linked_node_id for node in nodes):
                            nodes.append(Node(id=linked_node_id, size=20,
                                              label=str(linked_node_id),
                                              type="circle", color="blue", shape=None))

            else:

                for node in json_data['graph'][0]['data']:
                    nodes.append(
                        Node(id=node['id'], label=node['label'], color="green", font={"color": "white"}))
                    for linked_node in node['linkedTo']:
                        edge_color = GraphManager.asignarColorArista(
                            linked_node['weight'])
                        edges.append(Edge(source=node['id'], target=linked_node['nodeId'], label=str(
                            linked_node['weight']),  color=edge_color))
                        # si las aristas no tienen peso el color de las aristas sea por defecto morado
                        if linked_node['weight'] == "":
                            edge_color = "purple"
                            edges.append(Edge(source=node['id'], target=linked_node['nodeId'], label=str(
                                linked_node['weight']),  color=edge_color))

            config = Config(width=1000, height=500, directed=False,
                            nodeHighlightBehavior=True,  physics=False)
            agraph(nodes=nodes, edges=edges, config=config)
            return json_data
        return None

    def importar_datos(self):
        uploaded_file = st.file_uploader("Elige un archivo .txt", type="txt")
        if uploaded_file is not None:
            file_details = {"FileName": uploaded_file.name,
                            "FileType": uploaded_file.type}
            st.write(file_details)

            # Assuming the txt file has lines in the format: id,label,linkedTo
            nodes = []
            edges = []

            for line in uploaded_file:
                # Decode the binary data to text
                decoded_line = line.decode('utf-8')
                node_data = decoded_line.strip().split(',')
                nodes.append(
                    Node(id=node_data[0], label=node_data[1], color="green", font={"color": "white"}))
                # Assuming linked nodes are separated by semicolons
                linked_nodes = node_data[2].split(';')
                for linked_node in linked_nodes:
                    # Assuming linked node format is nodeId:weight
                    linked_node_data = linked_node.split(':')
                    edges.append(Edge(source=node_data[0], target=linked_node_data[0], label=str(
                        linked_node_data[1])))

            config = Config(width=1000, height=500, directed=False,
                            nodeHighlightBehavior=True,  physics=False)
            agraph(nodes=nodes, edges=edges, config=config)

    # Metdo par amostrar lo que se va a mostrar en acerca de grafos

    def acerca_de_grafos(self):
        st.write("acerca_de_grafos")
        st.write("Grafos es una aplicación que permite crear, editar y visualizar grafos. Esta aplicación fue desarrollada por estudiantes de la Universidad de Caldas como proyecto final para la asignatura de Analisis y Diseño de algoritmos.")
        st.write("Integrantes:")
        st.write("Fabian Alberto Guancha vera y Erley Jhovan Cabrera")

    # TODO:hay un problema a el momento de dar click sobre un nodo, se desaparece y renderiza un nuevo grafo
    def nuevo_grafo_aleatorio(self):
        # Pregunta al usuario por el número de nodos y aristas
        num_nodes = st.number_input('Number of nodes', min_value=1, value=5)
        num_edges = st.number_input('Number of edges', min_value=1, value=5)

        # Añade un botón para generar un nuevo grafo aleatorio
        if st.button('Generate new random graph'):
            # Crea un grafo vacío
            G = nx.Graph()

            # Añade nodos
            for i in range(num_nodes):
                G.add_node(i, label=f"Node {i}")

            # Añade aristas
            while G.number_of_edges() < num_edges:
                # Selecciona dos nodos al azar
                node1, node2 = random.sample(list(G.nodes), 2)

                # Añade una arista entre los dos nodos si no existe ya
                if not G.has_edge(node1, node2):
                    # Peso aleatorio entre 1 y 10
                    weight = random.randint(1, 10)
                    G.add_edge(node1, node2, weight=weight)

            # Actualiza el grafo en el estado de la sesión
            st.session_state.graph = G

            # Convierte el grafo en una lista de nodos y aristas para streamlit_agraph
            nodes = [
                Node(str(i), label=f"Node {i}",
                     color="green", font={"color": "white"})
                for i in G.nodes
            ]
            edges = [
                Edge(str(u), str(v), label=str(G.edges[u, v]['weight']))
                for u, v in G.edges
            ]

            # Actualiza el estado de la sesión con los nuevos nodos y aristas
            st.session_state['nodes'] = nodes
            st.session_state['edges'] = edges

            # Crea un objeto de configuración
            config = st.session_state.get(
                'config',
                Config(width=500, height=800, directed=False,
                       nodeHighlightBehavior=True, highlightColor="#F7A7A6", physics=False)
            )
            st.session_state['config'] = config
            # Dibuja el grafo
            agraph(nodes=nodes, edges=edges, config=config)
            self.guardarCambios()

    def grafo_completo(self):
        # Pregunta al usuario por el número de nodos
        num_nodes = st.number_input('Número de nodos', min_value=1, value=5)

        # Añade un botón para generar un nuevo grafo completo
        if st.button('Generar nuevo grafo completo'):
            # Crea un grafo completo
            G = nx.complete_graph(num_nodes)
            for i in G.nodes():
                G.nodes[i]['label'] = f'{i}'

            # Almacena el grafo generado en st.session_state.graph
            st.session_state.graph = G

            # Convierte el grafo en una lista de nodos y aristas para streamlit_agraph
            nodes = [Node(str(i), label=f"Node {i}", color="green", font={
                          "color": "white"}) for i in G.nodes]
            edges = [Edge(source=str(u), target=str(v), label="10")
                     for u, v in G.edges]

            # Actualiza el estado de la sesión con los nuevos nodos y aristas
            st.session_state['nodes'] = nodes
            st.session_state['edges'] = edges

            self.guardarCambios()

            return nodes, edges
        return None, None

    def grafo_dirigido(self):
        # Pregunta al usuario por el número de nodos
        num_nodos = st.number_input('Número de nodos', min_value=1, value=5)

        # Genera un grafo dirigido con networkx
        G = nx.DiGraph()
        G.add_nodes_from(range(num_nodos))

        # Agrega aristas para formar un ciclo (esto es solo un ejemplo, puedes personalizarlo)
        G.add_edges_from([(i, (i+1) % num_nodos) for i in range(num_nodos)])

        # Almacena el grafo generado en st.session_state.graph
        st.session_state.graph = G

       # Convertir el grafo en una lista de nodos y aristas para streamlit_agraph
        nodes = [Node(str(node), label=f"Node {node}", font={
                      "color": "white"}) for node in G.nodes]
        edges = [Edge(source=str(u), target=str(v), label="1")
                 for u, v in G.edges]

        # Actualiza el estado de la sesión con los nuevos nodos y aristas
        st.session_state['nodes'] = nodes
        st.session_state['edges'] = edges

        self.guardarCambios()

        return nodes, edges

    def GrafoBipartito(self, numNodosGrupo1: int, numNodosGrupo2: int):

        G = nx.complete_bipartite_graph(numNodosGrupo1, numNodosGrupo2)

        for i, (node, data) in enumerate(G.nodes(data=True)):
            grupo = 0 if i < numNodosGrupo1 else 1
            G.nodes[node]['label'] = f'Nodo {i + 1}'
            G.nodes[node]['color'] = 'skyblue' if grupo == 0 else 'lightgreen'

        for u, v, data in G.edges(data=True):
            G.edges[u, v]['weight'] = random.randint(1, 100)
            G.edges[u, v]['color'] = 'gray'

        nodes = [Node(id=str(node), label=G.nodes[node]['label'],
                      color=G.nodes[node]['color']) for node in G.nodes()]
        edges = [Edge(source=str(u), target=str(v), label=str(
            G.edges[u, v]['weight']), color=G.edges[u, v]['color']) for u, v in G.edges()]

        # Actualiza el estado de la sesión con los nuevos nodos y aristas
        st.session_state.graph = G
        st.session_state['nodes'] = nodes
        st.session_state['edges'] = edges

        # Configuración de la visualización del grafo
        config = Config(height=600, width=800, directed=False,
                        nodeHighlightBehavior=True, highlightColor="#F7A7A6", physics=False)

        # Dibujar el grafo
        agraph(nodes=nodes, edges=edges, config=config)

        self.guardarCambios()

        return nodes, edges

    @staticmethod
    def asignarColorArista(peso):
        if peso >= 0 and peso <= 20:
            return "blue"
        elif peso > 20 and peso <= 40:
            return "green"
        elif peso > 40 and peso <= 60:
            return "yellow"
        elif peso > 60 and peso <= 80:
            return "orange"
        elif peso > 80:
            return "red"
        else:
            return "gray"

    def get_graph(self):
        return self.graph

    def guardarCambios(self):
        # Muestra un botón "Guardar Cambios" después de generar el grafo
        if st.button('Guardar Cambios'):
            # Aquí puedes realizar cualquier operación necesaria antes de recargar
            # Por ejemplo, asegurarte de que todos los cambios en el grafo se han aplicado
            # y están reflejados en st.session_state

            # Recargar la página para mostrar los grafos cargados
            st.experimental_rerun()

    def mostrarGrafoTabla(self, nodes, edges, st):
        # Crear el grafo con networkx
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.id, label=node.label)
        for edge in edges:
            G.add_edge(edge.source, edge.to, weight=edge.label)

        # Crear un DataFrame con los nodos
        df_nodes = pd.DataFrame(columns=['Node', 'Label'])
        for node, data in G.nodes(data=True):
            df_nodes = pd.concat([df_nodes, pd.DataFrame(
                {'Node': [node], 'Label': [data['label']]})], ignore_index=True)

        # Crear un DataFrame con las aristas
        df_edges = pd.DataFrame(columns=['Source', 'Target', 'Weight'])
        for u, v, w in G.edges(data='weight'):
            df_edges = pd.concat([df_edges, pd.DataFrame(
                {'Source': [u], 'Target': [v], 'Weight': [w]})], ignore_index=True)

        # Mostrar los DataFrames en Streamlit
        st.write('Nodos')
        st.write(df_nodes)
        st.write('Aristas')
        st.write(df_edges)

    # def mostrarGrafoEnGrafica(self, nodes, edges, st):
        # # Crear el grafo con networkx
        # G = nx.Graph()
        # for node in nodes:
        # G.add_node(node.id, label=node.label)
        # for edge in edges:
        # G.add_edge(edge.source, edge.to, weight=edge.label)

        # # Dibujar el grafo con networkx
        # plt.figure(figsize=(10, 5))
        # nx.draw(G, with_labels=True)
        # st.pyplot()

    def esBipartito(self, nodes, edges) -> bool:
        # Crear el grafo con networkx
        salida = False
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.id, label=node.label)
        for edge in edges:
            G.add_edge(edge.source, edge.to, weight=edge.label)

        # verificar si en el grafo hay una arista de color 'rgba(254, 20, 56, 0.5)'
        for edge in edges:
            if edge.color == 'rgba(254, 20, 56, 0.5)':
                salida = True
            else:
                salida = bipartite.is_bipartite(G)
        return salida

    def esBipartitoConexoOdisconexo(self, nodes, edges) -> str:
        # Crear el grafo con networkx
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.id, label=node.label)
        for edge in edges:
            # Solo agregar las aristas que no tienen este color
            if edge.color != 'rgba(254, 20, 56, 0.5)':
                G.add_edge(edge.source, edge.to, weight=edge.label)

        # Verificar si el grafo es bipartito
        if not bipartite.is_bipartite(G):
            return "El grafo no es bipartito."

        # Verificar si el grafo no está vacío (tiene nodos) antes de comprobar la conectividad
        if len(G) == 0:
            return "El grafo está vacío."

        # Verificar si el grafo es conexo o disconexo
        if is_connected(G):
            return "El grafo es bipartito y conexo."
        else:
            return "El grafo es bipartito y disconexo."

    def esBipartitoConexo(self, nodes, edges) -> bool:
        # Crear el grafo con networkx
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.id, label=node.label)
        for edge in edges:
            G.add_edge(edge.source, edge.to, weight=edge.label)
        for edge in edges:
            if edge.color == 'rgba(254, 20, 56, 0.5)':
                return False
            else:
                return bipartite.is_bipartite(G)
