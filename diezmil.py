from random import randint
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR
from jugador import Jugador, JugadorAleatorio, JugadorSiempreSePlanta

class JuegoDiezMil:
    def __init__(self, jugador: Jugador):
        self.jugador: Jugador = jugador

    def jugar(self, verbose:bool=False, tope_turnos:int=1000) -> tuple[int,int]:
        ''' Juega un juego de 10mil para un jugador, hasta terminar o hasta 
            llegar a tope_turnos turnos. Devuelve la cantidad de turnos que
            necesitó y el puntaje final.
        '''
        turno: int = 0
        puntaje_total: int = 0
        while puntaje_total < 10000 and turno < tope_turnos:
            # Nuevo turno
            turno += 1
            puntaje_turno: int = 0
            msg: str = 'turno ' + str(turno) + ':'

            # Un turno siempre empieza tirando los 6 dados.
            jugada: str = 'tirar'
            dados_a_tirar: list[int] = [1, 2, 3, 4, 5, 6]
            fin_de_turno: bool = False

            while not fin_de_turno:
                # Tira los dados que correspondan y calcula su puntaje.
                dados: list[int] = [randint(1, 6) for _ in range(len(dados_a_tirar))]
                (puntaje_tirada, _) = puntaje_y_no_usados(dados)
                msg += ' ' + ''.join(map(str, dados)) + ' '

                if puntaje_tirada == 0:  
                    # Mala suerte, no suma nada. Pierde el turno.
                    fin_de_turno = True
                    puntaje_turno = 0

                else:
                    # Bien, suma puntos. Preguntamos al jugador qué quiere hacer.
                    jugada, dados_a_tirar = self.jugador.jugar(puntaje_total, puntaje_turno, dados)

                    if jugada == 'plantarse':
                        msg += 'P'
                        fin_de_turno = True
                        puntaje_turno += puntaje_tirada

                    elif jugada == 'tirar':
                        dados_a_separar = separar(dados, dados_a_tirar)
                        assert len(dados_a_separar) + len(dados_a_tirar) == len(dados)
                        puntaje_tirada, dados_no_usados = puntaje_y_no_usados(dados_a_separar)
                        assert puntaje_tirada > 0 and len(dados_no_usados) == 0
                        puntaje_turno += puntaje_tirada
                        # Cuando usó todos los dados, vuelve a tirar todo.
                        if len(dados_a_tirar) == 0:
                            dados_a_tirar = [1, 2, 3, 4, 5, 6]
                        msg += 'T(' + ''.join(map(str, dados_a_tirar)) + ') '

            puntaje_total += puntaje_turno
            msg += ' --> ' + str(puntaje_turno) + ' puntos. TOTAL: ' + str(puntaje_total)
            if verbose: print(msg)
        return (turno, puntaje_total)


def main():
    num_juegos = 1000
    
    # Jugador Aleatorio
    jugador_aleatorio = JugadorAleatorio('random')
    juego_aleatorio = JuegoDiezMil(jugador_aleatorio)
    
    total_turnos_aleatorio = 0
    total_puntaje_aleatorio = 0
    
    for _ in range(num_juegos):
        (cantidad_turnos, puntaje_final) = juego_aleatorio.jugar(verbose=False)
        total_turnos_aleatorio += cantidad_turnos
        total_puntaje_aleatorio += puntaje_final
    
    promedio_turnos_aleatorio = total_turnos_aleatorio / num_juegos
    promedio_puntaje_aleatorio = total_puntaje_aleatorio / num_juegos
    
    print(f"{jugador_aleatorio.nombre} - Promedio de turnos: {promedio_turnos_aleatorio}, Promedio de puntaje: {promedio_puntaje_aleatorio}")
    
    # Jugador Siempre Se Planta
    jugador_planton = JugadorSiempreSePlanta('plantón')
    juego_planton = JuegoDiezMil(jugador_planton)
    
    total_turnos_planton = 0
    total_puntaje_planton = 0
    
    for _ in range(num_juegos):
        (cantidad_turnos, puntaje_final) = juego_planton.jugar(verbose=False)
        total_turnos_planton += cantidad_turnos
        total_puntaje_planton += puntaje_final
    
    promedio_turnos_planton = total_turnos_planton / num_juegos
    promedio_puntaje_planton = total_puntaje_planton / num_juegos
    
    print(f"{jugador_planton.nombre} - Promedio de turnos: {promedio_turnos_planton}, Promedio de puntaje: {promedio_puntaje_planton}")

if __name__ == '__main__':
    main()
    