import json
import pandas as pd
import streamlit as st

from matplotlib import pyplot as plt
import networkx as nx
import os
import io

class GraphExporter:

    @staticmethod
    def exportar_Imagen(grafo, nombre_archivo: str = "grafo", formato: str = "png"):
        if grafo.number_of_nodes() == 0:
            print("El grafo está vacío. Agrega nodos y aristas antes de exportar.")
            st.warning("El grafo está vacío. Agrega nodos y aristas antes de exportar.")
            return

        print("Crea la figura")
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(grafo)
        nx.draw(grafo, pos, with_labels=True, node_color='skyblue', edge_color='gray')
        edge_labels = nx.get_edge_attributes(grafo, 'weight')
        nx.draw_networkx_edge_labels(grafo, pos, edge_labels=edge_labels)
        print("Termina la figura")

        buffer = io.BytesIO()
        plt.savefig(buffer, format=formato, dpi=300)
        plt.close()
        buffer.seek(0)

        print("Descargar imagen ")
        # Nota: La función st.download_button debe ser llamada desde un contexto de Streamlit script.
        st.download_button(
            label="Descargar imagen del grafo",
            data=buffer,
            file_name=f"{nombre_archivo}.{formato}",
            mime=f"image/{formato}"
        )
        print("Termina de Descargar imagen ")
        
    @staticmethod
    def exportar_CSV(nombre_archivo: str, nodes, edges):
        # Crear el DataFrame de nodos
        df_nodes = pd.DataFrame([(node.id, node.label) for node in nodes], columns=['Node', 'Label'])

        # Crear el DataFrame de aristas
        df_edges = pd.DataFrame([(edge.source, edge.to, edge.label) for edge in edges], columns=['Source', 'Target', 'Weight'])

        # Combina ambos DataFrames en un solo CSV usando StringIO para el almacenamiento temporal
        buffer = io.StringIO()
        df_nodes.to_csv(buffer, index=False)
        buffer.write('\n')  # Separador entre nodos y aristas
        df_edges.to_csv(buffer, index=False)
        buffer.seek(0)  # Vuelve al inicio del buffer para la descarga

        # Botón de descarga
        st.download_button(
            label="Descargar CSV",
            data=buffer.getvalue().encode('utf-8'),
            file_name=f"{nombre_archivo}.csv",
            mime="text/csv"
        )

    
    @staticmethod
    def exportar_TXT(nombre_archivo: str, nodes, edges):
        # Preparar el contenido del archivo TXT
        contenido_txt = "Nodos:\n"
        for node in nodes:
            contenido_txt += f"ID: {node.id}, Label: {node.label}\n"

        contenido_txt += "\nAristas:\n"
        for edge in edges:
            contenido_txt += f"De: {edge.source}, A: {edge.to}, Peso/Etiqueta: {edge.label}\n"

        # Convertir el contenido en bytes
        contenido_bytes = contenido_txt.encode('utf-8')

        # Botón de descarga
        st.download_button(
            label="Descargar TXT",
            data=contenido_bytes,
            file_name=f"{nombre_archivo}.txt",
            mime="text/plain"
        )


    @staticmethod
    def exportar_JSON(nombre_archivo: str, nodes, edges):
        # Crear las estructuras de datos para los nodos y las aristas
        nodos_json = [{"id": node.id, "label": node.label} for node in nodes]
        aristas_json = [{"source": edge.source, "target": edge.to, "label": edge.label} for edge in edges]

        # Compilar todo en un diccionario que representa el grafo
        grafo_json = {
            "nodes": nodos_json,
            "edges": aristas_json
        }

        # Convertir el diccionario a una cadena JSON
        contenido_json = json.dumps(grafo_json, indent=4)

        # Botón de descarga
        st.download_button(
            label="Descargar JSON",
            data=contenido_json,
            file_name=f"{nombre_archivo}.json",
            mime="application/json"
        )
