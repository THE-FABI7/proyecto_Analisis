# GraphManager.py
import pandas as pd
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config
import random
import networkx as nx
import io

class GraphManager:
    def __init__(self):
        # Asegurar la inicialización de 'graph' en st.session_state
        if 'graph' not in st.session_state:
            st.session_state['graph'] = nx.Graph()
        self.graph = st.session_state['graph']

    def actualizar_estado_session(self):
        # Actualiza st.session_state con la información actual del grafo
        st.session_state.nodes = [{'id': n, 'label': st.session_state.graph.nodes[n]['label']} for n in st.session_state.graph.nodes]
        st.session_state.edges = [{'source': u, 'target': v, 'weight': st.session_state.graph.edges[u, v]['weight']} for u, v in st.session_state.graph.edges]

    # dibuja el grafo dependiendo los valores que el usuario ingresa
    def draw_graph(self, G):
        nx.draw(G, with_labels=True)
        st.pyplot()


    def draw_graph(self, G, node_color='yellow'):
        nx.draw(G, with_labels=True, node_color=node_color)
        st.pyplot()

    # TODO: hay un problema a el momento de actulizar un nodo, se desaparecen las aristas relacionadas
    # Metodo para crear un grafo personalizado


    def nuevo_grafo_personalizado(self):
        st.sidebar.title("Crear nuevo grafo")
        node_id = st.sidebar.text_input("ID del nodo")
        node_label = st.sidebar.text_input("Etiqueta del nodo")
        node_color = st.sidebar.color_picker("Color del nodo")
        add_node_button = st.sidebar.button("Agregar nodo")

        edge_start = st.sidebar.text_input("ID del nodo de inicio de la arista")
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
            node_ids = [node.id for node in st.session_state['personalizado_nodes']]
            if edge_start in node_ids and edge_end in node_ids:
                st.session_state['personalizado_edges'].append(Edge(
                    source=st.session_state['personalizado_id_map'][edge_start], target=st.session_state['personalizado_id_map'][edge_end], label=edge_weight, color=edge_color,  width=3.0))
                self.graph.add_edge(edge_start, edge_end, weight=edge_weight, color=edge_color)
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
        #boton para editar aristas
        edge_delete = st.sidebar.selectbox("arista a editar", [(
            edge.source, edge.to) for edge in st.session_state['personalizado_edges']])
        actual_edge = next(
            (edge for edge in st.session_state['personalizado_edges']
        if edge.source == edge_delete[0] and edge.to == edge_delete[1]), None,)
        
        selected_weight = st.sidebar.number_input("Nuevo Peso", min_value=1, max_value=1000, value=1)
        new_edge_color = st.sidebar.color_picker("Nuevo color de la arista")
        edit_edge_button =  st.sidebar.button("Editar arista")
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
            st.session_state['personalizado_id_map'].pop(selected_node_id, None)

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

            for node in json_data['graph'][0]['data']:
                nodes.append(
                    Node(id=node['id'], label=node['label'], color="green", font={"color": "white"}))
                for linked_node in node['linkedTo']:
                    edges.append(Edge(source=node['id'], target=linked_node['nodeId'], label=str(
                        linked_node['weight'])))

            config = Config(width=1000, height=500, directed=False,
                        nodeHighlightBehavior=True,  physics=False)
            agraph(nodes=nodes, edges=edges, config=config)


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
        st.write("Fabian Alberto Guancha vera")

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
            nodes = [Node(str(i), label=G.nodes[i]['label'], color="green", font={"color": "white"}) for i in G.nodes]
            edges = [Edge(str(edge[0]), str(edge[1]), label=str(G.edges[edge]['weight'])) for edge in G.edges]

            # Actualiza el estado de la sesión con los nuevos nodos y aristas
            st.session_state['nodes'] = nodes
            st.session_state['edges'] = edges

            # Crea un objeto de configuración
            config = Config(width=2000, height=500, directed=False, nodeHighlightBehavior=True, highlightColor="#F7A7A6", physics=False)

            # Dibuja el grafo
            agraph(nodes=nodes, edges=edges, config=config)


    def grafo_completo(self):
        # Pregunta al usuario por el número de nodos
        num_nodes = st.number_input('Número de nodos', min_value=1, value=5)

        # Añade un botón para generar un nuevo grafo completo
        if st.button('Generar nuevo grafo completo'):
            # Crea un grafo completo
            G = nx.complete_graph(num_nodes)

            # Almacena el grafo generado en st.session_state.graph
            st.session_state.graph = G

            # Convierte el grafo en una lista de nodos y aristas para streamlit_agraph
            nodes = [Node(str(i), label=f"Node {i}", color="green", font={"color": "white"}) for i in G.nodes]
            edges = [Edge(source=str(u), target=str(v), label="1") for u, v in G.edges]

            # Actualiza el estado de la sesión con los nuevos nodos y aristas
            st.session_state['nodes'] = nodes
            st.session_state['edges'] = edges

            # Crea un objeto de configuración
            config = Config(width=2000, height=500, directed=False, nodeHighlightBehavior=True, highlightColor="#F7A7A6", physics=False)

            # Dibuja el grafo
            agraph(nodes=nodes, edges=edges, config=config)


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

        # Convierte el grafo en una lista de nodos y aristas para strreamlit_agraph
        nodes = [Node(str(node), label=f"Node {node}", font={"color": "white"}) for node in G.nodes]
        edges = [Edge(source=str(u), target=str(v), label="1") for u, v in G.edges]

        # Actualiza el estado de la sesión con los nuevos nodos y aristas
        st.session_state['nodes'] = nodes
        st.session_state['edges'] = edges

        # Configura y muestra el grafo en la interfaz de usuario
        config = Config(height=500, width=500, nodeHighlightBehavior=True, highlightColor="#F7A7A6", directed=True, physics=False)
        agraph(nodes=nodes, edges=edges, config=config)


    def GrafoBipartito(self, numNodosGrupo1: int, numNodosGrupo2: int):
        # Crear grafo bipartito completo
        self.graph = nx.complete_bipartite_graph(numNodosGrupo1, numNodosGrupo2)

        # Agregar etiquetas y colores a los nodos
        for i, node in enumerate(self.graph.nodes()):
            grupo = 'Grupo 1' if self.graph.nodes[node]['bipartite'] == 0 else 'Grupo 2'
            self.graph.nodes[node]['label'] = f'Nodo {i + 1} ({grupo})'
            self.graph.nodes[node]['color'] = 'skyblue' if grupo == 'Grupo 1' else 'lightgreen'

        # Agregar pesos aleatorios a las aristas
        for u, v in self.graph.edges():
            self.graph.edges[u, v]['weight'] = random.randint(1, 100)

        # Actualizar el estado de la sesión para reflejar los cambios en el grafo
        self.actualizar_estado_session()

        # Preparar nodos y aristas para visualización
        nodes = [Node(id=str(n), label=self.graph.nodes[n]['label'], color=self.graph.nodes[n]['color']) for n in self.graph.nodes()]
        edges = [Edge(source=str(u), target=str(v), label=str(self.graph.edges[u, v]['weight'])) for u, v in self.graph.edges()]

        # Retornar nodos y aristas para visualización
        return nodes, edges


    def get_graph(self):
        return self.graph
    
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
            df_nodes = pd.concat([df_nodes, pd.DataFrame({'Node': [node], 'Label': [data['label']]})], ignore_index=True)

        # Crear un DataFrame con las aristas
        df_edges = pd.DataFrame(columns=['Source', 'Target', 'Weight'])
        for u, v, w in G.edges(data='weight'):
            df_edges = pd.concat([df_edges, pd.DataFrame({'Source': [u], 'Target': [v], 'Weight': [w]})], ignore_index=True)

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