from Data.datapb.NodeDataRetrieve import NodeDataRetriever
import numpy as np
from scipy.stats import wasserstein_distance


class ProbabilityDistribution:
    """
    Clase encargada de generar la distribución de probabilidades de transición entre estados.
    """

    @staticmethod
    def datos_mt():
        """
        Esta función se llama datos_mt y probablemente contenga código relacionado con el manejo o
        procesamiento de datos.
        """
        retriever = NodeDataRetriever()
        data = retriever.get_six_node_data()
        return data

    @staticmethod
    def generar_distribucion_probabilidades(tabla, estado_actual, estado_futuro, num, estados):
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
            # verificar si i tiene "'", si es así, se elimina la comilla
            if "'" in i:
                i = i[:-1]

            nuevaTabla = ProbabilityDistribution.generar_tabla_comparativa(
                tabla[i])
            filtro2 = ProbabilityDistribution.porcentaje_distribucion(
                nuevaTabla, indices, num)
            probabilidades_distribuidas.append(filtro2)

            tabla = ProbabilityDistribution.generar_tabla(
                probabilidades_distribuidas, num)

            tabla[0] = [[estado_futuro, estado_actual]] + tabla[0]
            tabla[1] = [num] + tabla[1]
            return tabla

    def Solucion_estrategia1(matrices, c1, c2, estadoActual, estados):
        tabla = {}
        # Creamos una llave única para la tabla
        key = (tuple(c1), tuple(c2), estadoActual)
        if key not in tabla:
            tabla[key] = ProbabilityDistribution.generar_distribucion_probabilidades(
                matrices, c1, c2, estadoActual, estados)
        return tabla[key]

    @staticmethod
    def generar_tabla(distribucion, num, i=0, num_binario='', nuevo_valor=1):
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
            tabla1 = ProbabilityDistribution.generar_tabla(
                distribucion, num, i + 1, num_binario + '0', nuevo_valor * distribucion[i][1][2])
            tabla2 = ProbabilityDistribution.generar_tabla(
                distribucion, num, i + 1, num_binario + '1', nuevo_valor * distribucion[i][1][1])
            return [tabla1[0] + tabla2[0], tabla1[1] + tabla2[1]]

    @staticmethod
    def porcentaje_distribucion(tabla, indice, num):
        """
        Calcula el porcentaje de distribución de probabilidades.

        Args:
            tabla (list): Tabla de probabilidades.
            indices (list): Lista de índices.
            num (int): Número de nodos.

        Returns:
            list: Nueva tabla de probabilidades.
        """
        tablaNueva = [tabla[0]]
        fila = None
        try:
            tabla1 = [fila for fila in tabla[1:] if all(i < len(num) and pos < len(
                fila[0]) and fila[0][pos] == num[i] for i, pos in enumerate(indice))]
        except IndexError as e:
            print(f"IndexError: {e}")
            raise

        nuevosValores = [0, 0]
        for i in tabla1:
            nuevosValores[0] += i[1]
            nuevosValores[1] += i[2]

        total = sum(nuevosValores)
        nuevosValores = [v / total if total != 0 else v for v in nuevosValores]
        nuevaFila = [num, *nuevosValores]
        tablaNueva.append(nuevaFila)
        return tablaNueva

    @staticmethod
    def generar_tabla_comparativa(diccionario):
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

    @staticmethod
    def calcular_emd(p1, p2):
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

        # Asegúrate de que p1 y p2 sean unidimensionales
        if p1.ndim != 1 or p2.ndim != 1:
            raise ValueError("p1 y p2 deben ser arrays unidimensionales")

        # Ajusta p2 para que tenga la misma longitud que p1
        if len(p1) != len(p2):
            p2 = np.interp(np.linspace(0, 1, len(p1)),
                           np.linspace(0, 1, len(p2)), p2)

        cost_matrix = np.abs(np.subtract.outer(p1, p2))
        salida = np.sum(np.min(cost_matrix, axis=1) * p1)
        return salida

    @staticmethod
    def producto_tensor(p1, p2):
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
        resultado = np.outer(p1, p2).flatten()
        return resultado

    def generarEstadoTransicion(self, subconjuntos):
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def aux(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(
                    subconjuntos[estado][estado_actual_tuple] for estado in estados)
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                aux(i + 1)
                estado_actual[i] = 1
                aux(i + 1)
        aux(0)
        return transiciones, estados
