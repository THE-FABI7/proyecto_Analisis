import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config


class NodeManager:
    def __init__(self, graph):
        self.graph = graph
        if 'nodes' not in st.session_state:
            st.session_state['nodes'] = []
        if 'edges' not in st.session_state:
            st.session_state['edges'] = []

    def gestionar_nodos(self):
        with st.sidebar:
            self.agregar_nodo()
            self.editar_nodo()
            self.eliminar_nodo()

    def agregar_nodo(self):
        node_id = st.text_input("ID del nodo", key="add_node_id")
        node_label = st.text_input("Etiqueta del nodo", key="add_node_label")
        node_color = st.color_picker("Color del nodo", key="add_node_color")
        if st.button("Agregar nodo"):
            if node_id and node_label:
                if node_id in [node.id for node in st.session_state['nodes']]:
                    st.error("El ID del nodo ya existe.")
                else:
                    nodo = Node(id=node_id, label=node_label, color=node_color)
                    st.session_state['nodes'].append(nodo)
                    self.graph.add_node(node_id, label=node_label, color=node_color)
                    st.success("Nodo agregado correctamente.")
            else:
                st.error("El ID y la etiqueta del nodo son obligatorios.")
    
    def agregar_nodo2(self, node_id, label, color):
        """Agrega un nodo al grafo con ID, etiqueta y color especificados."""
        if node_id and label:
            if node_id in [node.id for node in st.session_state['nodes']]:
                st.error("El ID del nodo ya existe.")
            else:
                nodo = Node(id=node_id, label=label, color=color)
                st.session_state['nodes'].append(nodo)
                self.graph.add_node(node_id, label=label, color=color)
                st.success("Nodo agregado correctamente.")
        else:
            st.error("El ID y la etiqueta del nodo son obligatorios.")

    def editar_nodo(self):
        if st.session_state['nodes']:
            node_ids = [node.id for node in st.session_state['nodes']]
            selected_node_id = st.selectbox("Seleccionar nodo a editar:", node_ids, key="edit_node_select")
            new_label = st.text_input("Nueva etiqueta:", key="edit_node_label")
            new_color = st.color_picker("Nuevo color:", key="edit_node_color")
            if st.button("Actualizar Nodo", key="update_node"):
                for node in st.session_state['nodes']:
                    if node.id == selected_node_id:
                        node.label = new_label if new_label else node.label
                        node.color = new_color
                        self.graph.nodes[selected_node_id]['label'] = new_label
                        self.graph.nodes[selected_node_id]['color'] = new_color
                        st.success(f"Nodo {selected_node_id} actualizado.")

    def eliminar_nodo(self):
        if st.session_state['nodes']:
            node_ids = [node.id for node in st.session_state['nodes']]
            selected_node_id = st.selectbox("Seleccionar nodo a eliminar:", node_ids, key="delete_node_select")
            if st.button("Eliminar Nodo", key="delete_node"):
                st.session_state['nodes'] = [node for node in st.session_state['nodes'] if node.id != selected_node_id]
                self.graph.remove_node(selected_node_id)
                st.success(f"Nodo {selected_node_id} eliminado.")
