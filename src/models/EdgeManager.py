import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

class EdgeManager:
    def __init__(self, graph):
        self.graph = graph
        if 'nodes' not in st.session_state:
            st.session_state['nodes'] = []
        if 'edges' not in st.session_state:
            st.session_state['edges'] = []
        
    def gestionar_aristas(self):
        with st.sidebar:
            st.header("Gestionar Aristas")
            source_node_id = st.selectbox("Nodo de inicio", [node.id for node in st.session_state.nodes], key="edge_start")
            target_node_id = st.selectbox("Nodo de destino", [node.id for node in st.session_state.nodes], key="edge_end")
            weight = st.number_input("Peso", min_value=1, max_value=1000, key="edge_weight")
            edge_color = st.color_picker("Color de la arista", key="edge_color")

            if st.button("Agregar Arista", key="add_edge"):
                nueva_arista = Edge(source=source_node_id, target=target_node_id, weight=weight, label=str(weight), width=3, color=edge_color)
                st.session_state.edges.append(nueva_arista)
                self.graph.add_edge(source_node_id, target_node_id, weight=weight, color=edge_color)
                st.success("Arista agregada correctamente.")

            # Usa st.session_state para controlar qué se muestra
            if 'editing_edge' not in st.session_state:
                st.session_state.editing_edge = False
            if 'deleting_edge' not in st.session_state:
                st.session_state.deleting_edge = False

            if st.button("Editar Arista", key="start_edit_edge"):
                st.session_state.editing_edge = True
                st.session_state.deleting_edge = False

            if st.button("Eliminar Arista", key="start_delete_edge"):
                st.session_state.deleting_edge = True
                st.session_state.editing_edge = False

            # Controla el flujo de la interfaz de usuario según el estado
            if st.session_state.editing_edge:
                self.editarArista()
            elif st.session_state.deleting_edge:
                self.eliminarArista()

    def eliminarArista(self):
        with st.sidebar:
            edge_options = [f"{edge.source} -> {edge.to}" for edge in st.session_state.edges]
            edge_to_delete = st.selectbox("Seleccionar arista para eliminar", edge_options, key="delete_edge_select")
            delete_edge_button = st.button("Eliminar arista", key="delete_edge")

            if delete_edge_button:
                edge_index = edge_options.index(edge_to_delete)
                selected_edge = st.session_state.edges.pop(edge_index)
                self.graph.remove_edge(selected_edge.source, selected_edge.target)
                st.success(f"Arista {selected_edge.source} -> {selected_edge.target} eliminada.")
    
    def editarArista(self):
        with st.sidebar:
            print("Entra a editar arista")
            if 'selected_edge_index' not in st.session_state:
                st.session_state['selected_edge_index'] = 0

            edge_options = [(edge.source, edge.to) for edge in st.session_state['edges']]
            edge_index = st.selectbox(
                "Seleccionar arista para editar", 
                range(len(edge_options)),
                format_func=lambda x: f"{edge_options[x][0]} -> {edge_options[x][1]}",
                key="select_edge_to_edit"  # Clave única para este selectbox
            )

            st.session_state['selected_edge_index'] = edge_index

            new_weight = st.number_input(
                "Nuevo Peso", 
                min_value=1, 
                max_value=1000, 
                key=f"new_weight_{edge_index}"  # Clave única basada en el índice de la arista
            )
            new_color = st.color_picker(
                "Nuevo color de la arista", 
                key=f"new_color_{edge_index}"  # Clave única basada en el índice de la arista
            )

            # Define `update_key` aquí para usarlo en el botón de actualizar.
            update_key = f"update_edge_{edge_index}"
            if st.button("Actualizar Arista", key=update_key):  # Clave única para el botón
                print("Entra en la condicion")
                selected_edge = st.session_state['edges'][edge_index]
                selected_edge.label = str(new_weight)
                selected_edge.weight = new_weight  # Asegúrate de que la clase Edge tenga este atributo.
                selected_edge.color = new_color
        
                # Actualizar el grafo de networkx con los nuevos valores
                self.graph[selected_edge.source][selected_edge.to]['weight'] = new_weight
                self.graph[selected_edge.source][selected_edge.to]['color'] = new_color
        
                st.success(f"Arista {selected_edge.source} -> {selected_edge.to} actualizada correctamente.")
                #self.redibujar_grafo()
        
    def redibujar_grafo(self):
        print("Redubuja el grafo")
        nodes = st.session_state['nodes']
        edges = st.session_state['edges']
        config = Config(width=900, height=900, directed=False, nodeHighlightBehavior=True, physics=False)
        agraph(nodes=nodes, edges=edges, config=config)

    def eliminarArista(self):
        with st.sidebar:
            # Asegurarse de que 'edges' está inicializado en st.session_state
            if 'edges' not in st.session_state:
                st.session_state['edges'] = []

            edge_options = [f"{edge.source} -> {edge.to}" for edge in st.session_state.edges]
        
            if edge_options:
                # Seleccionar arista a "eliminar" (cambiar visualmente)
                selected_index = st.selectbox(
                    "Seleccionar arista para eliminar", 
                    range(len(edge_options)),
                    format_func=lambda x: edge_options[x],
                    key="delete_edge_select"
                )

                if st.button("Marcar arista como eliminada", key="delete_edge_button"): 
                    # Encuentra la arista seleccionada basándose en el índice
                    selected_edge = st.session_state.edges[selected_index]
    
                    # Cambiar visualmente la arista seleccionada para indicar que ha sido "eliminada"
                    selected_edge.dashes = True
                    # Aquí cambiamos el color a gris y agregamos "(eliminada)" a la etiqueta
                    selected_edge.color = "#CCCCCC"  # Usar un color gris
                    # selected_edge.label += "(el)"  # Añadir nota a la etiqueta
                
                    st.success(f"Arista {selected_edge.source} -> {selected_edge.to} marcada como eliminada.")

            else:
                st.warning("No hay aristas para eliminar.")
