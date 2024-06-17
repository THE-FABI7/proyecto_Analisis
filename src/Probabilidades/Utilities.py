import time

class Utilities:
    @staticmethod
    def medir_tiempo(func):
        def wrapper(*args, **kwargs):
            inicio = time.time()
            resultado = func(*args, **kwargs)
            fin = time.time()
            print(f"Tiempo de ejecución de {func.__name__}: {fin - inicio:.4f} segundos")
            return resultado
        return wrapper