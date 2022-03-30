import gym
# import numpy as np
import pygame


ANCHO = 1280
ALTO = 700


class Camara:
    def __init__(self, entidad):
        self.entidad = entidad
        self.offset = pygame.Vector2()
        self.offset_float = pygame.Vector2()
        self.limites = pygame.Vector2(-ANCHO/3, -(7*64 - (704-ALTO)))  # 444  # - 700/1.57

    def scroll(self):
        self.offset_float += ((self.entidad.rect.x - self.offset_float.x + self.limites.x) / 16,
                              (self.entidad.rect.y - self.offset_float.y + self.limites.y) / 8)
        self.offset.x = max(0, round(self.offset_float.x))  # Borde izquierdo
        self.offset.y = max(-64, round(self.offset_float.y))  # Borde superior
        self.offset.y = min(0, self.offset.y)  # Borde inferior


class SpatialHash(pygame.sprite.AbstractGroup):
    def draw(self, surface, offset=pygame.Vector2()):
        """draw all sprites onto the surface

        Group.draw(surface): return Rect_list

        Draws all of the member sprites onto the given surface.

        """
        sprites = self.sprites()
        if hasattr(surface, "blits"):
            self.spritedict.update(
                zip(sprites, surface.blits((spr.image,
                                            (spr.rect.x - offset.x, spr.rect.y - offset.y)) for spr in sprites))
            )
        else:
            for spr in sprites:
                self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty


class SpatialHashSingle(pygame.sprite.GroupSingle):
    def draw(self, surface, offset=pygame.Vector2()):
        """draw all sprites onto the surface

        Group.draw(surface): return Rect_list

        Draws all of the member sprites onto the given surface.

        """
        sprites = self.sprites()
        if hasattr(surface, "blits"):
            self.spritedict.update(
                zip(sprites, surface.blits((spr.image,
                                            (spr.rect.x - offset.x, spr.rect.y - offset.y)) for spr in sprites))
            )
        else:
            # print("Estoy pintando en un lugar inesperado!")
            for spr in sprites:
                self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty


class Juego(gym.Env):
    def __init__(self):
        self.nivel = Nivel()
        self.jugador = SpatialHashSingle(Jugador(pygame.Vector2(64, 448), self.nivel))  # 64, 448

        self.camara = None
        self.ventana = None
        self.flag_iniciar_render = True

    def step(self, action):
        # self.nivel.update(action)
        self.jugador.update(action)

    def render(self, mode="human"):
        if self.flag_iniciar_render:
            self.iniciar_render()

        self.ventana.fill('black')

        self.camara.scroll()

        self.nivel.draw(self.ventana, self.camara.offset)
        self.jugador.draw(self.ventana, self.camara.offset)

        # pygame.draw.line(self.ventana, 'red', (ANCHO/2, 0), (ANCHO/2, ALTO))
        # pygame.draw.line(self.ventana, 'red', (ANCHO / 3, 0), (ANCHO / 3, ALTO))

        pygame.display.update()

    def reset(self):
        self.jugador.sprite.reset()

    def iniciar_render(self):
        self.flag_iniciar_render = False

        pygame.init()
        self.ventana = pygame.display.set_mode((1280, 700))
        self.camara = Camara(self.jugador.sprite)


class Nivel:
    def __init__(self):
        self.bloques = SpatialHash()  # pygame.sprite.Group()

        datos_nivel = [
            "                         ",
            "        X              XX",
            "                        X",
            "                XXX     X",
            "            X           X",
            "    XXXXX              X",
            "                     XX",
            "                    X",
            "XXXXX  XXXXX    XXXX",
            "XXX XXXXXXXX  XXXXXX",
            "XX XXXXXXXXX  XXXXXX"
        ]

        datos_nivel = [
            "        X              XX",
            "                        X",
            "                XXX     X",
            "            X           X",
            "    XXXXX              X",
            "                     XX",
            "                    X",
            "XXXXX  XXXX    XX  X",
            "XXX XX         X  XX",
            "XX      XXXX      XX",
            "XXXXXXXXXXXX  XXXXXX"
        ]
        tam_bloque = 64

        for fila_i, fila in enumerate(datos_nivel):
            for col_i, celda in enumerate(fila):
                x = col_i * tam_bloque
                y = fila_i * tam_bloque
                if celda == 'X':
                    self.bloques.add(Bloque(pygame.Vector2(x, y), tam_bloque))
                # elif celda == 'P':
                #     print(x, y)
                #     self.jugador.add(Jugador((x, y)))

        # self.bloques.add(Bloque((0, 0), tam_bloque))
        # self.bloques.add(Bloque((64, 64), tam_bloque))
        # self.bloques.add(Bloque((0, 64), tam_bloque))

    def update(self, accion):
        pass

    def draw(self, ventana, offset):
        self.bloques.draw(ventana, offset)


class Sprite(pygame.sprite.Sprite):
    def __init__(self,
                 pos: pygame.Vector2,
                 dim: tuple,
                 color):
        super().__init__()

        self.image = pygame.Surface(dim)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)  # Pendiente de cámara

        self.pos = pos
        self.activo = True


class Bloque(Sprite):
    def __init__(self, pos: pygame.Vector2, tam):
        super().__init__(pos, (tam, tam), 'grey')


class Entidad(Sprite):
    GRAVEDAD = 0.4
    VELOCIDAD_SALTO = -14  # -14
    VELOCIDAD_DOBLE_SALTO = VELOCIDAD_SALTO * 0.75

    def __init__(self,
                 pos: pygame.Vector2,
                 dim: tuple,
                 color,
                 nivel: Nivel,
                 velocidad: pygame.Vector2 = pygame.Vector2()):
        super().__init__(pos, dim, color)
        self.nivel = nivel
        self.velocidad = velocidad

        self.comprobar_colision_nivel = True
        self.saltando = False
        self.doble_salto = False
        self.cayendo = False

        self.frames_salto = 20
        self.timer_salto = 0

    def mover(self, accion):
        self.velocidad.x = accion[0] * 4  # 4
        self.pos.x += self.velocidad.x
        self.rect.x = round(self.pos.x)

    def saltar(self, accion):
        if accion[1] and (not self.cayendo or self.saltando):
            if not self.saltando:
                self.velocidad.y = self.VELOCIDAD_SALTO
                self.saltando = True
                self.timer_salto = self.frames_salto
            elif not self.doble_salto and not self.timer_salto:
                self.velocidad.y = self.VELOCIDAD_DOBLE_SALTO
                self.doble_salto = True

        # if accion[1] and not self.saltando and not self.cayendo:
        #     self.velocidad.y = self.VELOCIDAD_SALTO
        #     self.saltando = True

    def aplicar_gravedad(self):
        self.velocidad.y += self.GRAVEDAD
        self.pos.y += self.velocidad.y
        self.rect.y = round(self.pos.y)

    def update(self, accion):
        self.mover(accion)
        self.saltar(accion)

        if self.comprobar_colision_nivel:
            self.colision_nivel()

        self.cayendo = round(self.velocidad.y) > 0

        self.actualizar_timers()
        # self.aplicar_gravedad()

        # print(self.saltando, self.doble_salto, self.cayendo, self.timer_salto, self.velocidad.y)

    def actualizar_timers(self):
        if self.timer_salto > 0 and self.saltando:
            self.timer_salto -= 1

    def colision_nivel(self):
        self.colision_nivel_horizontal()
        self.colision_nivel_vertical()

    def colision_nivel_vertical(self):
        self.aplicar_gravedad()

        for bloque in self.nivel.bloques:
            if self.rect.colliderect(bloque.rect):
                if self.velocidad.y > 0:
                    self.rect.bottom = bloque.rect.top
                    self.pos.y = self.rect.y
                    self.velocidad.y = 0
                    self.saltando = False
                    self.doble_salto = False
                elif self.velocidad.y < 0:
                    self.rect.top = bloque.rect.bottom
                    self.pos.y = self.rect.y
                    self.velocidad.y = 0

    def colision_nivel_horizontal(self):
        for bloque in self.nivel.bloques:
            if self.rect.colliderect(bloque.rect):
                if self.velocidad.x > 0:
                    self.rect.right = bloque.rect.left
                    self.pos.x = self.rect.x
                    if self.cayendo and not self.doble_salto:
                        # Fenómeno curioso: esto tiende una velocidad de 0,8
                        # Llego a la conclusión de que un número n dividido entre 2 más un número m
                        # repetidamente tiende a 2m.
                        # n/2 + m -> 2m
                        # Por ejemplo: n/2 + 0,4 -> 0,8
                        self.velocidad.y /= 2
                elif self.velocidad.x < 0:
                    self.rect.left = bloque.rect.right
                    self.pos.x = self.rect.x
                    if self.cayendo and not self.doble_salto:
                        self.velocidad.y /= 2


class Jugador(Entidad):
    def __init__(self, pos: pygame.Vector2, nivel: Nivel):
        super().__init__(pos, (32, 50), 'red', nivel)  # (32, 50)

    def reset(self):
        self.pos.update(64, 448)
        self.velocidad.update(0, 0)

    # def update(self, accion):
    #     super().update(accion)
    #
    #     print(self.pos, self.rect.topleft)
    #     print(f"Cayendo:  {self.cayendo}\n"
    #           f"Saltando: {self.saltando}\n")
