import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config


def main():
    navbar_options = ["Archivo", "Editar", "Ejecutar",
                      "Herramientas", "Ventana", "Ayuda"]
    archivo_options = ["nuevo grafo", "Abrir", "Cerrar", "Guardar",
                       "Guardar como", "Exportar datos", "Importar datos", "Salir"]
    editar_options = ["Deshacer", "Arco", "Nodo"]
    ejecutar_options = ["procesos"]
    ventana_options = ["Gráfica", "Tabla"]
    ayuda_options = ["Ayuda", "Acerca de Grafos"]

    navbar_selection = st.sidebar.selectbox("Menú", navbar_options)

    if navbar_selection == "Archivo":
        archivo_selection = st.sidebar.selectbox("Opciones", archivo_options)
        if archivo_selection == "nuevo grafo":

            nuevo_grafo()

        if archivo_selection == "Abrir":

            abrir_grafo()

        elif archivo_selection == "Cerrar":
            # cierra la aplicacion
            st.write("Has seleccionado la Sub opción 3")

        if archivo_selection == "Guardar":
            st.write("Has seleccionado la Sub opción 3")
        if archivo_selection == "Guardar como":
            st.write("Has seleccionado la Sub opción 3")

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
            st.write("Has seleccionado la Sub opción 1")


def draw_graph(G):
    nx.draw(G, with_labels=True)
    st.pyplot()


def draw_graph(G, node_color='yellow'):
    nx.draw(G, with_labels=True, node_color=node_color)
    st.pyplot()


def nuevo_grafo():
    st.sidebar.title("Crear nuevo grafo")
    node_id = st.sidebar.text_input("ID del nodo")
    node_label = st.sidebar.text_input("Etiqueta del nodo")
    node_color = st.sidebar.color_picker("Color del nodo")
    add_node_button = st.sidebar.button("Agregar nodo")

    edge_start = st.sidebar.text_input("ID del nodo de inicio de la arista")
    edge_end = st.sidebar.text_input("ID del nodo final de la arista")
    edge_weight = st.sidebar.text_input("Peso de la arista")
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
                source=st.session_state['id_map'][edge_start], target=st.session_state['id_map'][edge_end], label=edge_weight))
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

        for edge in st.session_state['edges']:
            if edge.source == selected_node_id:
                edge.source = st.session_state['id_map'][selected_node_id]
            if edge.to == selected_node_id:
                edge.to = st.session_state['id_map'][selected_node_id]

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


if __name__ == "__main__":
    main()
