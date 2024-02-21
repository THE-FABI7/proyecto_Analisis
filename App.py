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
    edge_weight = st.sidebar.number_input("Peso de la arista", min_value=0)
    add_edge_button = st.sidebar.button("Agregar arista")

    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
    if 'edges' not in st.session_state:
        st.session_state['edges'] = []

    if add_node_button:
        st.session_state['nodes'].append(
            Node(id=node_id, label=node_label, color=node_color, font={"color":"white"}))

    if add_edge_button:
        node_ids = [node.id for node in st.session_state['nodes']]
        if edge_start in node_ids and edge_end in node_ids:
            st.session_state['edges'].append(
                Edge(source=edge_start, target=edge_end))
        else:
            st.error(
                "Los nodos de inicio y fin deben existir antes de agregar una arista.")

    config = Config(width=500, height=500, directed=False,
                    nodeHighlightBehavior=True)
    agraph(nodes=st.session_state['nodes'],
           edges=st.session_state['edges'], config=config)


def abrir_grafo():
    uploaded_file = st.file_uploader(
        "Elige un archivo .json", type="json")
    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name,
                        "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)
        json_data = json.load(uploaded_file)
        G = nx.Graph()
        for node in json_data['graph'][0]['data']:
            G.add_node(node['id'], label=node['label'], type=node['type'],
                       radius=node['radius'], coordenates=node['coordenates'])
            for linked_node in node['linkedTo']:
                G.add_edge(node['id'], linked_node['nodeId'],
                           weight=linked_node['weight'])
        draw_graph(G)


if __name__ == "__main__":
    main()
