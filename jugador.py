from random import randint
from abc import ABC, abstractmethod
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR
import random

class Jugador(ABC):
    @abstractmethod
    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]) -> tuple[str, list[int]]:
        """
        Devuelve una jugada (plantarse o tirar) y los dados a tirar.
        
        Args:
            puntaje_total (int): Puntaje total del jugador en la partida.
            puntaje_turno (int): Puntaje acumulado en el turno del jugador.
            dados (list[int]): Tirada del turno actual.

        Returns:
            tuple[int, list[int]]: Acción a realizar y la lista de dados a tirar.
        """
        # Calcular la cantidad de dados no usados
        cantidad_dados_no_usados = len(dados)

        # Crear la clave para buscar en la política (cantidad de dados no usados, puntaje_turno)
        estado_clave = (cantidad_dados_no_usados, puntaje_turno)

        # Consultar la política para determinar la acción
        if estado_clave in self.politica:
            acciones = self.politica[estado_clave]
            # Tomar la acción con el valor más alto
            accion = max(acciones, key=acciones.get)
        else:
            accion = random.choice(['plantarse', 'tirar']) # Acción por defecto si no se encuentra el estado
            print(f"Estado {estado_clave} no encontrado en la política, usando acción por defecto que es: {accion}.")

        # Realizar la acción correspondiente
        if accion == 'plantarse':
            return ('plantarse', [])
        elif accion == 'tirar':
            # Aquí puedes calcular los dados no usados
            # Si decides tirar, devolver los dados no usados
            puntaje, no_usados = puntaje_y_no_usados(dados)
            return ('tirar', no_usados)
    

class JugadorAleatorio(Jugador):
    def __init__(self, nombre:str):
        self.nombre = nombre
        
    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int],
              verbose:bool=False) -> tuple[int,list[int]]:
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        if randint(0, 1)==0:
            return (JUGADA_PLANTARSE, [])
        else:
            return (JUGADA_TIRAR, no_usados)

class JugadorSiempreSePlanta(Jugador):
    def __init__(self, nombre:str):
        self.nombre = nombre
        
    def jugar(self, puntaje_total:int, puntaje_turno:int, dados:list[int], 
              verbose:bool=False) -> tuple[int,list[int]]:
        return (JUGADA_PLANTARSE, [])
