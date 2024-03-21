from streamlit_agraph import Node, Edge
import os
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config
import random
from src.models.GraphExporter import GraphExporter
from src.models.GraphManager import GraphManager

class UIManager:
    
    def __init__(self):
        self.graph_manager = GraphManager()
        self.exporter = GraphExporter()

    def load_css(self):
        with open('styles.css', 'r') as css:
            st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    def run(self):
        # Método para iniciar la aplicación y el menú de Streamlit
        # Aquí iría la lógica para mostrar opciones en la barra lateral, manejar la entrada del usuario,
        # y llamar a los métodos correspondientes en GraphManager y GraphExporter basado en esas entradas.
        self.load_css()

        # Inicializa 'nodes' y 'edges' al principio de este método
        if 'nodes' not in st.session_state:
            st.session_state.nodes = []
        if 'edges' not in st.session_state:
            st.session_state.edges = []

        if st.sidebar.button('Inicio'):
            st.experimental_rerun()

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
            f'<img src="https://www.ucaldas.edu.co/portal/wp-content/uploads/2020/05/monitorias-1.jpg" width="150" class="my-sidebar-image">', unsafe_allow_html=True)

        navbar_selection = st.sidebar.selectbox("Menú", navbar_options)

        if navbar_selection == "Archivo":
            archivo_selection = st.sidebar.selectbox("Opciones", archivo_options)

            if archivo_selection == "nuevo grafo":
                tipo_grafo_options = ["personalizado", "Aleatorio"]
                tipo_grafo = st.sidebar.selectbox(
                    "Tipo de grafo", tipo_grafo_options)
                
                if tipo_grafo == "personalizado":
                    self.graph_manager.nuevo_grafo_personalizado()
                    
                else:
                    tipo_grafo_aleatorio = ["completo",
                                        "dirigido", "ponderado", "random"]
                    tipo_grafoaleatorio_option = st.sidebar.selectbox(
                        "Tipo de grafo aleatorio", tipo_grafo_aleatorio)
                    
                    if tipo_grafoaleatorio_option == "completo":
                        self.graph_manager.grafo_completo()
                        
                    elif tipo_grafoaleatorio_option == "dirigido":
                        self.graph_manager.grafo_dirigido()
                        
                    elif tipo_grafoaleatorio_option == "random":
                        self.graph_manager.nuevo_grafo_aleatorio()
                        

            if archivo_selection == "Abrir":

                self.graph_manager.abrir_grafo()
                
            
            elif archivo_selection == "Salir":
                os._exit(0)

            if archivo_selection == "Guardar":
                self.exporter.guardar_grafo_actual(st.session_state['nodes'], st.session_state['edges'])
                
            if archivo_selection == "Guardar como":
                ruta = './Data/'
                nombreArchivo = 'grafo_exportado.json'
                nombreUsuario = st.text_input("Nombre del archivo", value=nombreArchivo)

                if not nombreUsuario.endswith('.json'):
                    nombreUsuario += '.json'
                    
                nombreCompleto = os.path.join(ruta, nombreUsuario)
                GraphExporter.exportar_JSON(nombreCompleto, st.session_state.nodes, st.session_state.edges)
                
            if archivo_selection == "Exportar datos":
                st.write("Has seleccionado la opción de exportación de datos")
                # Despliegue de opciones para formato de exportación
                export_format = st.selectbox(
                    "Seleccione el formato de exportación:",
                    ["txt", "json", "excel", "imagen"]
                )

                # Botón para ejecutar la exportación en el formato seleccionado
                if st.button('Exportar'):
                    if export_format == 'txt':
                        # Llama a la función de exportación a txt
                        nodes = st.session_state.get('nodes', [])
                        edges = st.session_state.get('edges', [])
                        self.exporter.exportar_TXT("Grafo_TXT", nodes, edges)
                        st.success("Datos exportados a archivo TXT.")

                    elif export_format == 'json':
                        # Llama a la función de exportación a json
                        nodes = st.session_state.get('nodes', [])
                        edges = st.session_state.get('edges', [])
                        self.exporter.exportar_JSON("Grafo_JSON", nodes, edges)
                        st.success("Datos exportados a archivo JSON.")

                    elif export_format == 'excel':
                        nodes = st.session_state.get('nodes', [])
                        edges = st.session_state.get('edges', [])
                        self.exporter.exportar_CSV("Grafo_Excel", nodes, edges)
                        st.success("Datos exportados a archivo Excel.")

                    elif export_format == 'imagen':
                        # Llama a la función de exportación a imagen
                        grafo_actual = self.graph_manager.get_graph()
                        self.exporter.exportar_Imagen(grafo_actual)
                        st.success("Grafo exportado a imagen.")

            if archivo_selection == "Importar datos":
                self.graph_manager.importar_datos()

        elif navbar_selection == "Editar":
            archivo_selection = st.sidebar.selectbox("Opciones", editar_options)
            if archivo_selection == "Deshacer":
                st.write("Has seleccionado la Sub opción 1")
            if archivo_selection == "Nodo":
                self.graph_manager.buscarNodo(st)
            if archivo_selection == "Arco":
                st.write("Has seleccionado la Sub opción arco")

        elif navbar_selection == "Ejecutar":
            archivo_selection = st.sidebar.selectbox("Opciones", ejecutar_options)
            if archivo_selection == "procesos":
                st.write("Has seleccionado la Sub opción 1")

        elif navbar_selection == "Ventana":
            archivo_selection = st.sidebar.selectbox("Opciones", ventana_options)
            if archivo_selection == "Gráfica":
                st.write("Los Datos del grafo en grafica son: ")
            if archivo_selection == "Tabla":
                st.write("Los Datos del grafo en tabla son:")
                self.graph_manager.mostrarGrafoTabla(st.session_state.nodes, st.session_state.edges,st)
                

        elif navbar_selection == "Herramientas":
            st.write("Has seleccionado la Sub opción 1")

        elif navbar_selection == "Ayuda":
            archivo_selection = st.sidebar.selectbox("Opciones", ayuda_options)
            if archivo_selection == "Ayuda":
                st.write("Has seleccionado la Sub opción 1")
            if archivo_selection == "Acerca de Grafos":
                self.graph_manager.acerca_de_grafos()