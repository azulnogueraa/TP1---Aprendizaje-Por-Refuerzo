import numpy as np
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR, JUGADAS_STR
from collections import defaultdict
from tqdm import tqdm
from jugador import Jugador

class AmbienteDiezMil:
    
    def __init__(self):
        """Definir las variables de instancia de un ambiente.
        ¿Qué es propio de un ambiente de 10.000?
        """
        self.estado = EstadoDiezMil()
        self.puntaje_total = 0  # ESTO NO LO HACE ESTADODIEZMIL() ???
        self.puntaje_turno = 0  # ESTO NO LO HACE ESTADODIEZMIL() ???

    def reset(self):
        """Reinicia el ambiente para volver a realizar un episodio.
        """
        self.estado = EstadoDiezMil()
        self.puntaje_total = 0 # esto no deberia seguir siendo el mismo ???
        self.puntaje_turno = 0
        return self.estado

    def step(self, accion):
        """Dada una acción devuelve una recompensa.
        El estado es modificado acorde a la acción y su interacción con el ambiente.
        Podría ser útil devolver si terminó o no el turno.
        Args:
            accion: Acción elegida por un agente.

        Returns:
            tuple[int, bool]: Una recompensa y un flag que indica si terminó el turno. 

        Si la acción es plantarse, suma el puntaje del turno al total, 
        reinicia el turno y devuelve la recompensa (el puntaje del turno) y True (indicando que el turno ha terminado).
        """
    
        if accion == JUGADA_PLANTARSE:
            recompensa = self.puntaje_turno # CAMBIAR
            self.puntaje_total += self.puntaje_turno
            self.puntaje_turno = 0 #Esto no lo hace fin_turno() ????
            self.estado.fin_turno()
            return recompensa, True
        

        # Si la acción es tirar, genera nuevos dados y calcula el puntaje.
        dados = [np.random.randint(1, 7) for _ in range(6 - len(self.estado.dados_usados))]
        puntaje, no_usados = puntaje_y_no_usados(dados)

        if puntaje == 0:
            recompensa = -self.puntaje_turno  # CAMBIAR LA PENALIZACION 
            self.puntaje_turno = 0
            self.estado.fin_turno()
            return recompensa, True


        # Si se obtienen puntos, se actualiza el estado y se devuelve el puntaje como recompensa.
        self.puntaje_turno += puntaje
        self.estado.actualizar_estado(dados, no_usados, puntaje)
        return puntaje, False

class EstadoDiezMil:
    def __init__(self):
        """Definir qué hace a un estado de diez mil.
        Recordar que la complejidad del estado repercute en la complejidad de la tabla del agente de q-learning.
        """
        self.puntaje_total = 0
        self.puntaje_turno = 0
        self.dados_usados = []
        self.ultima_tirada = []

    def actualizar_estado(self, dados, no_usados, puntaje) -> None:
        """Modifica las variables internas del estado luego de una tirada.

        Args:
            ... (_type_): _description_
            ... (_type_): _description_
        """
        self.ultima_tirada = dados
        self.puntaje_turno += puntaje
        self.dados_usados.extend([d for d in dados if d not in no_usados])
    
    def fin_turno(self):
        """Modifica el estado al terminar el turno.
        """
        self.puntaje_total += self.puntaje_turno
        self.puntaje_turno = 0
        self.dados_usados = []
        self.ultima_tirada = []

    def __str__(self):
        """Representación en texto de EstadoDiezMil.
        Ayuda a tener una versión legible del objeto.

        Returns:
            str: Representación en texto de EstadoDiezMil.
        """
        return f"Puntaje Total:{self.puntaje_total},Puntaje Turno:{self.puntaje_turno},Dados Usados:{len(self.dados_usados)}"

class AgenteQLearning:
    def __init__(
        self,
        ambiente: AmbienteDiezMil,
        alpha: float,
        gamma: float,
        epsilon: float,
        *args,
        **kwargs
    ):
        """Definir las variables internas de un Agente que implementa el algoritmo de Q-Learning.

        Args:
            ambiente (AmbienteDiezMil): Ambiente con el que interactuará el agente.
            alpha (float): Tasa de aprendizaje.
            gamma (float): Factor de descuento.
            epsilon (float): Probabilidad de explorar.
        """

        self.ambiente = ambiente
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 0.1
        self.q_table = defaultdict(lambda: np.zeros(2))

    def elegir_accion(self, estado): #ESTADO COMO PARAMETRO?
        """Selecciona una acción de acuerdo a una política ε-greedy.
        """
 
        if np.random.random() < self.epsilon:
            return np.random.choice([JUGADA_PLANTARSE, JUGADA_TIRAR])
        return np.argmax(self.q_table[str(estado)])

    def entrenar(self, episodios: int, verbose: bool = False) -> None:
        """Dada una cantidad de episodios, se repite el ciclo del algoritmo de Q-learning.
        Recomendación: usar tqdm para observar el progreso en los episodios.

        Args:
            episodios (int): Cantidad de episodios a iterar.
            verbose (bool, optional): Flag para hacer visible qué ocurre en cada paso. Defaults to False.
        """
        for _ in tqdm(range(episodios)):
            estado = self.ambiente.reset()
            terminado = False
            
            while not terminado:
                accion = self.elegir_accion(estado)
                recompensa, terminado = self.ambiente.step(accion)
                nuevo_estado = self.ambiente.estado
                
                mejor_siguiente_q = np.max(self.q_table[str(nuevo_estado)])
                self.q_table[str(estado)][accion] += self.alpha * (
                    recompensa + self.gamma * mejor_siguiente_q - self.q_table[str(estado)][accion])
                
                estado = nuevo_estado

    def guardar_politica(self, filename: str):
        """Almacena la política del agente en un formato conveniente.
        Args:
            filename (str): Nombre/Path del archivo a generar.
        """
        with open(filename, 'w') as f:
            for estado, valores in self.q_table.items():
                f.write(f"{estado},{valores[0]},{valores[1]}\n")

class JugadorEntrenado(Jugador):
    def __init__(self, nombre: str, filename_politica: str):
        self.nombre = nombre
        self.politica = self._leer_politica(filename_politica)
        
    def _leer_politica(self, filename:str, SEP:str=','):
        """Carga una politica entrenada con un agente de RL, que está guardada
        en el archivo filename en un formato conveniente.

        Args:
            filename (str): Nombre/Path del archivo que contiene a una política almacenada. 
        """

        politica = {}
        with open(filename, 'r') as f:
            for linea in f:
                estado, q_plantarse, q_tirar = linea.strip().split(SEP)
                politica[estado] = [float(q_plantarse), float(q_tirar)]
        return politica
    

    def jugar(
        self,
        puntaje_total:int,
        puntaje_turno:int,
        dados:list[int],
    ) -> tuple[int,list[int]]:
        
        """Devuelve una jugada y los dados a tirar.

        Args:
            puntaje_total (int): Puntaje total del jugador en la partida.
            puntaje_turno (int): Puntaje en el turno del jugador
            dados (list[int]): Tirada del turno.

        Returns:
            tuple[int,list[int]]: Una jugada y la lista de dados a tirar.
        """
        puntaje, no_usados = puntaje_y_no_usados(dados)
        estado = EstadoDiezMil()
        estado.puntaje_total = puntaje_total
        estado.puntaje_turno = puntaje_turno
        estado.ultima_tirada = dados
        
        # jugada = self.politica[estado]
        jugada = np.argmax(self.politica.get(str(estado), [0, 0]))

        if jugada == JUGADA_PLANTARSE:
            return (JUGADA_PLANTARSE, [])
        elif jugada == JUGADA_TIRAR:
            return (JUGADA_TIRAR, no_usados)
       

      