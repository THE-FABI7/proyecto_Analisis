from Data.datapb.NodeDataRetrieve import NodeDataRetriever
import numpy as np
from scipy.stats import wasserstein_distance
import pandas as pd

class ProbabilityDistribution:
    """
    Clase encargada de generar la distribución de probabilidades de transición entre estados.
    """

    def datos_mt(self):
        """
        Obtiene los datos de transición entre nodos.

        Returns:
            dict: Diccionario de datos de transición.
        """
        retriever = NodeDataRetriever()
        return retriever.get_five_node_data()

    def tabla_distribucion_probabilidades(self, matrices, estado_actual, estado_futuro, num, estados):
        """
        Genera una tabla de distribución de probabilidades.

        Args:
            matrices (dict): Diccionario de matrices de datos.
            estado_actual (list): Lista de estados actuales.
            estado_futuro (list): Lista de estados futuros.
            num (int): Número de nodos.
            estados (list): Lista de todos los estados posibles.

        Returns:
            list: Tabla de distribución de probabilidades.
        """
        indices = [estados.index(i) for i in estado_actual]
        prob_distribuidas = []

        for estado in estado_futuro:
            estado = estado.rstrip("'")
            nueva_tabla = self.crear_tabla_comparativa(matrices[estado])
            filtro = self.porcentajes_distribuciones(nueva_tabla, indices, num)
            prob_distribuidas.append(filtro)

        tabla = self.crear_tabla(prob_distribuidas, num)
        tabla[0] = [[estado_futuro, estado_actual]] + tabla[0]
        tabla[1] = [num] + tabla[1]
        return tabla
        
    def crear_tabla(self, distribucion, num, i=0, binario='', nuevo_valor=1):
        """
        Genera una tabla de probabilidades distribuidas.

        Args:
            distribucion (list): Lista de distribuciones.
            num (int): Número de nodos.
            i (int): Índice actual (por defecto 0).
            binario (str): Número binario (por defecto '').
            nuevo_valor (int): Nuevo valor (por defecto 1).

        Returns:
            list: Tabla de probabilidades.
        """
        if i == len(distribucion):
            binario = binario.zfill(len(distribucion))
            nuevo_dato = tuple(int(bit) for bit in binario)
            return [[nuevo_dato], [nuevo_valor]]
        else:
            tabla1 = self.crear_tabla(distribucion, num, i+1, binario+'0', nuevo_valor*distribucion[i][1][2])
            tabla2 = self.crear_tabla(distribucion, num, i+1, binario+'1', nuevo_valor*distribucion[i][1][1])
            return [tabla1[0]+tabla2[0], tabla1[1]+tabla2[1]]
        
    def porcentajes_distribuciones(self, tabla, indices, num):
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
        fila = [fila for fila in tabla[1:] if all(i < len(num) and pos < len(fila[0]) and fila[0][pos] == num[i] for i, pos in enumerate(indices))]
        
        nuevos_valores = [sum(fila[i] for fila in fila) for i in [1, 2]]
        total = sum(nuevos_valores)
        nuevos_valores = [v / total if total != 0 else v for v in nuevos_valores]
        
        fila_nueva = [num, *nuevos_valores]
        tabla_nueva.append(fila_nueva)
        return tabla_nueva
    
    def crear_tabla_comparativa(self, diccionario):
        """
        Genera una tabla comparativa a partir de un diccionario.

        Args:
            diccionario (dict): Diccionario de probabilidades.

        Returns:
            list: Lista de probabilidades comparativas.
        """
        return [['key', (1,), (0,)]] + [[k, v, 1 - v] for k, v in diccionario.items()]

    def calcular_emd(self, p1, p2):
        """
        Calcula la diferencia de probabilidad utilizando Earth Mover's Distance (EMD).

        Args:
            p1 (list): Primera partición de probabilidades.
            p2 (np.ndarray): Producto tensor de las particiones de probabilidades.

        Returns:
            float: Diferencia de probabilidad.
        """
        p1, p2 = np.array(p1), np.array(p2)

        if p1.ndim != 1 or p2.ndim != 1:
            raise ValueError("p1 y p2 deben ser arrays unidimensionales")

        if len(p1) != len(p2):
            p2 = np.interp(np.linspace(0, 1, len(p1)), np.linspace(0, 1, len(p2)), p2)
        
        cost_matrix = np.abs(np.subtract.outer(p1, p2))
        return np.sum(np.min(cost_matrix, axis=1) * p1)

    def producto_tensor(self, p1, p2):
        """
        Calcula el producto tensor de dos particiones de probabilidades.

        Args:
            p1 (list): Primera partición de probabilidades.
            p2 (list): Segunda partición de probabilidades.

        Returns:
            np.ndarray: Producto tensor de las particiones de probabilidades.
        """
        return np.outer(p1, p2).flatten()
    
    def retornar_candidatos(self):
        """
        Retorna los estados del sistema.

        Returns:
            list: Lista de estados.
        """
        datos = self.datos_mt()
        _, estados = self.crear_estados_transicion(datos)
        return estados
    
    def crear_estados_transicion(self, subconjuntos):
        """
        Crea las transiciones entre estados.

        Args:
            subconjuntos (dict): Diccionario de subconjuntos.

        Returns:
            tuple: Diccionario de transiciones y lista de estados.
        """
        estados = list(subconjuntos.keys())
        transiciones = {}
        estado_actual = [0] * len(estados)

        def aux(i):
            if i == len(estados):
                estado_actual_tuple = tuple(estado_actual)
                estado_futuro = tuple(subconjuntos[estado][estado_actual_tuple] for estado in estados)
                transiciones[estado_actual_tuple] = estado_futuro
            else:
                estado_actual[i] = 0
                aux(i + 1)
                estado_actual[i] = 1
                aux(i + 1)
        aux(0)
        return transiciones, estados
    
    def retornar_futuros(self):
        """
        Retorna los estados futuros del sistema.

        Returns:
            list: Lista de estados futuros.
        """
        datos = self.datos_mt()
        _, estados = self.crear_estados_transicion(datos)
        return [estado + "'" for estado in estados]
    
    def retornar_estados(self):
        """
        Retorna los estados del sistema.

        Returns:
            list: Lista de estados.
        """
        datos = self.datos_mt()
        _, estados = self.crear_estados_transicion(datos)
        return estados

    def retornar_valor_actual(self, c1, c2):
        datos = self.datos_mt()
        lista = []
        if len(c1) == 1:
            lista.append((0,))
            lista.append((1,))
        elif len(c1) == 2:
            lista.append((0, 0))
            lista.append((0, 1))
            lista.append((1, 0))
            lista.append((1, 1))

        elif len(c1) == 3:
            lista.append((0, 0, 0))
            lista.append((0, 0, 1))
            lista.append((0, 1, 0))
            lista.append((0, 1, 1))
            lista.append((1, 0, 0))
            lista.append((1, 0, 1))
            lista.append((1, 1, 0))
            lista.append((1, 1, 1)
                            )
        elif len(c1) == 4:
            lista.append((0, 0, 0, 0))
            lista.append((0, 0, 0, 1))
            lista.append((0, 0, 1, 0))
            lista.append((0, 0, 1, 1))
            lista.append((0, 1, 0, 0))
            lista.append((0, 1, 0, 1))
            lista.append((0, 1, 1, 0))
            lista.append((0, 1, 1, 1))
            lista.append((1, 0, 0, 0))
            lista.append((1, 0, 0, 1))
            lista.append((1, 0, 1, 0))
            lista.append((1, 0, 1, 1))
            lista.append((1, 1, 0, 0))
            lista.append((1, 1, 0, 1))
            lista.append((1, 1, 1, 0))
            lista.append((1, 1, 1, 1))

        elif len(c1) == 5:
            lista.append((0, 0, 0, 0, 0))
            lista.append((0, 0, 0, 0, 1))
            lista.append((0, 0, 0, 1, 0))
            lista.append((0, 0, 0, 1, 1))
            lista.append((0, 0, 1, 0, 0))
            lista.append((0, 0, 1, 0, 1))
            lista.append((0, 0, 1, 1, 0))
            lista.append((0, 0, 1, 1, 1))
            lista.append((0, 1, 0, 0, 0))
            lista.append((0, 1, 0, 0, 1))
            lista.append((0, 1, 0, 1, 0))
            lista.append((0, 1, 0, 1, 1))
            lista.append((0, 1, 1, 0, 0))
            lista.append((0, 1, 1, 0, 1))
            lista.append((0, 1, 1, 1, 0))
            lista.append((0, 1, 1, 1, 1))
            lista.append((1, 0, 0, 0, 0))
            lista.append((1, 0, 0, 0, 1))
            lista.append((1, 0, 0, 1, 0))
            lista.append((1, 0, 0, 1, 1))
            lista.append((1, 0, 1, 0, 0))
            lista.append((1, 0, 1, 0, 1))
            lista.append((1, 0, 1, 1, 0))
            lista.append((1, 0, 1, 1, 1))
            lista.append((1, 1, 0, 0, 0))
            lista.append((1, 1, 0, 0, 1))
            lista.append((1, 1, 0, 1, 0))
            lista.append((1, 1, 0, 1, 1))
            lista.append((1, 1, 1, 0, 0))
            lista.append((1, 1, 1, 0, 1))
            lista.append((1, 1, 1, 1, 0))
            lista.append((1, 1, 1, 1, 1))

        elif len(c1) == 6:
            lista.append((0, 0, 0, 0, 0, 0))
            lista.append((0, 0, 0, 0, 0, 1))
            lista.append((0, 0, 0, 0, 1, 0))
            lista.append((0, 0, 0, 0, 1, 1))
            lista.append((0, 0, 0, 1, 0, 0))
            lista.append((0, 0, 0, 1, 0, 1))
            lista.append((0, 0, 0, 1, 1, 0))
            lista.append((0, 0, 0, 1, 1, 1))
            lista.append((0, 0, 1, 0, 0, 0))
            lista.append((0, 0, 1, 0, 0, 1))
            lista.append((0, 0, 1, 0, 1, 0))
            lista.append((0, 0, 1, 0, 1, 1))
            lista.append((0, 0, 1, 1, 0, 0))
            lista.append((0, 0, 1, 1, 0, 1))
            lista.append((0, 0, 1, 1, 1, 0))
            lista.append((0, 0, 1, 1, 1, 1))
            lista.append((0, 1, 0, 0, 0, 0))
            lista.append((0, 1, 0, 0, 0, 1))
            lista.append((0, 1, 0, 0, 1, 0))
            lista.append((0, 1, 0, 0, 1, 1))
            lista.append((0, 1, 0, 1, 0, 0))
            lista.append((0, 1, 0, 1, 0, 1))
            lista.append((0, 1, 0, 1, 1, 0))
            lista.append((0, 1, 0, 1, 1, 1))
            lista.append((0, 1, 1, 0, 0, 0))
            lista.append((0, 1, 1, 0, 0, 1))
            lista.append((0, 1, 1, 0, 1, 0))
            lista.append((0, 1, 1, 0, 1, 1))
            lista.append((0, 1, 1, 1, 0, 0))
            lista.append((0, 1, 1, 1, 0, 1))
            lista.append((0, 1, 1, 1, 1, 0))
            lista.append((0, 1, 1, 1, 1, 1))
            lista.append((1, 0, 0, 0, 0, 0))
            lista.append((1, 0, 0, 0, 0, 1))
            lista.append((1, 0, 0, 0, 1, 0))
            lista.append((1, 0, 0, 0, 1, 1))
            lista.append((1, 0, 0, 1, 0, 0))
            lista.append((1, 0, 0, 1, 0, 1))
            lista.append((1, 0, 0, 1, 1, 0))
            lista.append((1, 0, 0, 1, 1, 1))
            lista.append((1, 0, 1, 0, 0, 0))
            lista.append((1, 0, 1, 0, 0, 1))
            lista.append((1, 0, 1, 0, 1, 0))
            lista.append((1, 0, 1, 0, 1, 1))
            lista.append((1, 0, 1, 1, 0, 0))
            lista.append((1, 0, 1, 1, 0, 1))
            lista.append((1, 0, 1, 1, 1, 0))
            lista.append((1, 0, 1, 1, 1, 1))
            lista.append((1, 1, 0, 0, 0, 0))
            lista.append((1, 1, 0, 0, 0, 1))
            lista.append((1, 1, 0, 0, 1, 0))
            lista.append((1, 1, 0, 0, 1, 1))
            lista.append((1, 1, 0, 1, 0, 0))
            lista.append((1, 1, 0, 1, 0, 1))
            lista.append((1, 1, 0, 1, 1, 0))
            lista.append((1, 1, 0, 1, 1, 1))
            lista.append((1, 1, 1, 0, 0, 0))
            lista.append((1, 1, 1, 0, 0, 1))
            lista.append((1, 1, 1, 0, 1, 0))
            lista.append((1, 1, 1, 0, 1, 1))
            lista.append((1, 1, 1, 1, 0, 0))
            lista.append((1, 1, 1, 1, 0, 1))
            lista.append((1, 1, 1, 1, 1, 0))
            lista.append((1, 1, 1, 1, 1, 1))
        else:
            for k, v in datos.items():
                for k2, v2 in v.items():
                    lista.append(k2)
                break
        return lista
    
    def retornar_distribucion(self, estado_actual, estado_futuro, valor_actual):
        """
        Retorna la distribución de probabilidades para los estados actuales y futuros.

        Args:
            estado_actual (list): Estado actual.
            estado_futuro (list): Estado futuro.
            valor_actual (tuple): Valor actual.

        Returns:
            DataFrame: DataFrame con la distribución de probabilidades.
        """
        matrices = self.datos_mt()
        _, estados = self.crear_estados_transicion(matrices)
        datos = self.tabla_distribucion_probabilidades(matrices, estado_actual, estado_futuro, valor_actual, estados)
        
        columnas = [str(datos[0][0])]
        columnas.extend([str(col) for col in datos[0][1:]])

        return pd.DataFrame(datos[1:], columns=columnas)
