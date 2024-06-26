from Probabilidades.Estrategia02 import Estrategia02
from Probabilidades.Estrategia import Estrategia
from streamlit_agraph import Node, Edge
import os
import streamlit as st
import json
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_agraph import agraph, Node, Edge, Config
import random
from src.models.GraphExporter import GraphExporter
from src.models.GraphManager import GraphManager
from src.models.NodeManager import NodeManager
from src.models.EdgeManager import EdgeManager
from src.Probabilidades.ProbabilityDistribution import ProbabilityDistribution


class UIManager:

    def __init__(self):
        self.graph_manager = GraphManager()
        graph = self.graph_manager.get_graph()
        self.exporter = GraphExporter()
        self.node_manager = NodeManager(graph)
        self.edge_manager = EdgeManager(graph)
        if 'nodosG1' not in st.session_state:
            st.session_state.nodosG1 = []
        if 'nodosG2' not in st.session_state:
            st.session_state.nodosG2 = []
        if 'estado_actual' not in st.session_state:
            st.session_state.estado_actual = None
        if 'aux' not in st.session_state:
            st.session_state.aux = None
        if 'candidatos' not in st.session_state:
            st.session_state.candidatos = []
        self.prob_dist = ProbabilityDistribution()
        self.estrategia2 = Estrategia02()
        self.estrategia = Estrategia()

    def load_css(self):
        with open('styles.css', 'r') as css:
            st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    def display_graph(self, graph):
        if graph is not None and len(graph.nodes) > 0:
            # Intenta obtener la etiqueta de cada nodo y asigna una predeterminada si no existe
            nodes = [Node(id=str(n), label=graph.nodes[n].get(
                'label', f'Node {n}')) for n in graph.nodes()]
            edges = [Edge(source=str(u), target=str(v), label=str(
                graph.edges[u, v].get('weight', 1))) for u, v in graph.edges()]
            agraph(nodes=nodes, edges=edges,
                   config=Config(width=800, height=600))
            st.session_state.show_graph = False
        else:
            # Aquí puedes manejar el caso en el que el grafo es nulo o está vacío
            st.error("No hay un grafo para mostrar.")

    def run(self):
        # Método para iniciar la aplicación y el menú de Streamlit
        # Aquí iría la lógica para mostrar opciones en la barra lateral, manejar la entrada del usuario,
        # y llamar a los métodos correspondientes en GraphManager y GraphExporter basado en esas entradas.
        # Cargar estilos CSS y otras inicializaciones
        self.load_css()
        self.initialize_state()
        self.handle_sidebar()

    def initialize_state(self):
        # Inicializar los nodos y aristas si aún no están en st.session_state
        if 'nodes' not in st.session_state:
            st.session_state['nodes'] = []
        if 'edges' not in st.session_state:
            st.session_state['edges'] = []
        if 'graph' not in st.session_state:
            st.session_state['graph'] = None
        if 'show_graph' not in st.session_state:
            st.session_state.show_graph = False
        if 'graph_updated' not in st.session_state:
            st.session_state.graph_updated = False

    def handle_sidebar(self):
        if st.sidebar.button('Inicio'):
            st.experimental_rerun()

        navbar_options = ["Archivo", "Editar", "Ejecutar",
                          "Herramientas", "Ventana", "Ayuda"]
        archivo_options = ["nuevo grafo", "Abrir", "Cerrar", "Guardar",
                           "Guardar como", "Exportar datos", "Importar datos", "Salir"]
        editar_options = ["Deshacer", "Arco", "Nodo"]
        ejecutar_options = ["procesos", "Estrategia 1", "Estrategia 2"]
        ventana_options = ["Gráfica", "Tabla"]
        ayuda_options = ["Ayuda", "Acerca de Grafos"]
        # Usa un archivo de imagen y muéstralo en el encabezado de la barra lateral usando st.image.
        st.sidebar.markdown(
            f'<img src="https://www.ucaldas.edu.co/portal/wp-content/uploads/2020/05/monitorias-1.jpg" width="150" class="my-sidebar-image">', unsafe_allow_html=True)

        navbar_selection = st.sidebar.selectbox("Menú", navbar_options)

        if navbar_selection == "Archivo":
            archivo_selection = st.sidebar.selectbox(
                "Opciones", archivo_options)

            if archivo_selection == "nuevo grafo":

                self.handle_new_graph()

            if archivo_selection == "Abrir":

                self.graph_manager.abrir_grafo()

            elif archivo_selection == "Salir":
                os._exit(0)

            if archivo_selection == "Guardar":
                self.exporter.guardar_grafo_actual(
                    st.session_state['nodes'], st.session_state['edges'])

            if archivo_selection == "Guardar como":
                ruta = './Data/'
                nombreArchivo = 'grafo_exportado.json'
                nombreUsuario = st.text_input(
                    "Nombre del archivo", value=nombreArchivo)

                if not nombreUsuario.endswith('.json'):
                    nombreUsuario += '.json'

                nombreCompleto = os.path.join(ruta, nombreUsuario)
                GraphExporter.exportar_JSON(
                    nombreCompleto, st.session_state.nodes, st.session_state.edges)

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
            archivo_selection = st.sidebar.selectbox(
                "Opciones", editar_options)
            if archivo_selection == "Deshacer":
                st.write("Has seleccionado la Sub opción 1")
            if archivo_selection == "Nodo":
                st.sidebar.header("Nodos Edit")
                self.node_manager.agregar_nodo()
                self.node_manager.editar_nodo(st)
                self.node_manager.buscarNodo(st)
                self.node_manager.eliminar_nodo(st)
                self.graph_manager.buscarNodo(st)
            if archivo_selection == "Arco":
                st.sidebar.header("Arco edit")
                self.edge_manager.gestionar_aristas()
                self.edge_manager.editarArista()
                self.edge_manager.eliminarArista()
                
        
            
        elif navbar_selection == "Ejecutar":
            archivo_selection = st.sidebar.selectbox(
                "Opciones", ejecutar_options)
            if archivo_selection == "procesos":
                st.write("Has seleccionado la Sub opción de procesos")
                selected_sub_option = st.selectbox(
                    "Seleccionar un proceso:",
                    ["¿El grafo es bipartito?",
                        "¿El grafo es bipartito conexo ó disconexo?"]
                )
                if selected_sub_option == "¿El grafo es bipartito?":
                    if self.graph_manager.esBipartito(st.session_state.nodes, st.session_state.edges):
                        st.text("El grafo es bipartito")
                    else:
                        st.text("El grafo no es bipartito")
                elif selected_sub_option == "¿El grafo es bipartito conexo ó disconexo?":
                    salida = self.graph_manager.esBipartitoConexoOdisconexo(
                        st.session_state.nodes, st.session_state.edges)
                    st.text(salida)

            if archivo_selection == "Estrategia 1":
                st.write("Has seleccionado la opción de Estrategia 1")
                st.title("Simulador de Transiciones de Estado")
                st.sidebar.header("Configuración de Estados Actuales")

                st.write("## Inicio Estrategia")

                estados_presentes = st.multiselect("Seleccione los estados presentes", self.prob_dist.retornar_estados())
                estados_futuros = st.multiselect("Seleccione los estados futuros", self.prob_dist.retornar_futuros())
                estado_actual = st.selectbox("Seleccione el estado actual", self.prob_dist.retornar_valor_actual(estados_presentes, estados_futuros))
                
                st.session_state.nodes, st.session_state.edges = self.graph_manager.generar_grafoBipartito(estados_presentes, estados_futuros, Node, Edge)
                
                st.write("Nodos del estado presente después del filtro:", estados_presentes)
                                        
                nodosG2_filtrados = [i[:-1] if "'" in i else i for i in estados_futuros]

                if st.button("Solucionar"):
                    st.session_state.aux = self.estrategia.retornar_distribuciones(estados_presentes, nodosG2_filtrados, estado_actual, st)

                nodosG1_str = ', '.join(estados_presentes)
                nodosG2_filtrados_str = ', '.join(nodosG2_filtrados)
                st.latex(r'P(\{' + nodosG2_filtrados_str + r'\}^{t+1} | \{' + nodosG1_str + r'\}^{t})')
                
                st.header("Distribución de probabilidad")
                if st.session_state.aux is not None:
                    st.write(st.session_state.aux)

                st.header("Particiones del grafo")
                particiones_grafo, particiones = self.estrategia.crear_particiones(estados_presentes, estados_futuros, estado_actual)
                st.write(particiones_grafo)

                st.header("Mejor partición del grafo")
                particion_adecuada, d, lista = self.estrategia.retornar_particion_adecuada(estados_presentes, nodosG2_filtrados, estado_actual)
                st.write(str(particion_adecuada), d)
                
                self.estrategia.dibujar_grafo(estados_presentes, nodosG2_filtrados, estado_actual, st.session_state.nodes, st.session_state.edges, st)

            if archivo_selection == "Estrategia 2":
                estados_presentes = st.multiselect("Seleccione los estados presentes", self.prob_dist.retornar_estados())
                estados_futuros = st.multiselect("Seleccione los estados futuros", self.prob_dist.retornar_futuros())
                estado_actual = st.selectbox("Seleccione el estado actual", self.prob_dist.retornar_valor_actual(estados_presentes, estados_futuros))
                st.session_state.nodes, st.session_state.edges = self.graph_manager.generar_grafoBipartito(estados_presentes, estados_futuros, Node, Edge)

                aux3 =[]
                for i in estados_futuros:
                    # verificar si el dato tiene ' al final por ejemplo "1'"
                    if "'" in i:
                        aux3.append(i[:-1])
                if st.button("Calcular segunda estrategia"):
                    st.header("Mejor particion estrategia 2")
                    particionn, diferencia, lista,l = self.estrategia2.estrategia2(estados_presentes, estados_futuros, estado_actual, st.session_state.edges)
                    st.write(str(particionn), diferencia)
                    st.header("Distribuciones del grafo")
                    st.session_state.aux = self.estrategia.retornar_distribuciones(estados_presentes, estados_futuros, estado_actual, st)
                    if st.session_state.aux is not None:
                        st.write(st.session_state.aux)
                    st.header("Particiones del grafo")
                    df, particiones  = self.estrategia2.crear_particiones(estados_presentes, estados_futuros, estado_actual, st.session_state.edges)
                    #self.estrategia2.pintarGrafoGenerado(estados_presentes, estados_futuros,estadoActual, st.session_state.nodes, st.session_state.edges,Node, Edge)
                    st.write(df)
                    

        elif navbar_selection == "Ventana":
            archivo_selection = st.sidebar.selectbox(
                "Opciones", ventana_options)
            if archivo_selection == "Gráfica":
                st.write("Los Datos del grafo en grafica son: ")
            if archivo_selection == "Tabla":
                st.write("Los Datos del grafo en tabla son:")
                self.graph_manager.mostrarGrafoTabla(
                    st.session_state.nodes, st.session_state.edges, st)

        elif navbar_selection == "Herramientas":
            st.write("Has seleccionado la Sub opción 1")

        elif navbar_selection == "Ayuda":
            archivo_selection = st.sidebar.selectbox("Opciones", ayuda_options)
            if archivo_selection == "Ayuda":
                st.write("Has seleccionado la Sub opción 1")
            if archivo_selection == "Acerca de Grafos":
                self.graph_manager.acerca_de_grafos()

    def handle_new_graph(self):
        tipo_grafo_options = ["personalizado", "Aleatorio", "Bipartito"]
        tipo_grafo = st.sidebar.selectbox("Tipo de grafo", tipo_grafo_options)

        if tipo_grafo == 'Aleatorio':
            tipo_grafo_aleatorio = ["completo",
                                    "dirigido", "ponderado", "random"]
            tipo_grafoaleatorio_option = st.sidebar.selectbox(
                "Tipo de grafo aleatorio", tipo_grafo_aleatorio)

            if tipo_grafoaleatorio_option == "completo":
                nodes, edges = self.graph_manager.grafo_completo()
                if nodes is not None and edges is not None:
                    self.display_graph(st.session_state.graph)

            elif tipo_grafoaleatorio_option == "dirigido":
                nodes, edges = self.graph_manager.grafo_dirigido()
                if nodes is not None and edges is not None:
                    self.display_graph(st.session_state.graph)

            elif tipo_grafoaleatorio_option == "random":
                self.graph_manager.nuevo_grafo_aleatorio()

        if tipo_grafo == "personalizado":
            self.graph_manager.nuevo_grafo_personalizado2(st)

        elif tipo_grafo == 'Bipartito':
            numNodosGrupo1 = st.sidebar.number_input(
                "Número de nodos en Grupo 1", min_value=1, value=5)
            numNodosGrupo2 = st.sidebar.number_input(
                "Número de nodos en Grupo 2", min_value=1, value=5)

            # Llamando a la función para crear un grafo bipartito
            self.graph_manager.GrafoBipartito(numNodosGrupo1, numNodosGrupo2)
            # Guarda el nuevo grafo en el estado de la sesión y lo muestra
            st.session_state['graph'] = self.graph_manager.get_graph()
            self.display_graph(st.session_state['graph'])
