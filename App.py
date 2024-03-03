import os
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config
import random


def main():

    navbar_options = ["Archivo", "Editar", "Ejecutar",
                      "Herramientas", "Ventana", "Ayuda"]
    archivo_options = ["nuevo grafo", "Abrir", "Cerrar", "Guardar",
                       "Guardar como", "Exportar datos", "Importar datos", "Salir"]
    editar_options = ["Deshacer", "Arco", "Nodo"]
    ejecutar_options = ["procesos"]
    ventana_options = ["Gráfica", "Tabla"]
    ayuda_options = ["Ayuda", "Acerca de Grafos"]
    # Usa un archivo de imagen y muéstralo en el encabezado de la barra lateral usando st.image.
    st.sidebar.markdown(
        f'<img src="https://www.ucaldas.edu.co/portal/wp-content/uploads/2020/05/monitorias-1.jpg" width="100" class="my-sidebar-image">', unsafe_allow_html=True)

    navbar_selection = st.sidebar.selectbox("Menú", navbar_options)

    if navbar_selection == "Archivo":
        archivo_selection = st.sidebar.selectbox("Opciones", archivo_options)
        if archivo_selection == "nuevo grafo":
            tipo_grafo_options = ["personalizado", "Aleatorio"]
            tipo_grafo = st.sidebar.selectbox(
                "Tipo de grafo", tipo_grafo_options)
            if tipo_grafo == "personalizado":
                nuevo_grafo_personalizado()
            else:
                nuevo_grafo_aleatorio()

        if archivo_selection == "Abrir":

            abrir_grafo()

        elif archivo_selection == "Cerrar":
            os._exit(0)

        if archivo_selection == "Guardar":
            st.write("Has seleccionado la Sub opción 3")
        if archivo_selection == "Guardar como":
            st.write("Has seleccionado la Sub opción 3")
        if archivo_selection == "Exportar datos":
            st.write("Has seleccionado la opción de exportación a Excel")
        if archivo_selection == "Importar datos":
            importar_datos()

    elif navbar_selection == "Editar":
        archivo_selection = st.sidebar.selectbox("Opciones", editar_options)
        if archivo_selection == "Deshacer":
            st.write("Has seleccionado la Sub opción 1")
        if archivo_selection == "Nodo":
            st.write("Has seleccionado la Sub opción 1")
        if archivo_selection == "Arco":
            st.write("Has seleccionado la Sub opción arco")

    elif navbar_selection == "Ejecutar":
        archivo_selection = st.sidebar.selectbox("Opciones", ejecutar_options)
        if archivo_selection == "procesos":
            st.write("Has seleccionado la Sub opción 1")

    elif navbar_selection == "Ventana":
        archivo_selection = st.sidebar.selectbox("Opciones", ventana_options)
        if archivo_selection == "Gráfica":
            st.write("Has seleccionado la Sub opción 1")
        if archivo_selection == "Tabla":
            st.write("Has seleccionado la Sub opción 1")

    elif navbar_selection == "Herramientas":
        st.write("Has seleccionado la Sub opción 1")

    elif navbar_selection == "Ayuda":
        archivo_selection = st.sidebar.selectbox("Opciones", ayuda_options)
        if archivo_selection == "Ayuda":
            st.write("Has seleccionado la Sub opción 1")
        if archivo_selection == "Acerca de Grafos":
            acerca_de_grafos()


def draw_graph(G):
    nx.draw(G, with_labels=True)
    st.pyplot()


def draw_graph(G, node_color='yellow'):
    nx.draw(G, with_labels=True, node_color=node_color)
    st.pyplot()


def nuevo_grafo_personalizado():
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

    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
    if 'edges' not in st.session_state:
        st.session_state['edges'] = []
    if 'id_map' not in st.session_state:
        st.session_state['id_map'] = {}

    if add_node_button:
        st.session_state['nodes'].append(
            Node(id=node_id, label=node_label, color=node_color, font={"color": "white"}))
        st.session_state['id_map'][node_id] = node_id

    if add_edge_button:
        node_ids = [node.id for node in st.session_state['nodes']]
        if edge_start in node_ids and edge_end in node_ids:
            st.session_state['edges'].append(Edge(
                source=st.session_state['id_map'][edge_start], target=st.session_state['id_map'][edge_end], label=edge_weight, color=edge_color))
        else:
            st.error(
                "Los nodos de inicio y fin deben existir antes de agregar una arista.")

    selected_node_id = st.sidebar.selectbox("Selecciona un nodo para editar", options=[
                                            node.id for node in st.session_state['nodes']])
    new_node_id = st.sidebar.text_input("Nuevo ID del nodo")
    new_node_label = st.sidebar.text_input("Nueva etiqueta del nodo")
    new_node_color = st.sidebar.color_picker("Nuevo color del nodo")
    edit_node_button = st.sidebar.button("Editar nodo")

    if edit_node_button:
        for node in st.session_state['nodes']:
            if node.id == selected_node_id:
                st.session_state['id_map'][selected_node_id] = new_node_id
                node.id = new_node_id
                node.label = new_node_label
                node.color = new_node_color

    config = Config(width=900, height=900, directed=False,
                    nodeHighlightBehavior=True)
    agraph(nodes=st.session_state['nodes'],
           edges=st.session_state['edges'], config=config)


def abrir_grafo():
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

        config = Config(width=500, height=500, directed=False,
                        nodeHighlightBehavior=True)
        agraph(nodes=nodes, edges=edges, config=config)


def importar_datos():
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

        config = Config(width=500, height=500, directed=False,
                        nodeHighlightBehavior=True)
        agraph(nodes=nodes, edges=edges, config=config)


def acerca_de_grafos():
    st.write("acerca_de_grafos")
    st.write("Grafos es una aplicación que permite crear, editar y visualizar grafos. Esta aplicación fue desarrollada por estudiantes de la Universidad de Caldas como proyecto final para la asignatura de Analisis y Diseño de algoritmos.")
    st.write("Integrantes:")
    st.write("Fabian Alberto Guancha vera")


def nuevo_grafo_aleatorio():
    # Ask the user for the number of nodes and edges
    num_nodes = st.number_input('Number of nodes', min_value=1, value=5)
    num_edges = st.number_input('Number of edges', min_value=1, value=5)

    # Create an empty graph
    G = nx.Graph()

    # Add nodes
    for i in range(num_nodes):
        G.add_node(i, label=f"Node {i}")

    # Add edges
    while G.number_of_edges() < num_edges:
        # Randomly select two nodes
        node1 = random.choice(list(G.nodes))
        node2 = random.choice(list(G.nodes))

        # Add an edge between the two nodes
        if node1 != node2 and not G.has_edge(node1, node2):
            weight = random.randint(1, 10)  # Random weight between 1 and 10
            G.add_edge(node1, node2, weight=weight)

    # Convert the graph into a list of nodes and edges for streamlit_agraph
    nodes = [Node(str(i), label=G.nodes[i]['label']) for i in G.nodes]
    edges = [Edge(str(edge[0]), str(edge[1]), label=str(
        G.edges[edge]['weight'])) for edge in G.edges]

    # Create a config object
    config = Config(width=700, height=700, directed=False)

    # Draw the graph
    return agraph(nodes=nodes, edges=edges, config=config)


if __name__ == "__main__":
    main()
