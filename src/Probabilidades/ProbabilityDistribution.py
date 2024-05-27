from Data.datapb.NodeDataRetrieve import NodeDataRetriever
import numpy as np
from scipy.stats import wasserstein_distance


class ProbabilityDistribution:
    """
    Clase encargada de generar la distribución de probabilidades de transición entre estados.
    """
    
    def datos_mt(self):
        """
        Esta función se llama datos_mt y probablemente contenga código relacionado con el manejo o
        procesamiento de datos.
        """
        data = NodeDataRetriever.get_three_node_data(self)
        return data

    def generar_distribucion_probabilidades(self, tabla, estado_actual, estado_futuro, num, estados):
        """
        Genera la distribución de probabilidades de transición entre estados.

        Args:
            tabla (dict): Diccionario de transiciones.
            estado_actual (list): Estado actual.
            estado_futuro (list): Estado futuro.
            num (int): Número de nodos.
            estados (list): Lista de estados.

        Returns:
            list: Tabla de probabilidades distribuidas.
        """
        indices = [estados.index(i) for i in estado_actual]
        probabilidades_distribuidas = []
        for i in estado_futuro:
            nueva_tabla = ProbabilityDistribution.generar_tabla_comparativa(self,tabla[i])
            filtro2 = ProbabilityDistribution.porcentaje_distribucion(self,nueva_tabla, indices, num)
            probabilidades_distribuidas.append(filtro2)
        tabla = ProbabilityDistribution.generar_tabla(self,probabilidades_distribuidas, num)
        tabla[0] = [f"{estado_actual} | {estado_futuro}"] + tabla[0]
        tabla[1] = [num] + tabla[1]
        return tabla

    def generar_tabla(self, distribucion, num, i=0, num_binario='', nuevo_valor=1):
        """
        Genera una tabla de probabilidades distribuidas.

        Args:
            distribucion (list): Lista de distribuciones.
            num (int): Número de nodos.
            i (int): Índice actual (por defecto 0).
            num_binario (str): Número binario (por defecto '').
            nuevo_valor (int): Nuevo valor (por defecto 1).

        Returns:
            list: Tabla de probabilidades.
        """
        if i == len(distribucion):
            num_binario = '0' * (len(distribucion) -
                                 len(num_binario)) + num_binario
            nuevo_dato = tuple(int(bit) for bit in num_binario)
            return [[nuevo_dato], [nuevo_valor]]
        else:
            tabla1 = ProbabilityDistribution.generar_tabla(self,
                distribucion, num, i + 1, num_binario + '0', nuevo_valor * distribucion[i][1][2])
            tabla2 = ProbabilityDistribution.generar_tabla(self,
                distribucion, num, i + 1, num_binario + '1', nuevo_valor * distribucion[i][1][1])
            return [tabla1[0] + tabla2[0], tabla1[1] + tabla2[1]]

    def porcentaje_distribucion(self, tabla, indices, num):
        """
        Calcula el porcentaje de distribución de probabilidades.

        Args:
            tabla (list): Tabla de probabilidades.
            indices (list): Lista de índices.
            num (int): Número de nodos.

        Returns:
            list: Nueva tabla de probabilidades.
        """
        tabla_nueva = [tabla[0]]
        tabla1 = [fila for fila in tabla if all(i < len(num) and pos < len(
            fila[0]) and fila[0][pos] == num[i] for i, pos in enumerate(indices))]
        nuevos_valores = [0, 0]
        for i in tabla1:
            nuevos_valores[0] += i[1]
            nuevos_valores[1] += i[2]
        nuevos_valores = [v / len(tabla1) for v in nuevos_valores]
        nueva_fila = [num, *nuevos_valores]
        tabla_nueva.append(nueva_fila)
        return tabla_nueva

    def generar_tabla_comparativa(self, diccionario):
        """
        Genera una tabla comparativa a partir de un diccionario.

        Args:
            diccionario (dict): Diccionario de probabilidades.

        Returns:
            list: Lista de probabilidades comparativas.
        """
        lista = [['key', (1,), (0,)]]
        for k, v in diccionario.items():
            lista.append([k, v, 1 - v])
        return lista

    def calcular_emd(self, p1, p2):
        """
        Calcula la diferencia de probabilidad utilizando Earth Mover's Distance (EMD).

        Args:
            p1 (list): Primera partición de probabilidades.
            p2 (list): Segunda partición de probabilidades.

        Returns:
            list: Diferencias de probabilidad.
        """
        p1 = np.array(p1)
        p2 = np.array(p2)
        diferencias = [wasserstein_distance(p1, p2_row) for p2_row in p2]
        return diferencias

    def producto_tensor(self, p1, p2):
        """
        Calcula el producto tensor de dos particiones de probabilidades.

        Args:
            p1 (list): Primera partición de probabilidades.
            p2 (list): Segunda partición de probabilidades.

        Returns:
            np.ndarray: Producto tensor de las particiones de probabilidades.
        """
        p1 = np.array(p1)
        p2 = np.array(p2)
        resultado = np.outer(p1, p2)
        return resultado
