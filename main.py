import numpy as np
import pygame.time

from plataformas import *


def manejar_eventos(eventos):
    for evento in eventos:
        if evento.type == pygame.QUIT:
            return 1
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            return 2
    return 0


def manejar_entrada(teclas):
    accion_mover = 0
    accion_saltar = 0
    accion_disparar = 0
    accion_dash = 0

    if teclas[pygame.KSCAN_SPACE] or teclas[pygame.KSCAN_UP] or teclas[pygame.KSCAN_W]:
        accion_saltar = 1
    if teclas[pygame.KSCAN_B]:
        accion_dash = 1
    if teclas[pygame.KSCAN_N]:
        accion_disparar = 1
    if teclas[pygame.KSCAN_M]:
        accion_disparar = -1
    if teclas[pygame.KSCAN_LEFT] or teclas[pygame.KSCAN_A]:
        accion_mover += -1
    if teclas[pygame.KSCAN_RIGHT] or teclas[pygame.KSCAN_D]:
        accion_mover += 1
    return [accion_mover, accion_saltar, accion_disparar, accion_dash]


def leer_acciones():
    acciones = []
    with open("acciones.txt") as f:
        for x in f.readline().strip().split("], ["):
            l = []
            for e in x.replace("[", "").replace("]", "").split(", "):
                l.append(int(e))
            acciones.append(l)
    print(acciones)
    return acciones


def main():
    pygame.init()
    clock = pygame.time.Clock()
    juego = Juego()
    juego.juega_humano = True
    # juego.inicializar_render()

    flag_grabacion = True
    acciones = []
    if not flag_grabacion:
        acciones = leer_acciones()

    milisegundos = 0
    frames = 0

    while True:
        evento = manejar_eventos(pygame.event.get())
        if evento == 1:
            break
        elif evento == 2:
            juego.reset()

        if flag_grabacion:
            accion = manejar_entrada(list(pygame.key.get_pressed()))
            # acciones.append(accion)
        else:
            if len(acciones) > 0:
                accion = acciones.pop(0)
            else:
                accion = [0, 0, 0, 0]
                print("¡REPRODUCCIÓN FINALIZADA!")
                acciones = leer_acciones()
                clock.tick(1)
                juego.reset()

        # lista = list(pygame.key.get_pressed())
        # if True in lista:
        #     print(lista.index(True))

        # Acción random
        # accion = [np.random.randint(-1, 2), np.random.randint(0, 2),
        #           np.random.randint(-1, 2), np.random.randint(0, 2)]

        juego.step(accion)
        juego.render()

        if juego.done:
            juego.reset()

        clock.tick(60)

        # frames += 1
        # milisegundos += max(1, clock.tick(60))
        #
        # if milisegundos >= 1000:
        #     print(frames)
        #     milisegundos = 0
        #     frames = 0

    # if flag_grabacion:
    #     with open(f"acciones{juego.nivel.semilla}.txt", 'w') as f:
    #         f.write(str(acciones))
    #     print(acciones)


if __name__ == "__main__":
    main()
