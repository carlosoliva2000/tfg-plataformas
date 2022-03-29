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
    accion_saltar = 0
    accion_mover = 0
    if teclas[pygame.KSCAN_SPACE] or teclas[pygame.KSCAN_UP] or teclas[pygame.KSCAN_W]:
        accion_saltar = 1
    if teclas[pygame.KSCAN_LEFT] or teclas[pygame.KSCAN_A]:
        accion_mover += -1
    if teclas[pygame.KSCAN_RIGHT] or teclas[pygame.KSCAN_D]:
        accion_mover += 1
    return [accion_mover, accion_saltar]


pygame.init()
clock = pygame.time.Clock()
juego = Juego()
# juego.inicializar_render()

while True:
    evento = manejar_eventos(pygame.event.get())
    if evento == 1:
        break
    elif evento == 2:
        juego.reset()

    accion = manejar_entrada(list(pygame.key.get_pressed()))

    # lista = list(pygame.key.get_pressed())
    # if True in lista:
    #     print(lista.index(True))

    # Acción random
    # accion = [np.random.randint(-1, 2), np.random.randint(0, 2)]

    juego.step(accion)
    juego.render()
    clock.tick(60)
