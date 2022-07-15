import gym
import numpy as np
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


class Juego(gym.Env):
    def __init__(self):
        self.nivel = Nivel()
        self.jugador = SpatialHashSingle(Jugador(pygame.Vector2(64, 398), self.nivel, self))  # 64, 448
        self.disparos_jugador = SpatialHash()
        self.enemigos = SpatialHash()
        self.enemigos.add(EnemigoDeambulante(pygame.Vector2(64*12, 0), self.nivel, self))
        self.enemigos.add(EnemigoSaltarin(pygame.Vector2(64 * 14 + 32, -64*40), self.nivel, self))
        self.enemigos.add(EnemigoTirador(pygame.Vector2(64 * 24 + 32, -64 * 40), self.nivel, self))

        self.camara = None
        self.ventana = None
        self.flag_iniciar_render = True

    def step(self, action):
        self.nivel.update(self.jugador.sprite.pos.x)
        self.jugador.update(action)
        self.disparos_jugador.update()
        self.enemigos.update()

        if not self.jugador.sprite.activo:
            self.reset()

    def render(self, mode="human"):
        if self.flag_iniciar_render:
            self.iniciar_render()

        self.ventana.fill('black')

        self.camara.scroll()

        self.disparos_jugador.draw(self.ventana, self.camara.offset)
        self.nivel.draw(self.ventana, self.camara.offset)
        if self.jugador.sprite.activo:
            self.jugador.draw(self.ventana, self.camara.offset)
            for r in self.jugador.sprite.rayos:
                r.render(self.ventana, self.camara.offset)
        self.enemigos.draw(self.ventana, self.camara.offset)

        # pygame.draw.line(self.ventana, 'red', (ANCHO/2, 0), (ANCHO/2, ALTO))
        # pygame.draw.line(self.ventana, 'red', (ANCHO / 3, 0), (ANCHO / 3, ALTO))

        pygame.display.update()

    def reset(self):
        self.nivel.reset()
        self.jugador.sprite.reset()
        self.disparos_jugador.empty()
        self.enemigos.empty()
        self.enemigos.add(EnemigoDeambulante(pygame.Vector2(64*12, 0), self.nivel, self))
        self.enemigos.add(EnemigoSaltarin(pygame.Vector2(64 * 14 + 32, -64*40), self.nivel, self))
        self.enemigos.add(EnemigoTirador(pygame.Vector2(64 * 24 + 32, -64 * 40), self.nivel, self))

    def iniciar_render(self):
        self.flag_iniciar_render = False

        pygame.init()
        self.ventana = pygame.display.set_mode((1280, 700))
        self.camara = Camara(self.jugador.sprite)


class Nivel:
    def __init__(self):
        self.bloques = SpatialHash()  # pygame.sprite.Group()
        self.monedas = SpatialHash()

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
            "        X    ...       XX.",
            "             ...       .X.",
            "                XXX     X",
            "     ...    X           X",
            "    XXXXX              X",
            "             .       XX",
            "             .      X",
            "XXXXX  XXXX    XX  X",
            "XXX.XX         X  XX",
            "XX      XXXX.     XX",
            "XXXXXXXXXXXX. XXXXXX"
        ]

        datos_nivel = [
            "        X    ...       XX.",
            "             ...       .X.",
            "X               XXX     X",
            "X    ...    X           X",
            " X  XXXXX              X",
            "  X          .       XX",
            "   X         .      X",
            "XXXXX  XXXX  XXXXXXX",
            "XXX.XX      X  X  XX",
            "XX      XXXX.     XX",
            "XXXXXXXXXXXX. XXXXXX"
        ]

        tam_bloque = 64

        # for fila_i, fila in enumerate(datos_nivel):
        #     for col_i, celda in enumerate(fila):
        #         x = col_i * tam_bloque
        #         y = fila_i * tam_bloque
        #         if celda == 'X':
        #             self.bloques.add(Bloque(pygame.Vector2(x, y), tam_bloque+1))  # tam+1 para evitar huecos de 1 px
        #         elif celda == '.':
        #             self.monedas.add(Moneda(pygame.Vector2(x+tam_bloque/2-Moneda.TAM/2, y+tam_bloque/2-Moneda.TAM/2)))
        #         # elif celda == 'P':
        #         #     print(x, y)
        #         #     self.jugador.add(Jugador((x, y)))

        self.ultima_x = 0
        self.step_generacion = 10 * tam_bloque

        self.generar_nivel()

        self.datos_nivel = datos_nivel
        self.tam_bloque = tam_bloque

        # self.bloques.add(Bloque((0, 0), tam_bloque))
        # self.bloques.add(Bloque((64, 64), tam_bloque))
        # self.bloques.add(Bloque((0, 64), tam_bloque))

    def generar_nivel(self):
        tam_bloque = 64
        y_min, y_max = 0, 10
        y_actual = 8
        for x in range(self.ultima_x, self.ultima_x + self.step_generacion + 1, tam_bloque):
            # x = x * tam_bloque
            y_actual = np.clip(np.random.randint(y_actual-1, y_actual+2), y_min, y_max)  # 8 * tam_bloque
            self.bloques.add(Bloque(pygame.Vector2(x, y_actual*tam_bloque), tam_bloque+1))
        self.ultima_x += self.step_generacion

    def update(self, x_jugador):
        # print(self.ultima_x)
        # pass
        if self.ultima_x - x_jugador < 64 * 14:
            self.generar_nivel()
            if len(self.bloques) > 60:
                for i, b in enumerate(self.bloques):
                    if i < 20:
                        self.bloques.remove(b)
                    else:
                        break

    def reset(self):
        self.monedas.empty()
        datos_nivel = self.datos_nivel
        tam_bloque = self.tam_bloque

        for fila_i, fila in enumerate(datos_nivel):
            for col_i, celda in enumerate(fila):
                if celda == '.':
                    x = col_i * tam_bloque
                    y = fila_i * tam_bloque
                    self.monedas.add(Moneda(pygame.Vector2(x+tam_bloque/2-Moneda.TAM/2, y+tam_bloque/2-Moneda.TAM/2)))

    def draw(self, ventana, offset):
        self.bloques.draw(ventana, offset)
        self.monedas.draw(ventana, offset)


class Sprite(pygame.sprite.Sprite):
    def __init__(self,
                 pos: pygame.Vector2,
                 dim: tuple,
                 color):
        super().__init__()

        self.image = pygame.Surface(dim)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

        self.pos = pos
        self.activo = True

    def kill(self) -> None:
        super().kill()
        self.activo = False

    def reset(self):
        self.activo = True


class Bloque(Sprite):
    COLOR = 'grey'

    def __init__(self, pos: pygame.Vector2, tam):
        super().__init__(pos, (tam, tam), self.COLOR)


class Moneda(Sprite):
    TAM = 16
    DIMENSION = (TAM, TAM)
    COLOR = 'yellow'

    def __init__(self, pos: pygame.Vector2):
        super().__init__(pos, self.DIMENSION, self.COLOR)


class Entidad(Sprite):
    GRAVEDAD = 0.4
    VELOCIDAD_SALTO = -7

    def __init__(self,
                 pos: pygame.Vector2,
                 dim: tuple,
                 color,
                 orientacion: int,
                 nivel: Nivel,
                 juego: Juego,
                 velocidad_x=4,
                 accion_por_defecto=None):
        super().__init__(pos, dim, color)
        self.nivel = nivel
        self.juego = juego
        self.velocidad = pygame.Vector2()
        self.velocidad_x = velocidad_x
        self.accion_por_defecto = accion_por_defecto

        # Inputs de accciones
        self.input_mover = 0
        self.input_saltar = 0

        # Acción que realiza una Entidad en un instante
        self.accion = None

        # Indica la orientación horizontal, 1 si mira hacia la derecha o -1 si mira hacia la izquierda
        self.orientacion = orientacion

        # Le afecta la gravedad, por lo que cae en función de la velocidad cada actualización
        self.afectado_por_gravedad = True

        # Flag que indica si hay colisión horizontal en esta actualización
        self.flag_colision_horizontal = False

        # Flag que indica si hay colisión vertical en esta actualización
        self.flag_colision_vertical = False

        # Indica si la entidad se encuentra apoyada en el suelo
        self.en_suelo = False

        # Indica si la entidad ha colisionado alguna vez con otro sprite, ayudando a la detección del flag anterior
        self.ha_colisionado = False

        # Indica si la entidad debería comprobar colisiones horizontales
        self.comprobar_colisiones_horizontales = True

        # Indica si la entidad debería comprobar colisiones verticales
        self.comprobar_colisiones_verticales = True

        # Indica si el sistema de detección de colisiones es discreto (True) o contínuo (False) (POR IMPLEMENTAR)
        self.deteccion_colisiones_discreta = True

        # Indica si la entidad está realizando un salto
        self.saltando = False

        # Indica si la entidad está cayendo (preferible a consultar velocidad.y)
        self.cayendo = False

        # Indica si existe alguna animación activa en este instante
        self.animacion_activa = False

        self.cooldown_salto = 20

        self.timer_salto = 0

    def update(self, accion=None):
        if self.activo:
            self.seleccionar_accion(accion)
            accion = self.accion

            self.manejar_input_acciones(accion)
            self.aplicar_acciones()
            self.actualizar_flags()
            self.actualizar_timers()
            self.resolver_flags_y_timers()
            self.actualizar_animacion()
            self.log()

    def seleccionar_accion(self, accion):
        if accion:
            self.accion = accion
        elif self.accion_por_defecto:
            self.accion = self.accion_por_defecto
        else:
            # IA de los enemigos (determinar acción según la situación)
            self.accion = self.determinar_accion()

    def determinar_accion(self):
        return self.accion

    def manejar_input_acciones(self, accion):
        self.input_mover = accion[0]
        self.input_saltar = accion[1]

    def aplicar_acciones(self):
        self.aplicar_movimiento_horizontal()
        self.pos.x += self.velocidad.x
        self.rect.x = round(self.pos.x)
        if self.comprobar_colisiones_horizontales:
            self.calcular_colisiones_horizontales()

        self.aplicar_movimiento_vertical()
        self.pos.y += self.velocidad.y
        self.rect.y = round(self.pos.y)
        if self.comprobar_colisiones_verticales:
            self.calcular_colisiones_verticales()

    def actualizar_flags(self):
        self.cayendo = round(self.velocidad.y) > 0
        self.ha_colisionado = (self.ha_colisionado or
                               self.flag_colision_horizontal or self.flag_colision_vertical)

        # Si la gravedad no afecta y se produce una colisión horizontal, producirá falsos positivos
        if self.ha_colisionado:
            self.en_suelo = not self.cayendo and not self.saltando
        else:
            self.en_suelo = False

    def actualizar_timers(self):
        if self.timer_salto > 0 and self.saltando:
            self.timer_salto -= 1

    def resolver_flags_y_timers(self):
        pass

    def actualizar_animacion(self):
        pass

    def log(self):
        pass

    def aplicar_movimiento_horizontal(self):
        self.mover()

    def aplicar_movimiento_vertical(self):
        self.saltar()
        if self.afectado_por_gravedad:
            self.aplicar_gravedad()

    def mover(self):
        accion = self.input_mover
        if not self.animacion_activa:
            if accion:
                self.orientacion = 1 if accion == 1 else -1
            self.velocidad.x = accion * self.velocidad_x

    def saltar(self):
        accion = self.input_saltar
        if accion and self.en_suelo:
            self.velocidad.y = self.VELOCIDAD_SALTO
            self.saltando = True
            self.timer_salto = self.cooldown_salto

    def aplicar_gravedad(self):
        self.velocidad.y += self.GRAVEDAD

    def calcular_colisiones_horizontales(self):
        colisiones = 0
        for bloque in self.nivel.bloques:
            if self.rect.colliderect(bloque.rect):
                colisiones += 1
                self.en_colision_horizontal(bloque, self.velocidad.x)

            self.flag_colision_horizontal = colisiones > 0

    def calcular_colisiones_verticales(self):
        colisiones = 0
        for bloque in self.nivel.bloques:
            if self.rect.colliderect(bloque.rect):
                colisiones += 1
                self.en_colision_vertical(bloque, self.velocidad.y)

        self.flag_colision_vertical = colisiones > 0

    def en_colision_horizontal(self, obj, vx):
        if self.velocidad.x > 0:
            self.rect.right = obj.rect.left
        elif self.velocidad.x < 0:
            self.rect.left = obj.rect.right

        self.pos.x = self.rect.x

    def en_colision_vertical(self, obj, vy):
        if self.velocidad.y > 0:
            self.rect.bottom = obj.rect.top
            self.saltando = False
        elif self.velocidad.y < 0:
            self.rect.top = obj.rect.bottom

        self.pos.y = self.rect.y
        self.velocidad.y = 0
        # if self.velocidad.y > 0:
        #     self.rect.bottom = bloque.rect.top
        #     self.pos.y = self.rect.y
        #     self.velocidad.y = 0
        #     self.saltando = False
        #     self.doble_salto = False
        # elif self.velocidad.y < 0:
        #     self.rect.top = bloque.rect.bottom
        #     self.pos.y = self.rect.y
        #     self.velocidad.y = 0


class Tirador(Entidad):
    def __init__(self, pos: pygame.Vector2, dim: tuple, color, orientacion: int, nivel: Nivel, juego: Juego, vel_x):
        super().__init__(pos, dim, color, orientacion, nivel, juego, vel_x)

        self.input_disparar = 0

        self.cooldown_disparo = 20
        self.timer_disparo = 0

    def manejar_input_acciones(self, accion):
        super().manejar_input_acciones(accion)
        self.input_disparar = accion[2]

    def aplicar_acciones(self):
        super().aplicar_acciones()
        self.disparar()

    def actualizar_timers(self):
        super().actualizar_timers()
        if self.timer_disparo > 0:
            self.timer_disparo -= 1

    def disparar(self):
        accion = self.input_disparar
        if accion and self.timer_disparo == 0:
            # print("PUM")
            self.timer_disparo = self.cooldown_disparo
            self.juego.disparos_jugador.add(Disparo(self.pos.copy(), self.orientacion, self.groups()[0],
                                                    self.nivel, self.juego))


class Jugador(Tirador):
    DIMENSION = (32, 50)
    COLOR = 'red'
    ORIENTACION_INICIAL = 1
    VELOCIDAD_SALTO = -14  # -14
    VELOCIDAD_DOBLE_SALTO = int(VELOCIDAD_SALTO * 0.75)
    VELOCIDAD_X = 4

    def __init__(self, pos: pygame.Vector2, nivel: Nivel, juego: Juego):
        super().__init__(pos, self.DIMENSION, self.COLOR, self.ORIENTACION_INICIAL, nivel, juego, self.VELOCIDAD_X)

        # Inputs de accciones
        self.input_dash = 0

        # Indica si la entidad está realizando un doble salto
        self.doble_salto = False

        # Indica si la animación de dash se ha iniciado
        self.dash_iniciado = False

        # Indica si la animación de dash ha finalizado
        self.dash_finalizado = False

        self.cooldown_dash = 60*1
        # TODO: ajustar duración y velocidad de dash. Es muy corto y mantiene demasiada inercia
        self.duracion_dash = 10  # 10

        self.timer_cooldown_dash = 0
        self.timer_duracion_dash = 0

        self.rayos = [Rayo(self, ang) for ang in np.linspace(0, 2*np.pi, 17)]
        # self.rayos.extend([Rayo(self, ang) for ang in np.linspace(-np.pi/2, np.pi/2, 19)])
        # self.rayos.extend([Rayo(self, ang) for ang in np.linspace(3*np.pi/2, np.pi/2, 19)])
        # self.rayos = [Rayo(self, ang) for ang in np.linspace(-np.pi/2, np.pi/2, 9)]

    def kill(self) -> None:
        self.activo = False

    def reset(self):
        super().reset()
        self.pos.update(64, 398)
        self.orientacion = 1
        self.velocidad.update(0, 0)
        self.ha_colisionado = False
        self.dash_iniciado = False
        self.dash_finalizado = False
        self.animacion_activa = False

    def update(self, accion=None):
        super().update(accion)
        if self.pos.y > 1000:
            self.kill()
        for r in self.rayos:
            r.actualizar()

    def manejar_input_acciones(self, accion):
        super().manejar_input_acciones(accion)
        self.input_dash = accion[3]

    def actualizar_timers(self):
        super().actualizar_timers()
        if self.timer_cooldown_dash > 0:
            self.timer_cooldown_dash -= 1

        if self.timer_duracion_dash > 0:
            self.timer_duracion_dash -= 1
            if self.timer_duracion_dash == 0:
                self.dash_finalizado = True

    def resolver_flags_y_timers(self):
        if self.flag_colision_horizontal and self.cayendo and not self.doble_salto:
            # Fenómeno curioso: esto tiende una velocidad de 0,8
            # Llego a la conclusión de que un número n dividido entre 2 más un número m
            # repetidamente tiende a 2m.
            # n/2 + m -> 2m
            # Por ejemplo: n/2 + 0,4 -> 0,8
            self.velocidad.y /= 2

    def actualizar_animacion(self):
        self.image.fill(self.COLOR if not self.dash_iniciado else 'white')
        self.image.fill('DARKRED',
                        pygame.rect.Rect(self.rect.w/2 if self.orientacion == 1 else 0,
                                         self.rect.h/6, self.rect.w/2+1, self.rect.h/6))

    def aplicar_movimiento_horizontal(self):
        super().aplicar_movimiento_horizontal()
        self.dashear()

    def saltar(self):
        accion = self.input_saltar
        if accion and (self.en_suelo or self.saltando):  # (not self.cayendo or self.saltando)
            if not self.saltando:
                self.velocidad.y = self.VELOCIDAD_SALTO
                self.saltando = True
                self.timer_salto = self.cooldown_salto
            elif not self.doble_salto and not self.timer_salto:
                self.velocidad.y = self.VELOCIDAD_DOBLE_SALTO
                self.doble_salto = True

    def dashear(self):
        accion = self.input_dash
        if accion and not self.dash_iniciado and self.timer_cooldown_dash == 0:
            # print("Inicio dash...")
            self.dash_iniciado = True
            self.dash_finalizado = False
            self.timer_duracion_dash = self.duracion_dash
            self.animacion_activa = True

        if self.dash_iniciado and not self.dash_finalizado:
            # print("DASH!")
            self.velocidad.x = 15 * self.orientacion  # 15
            self.velocidad.y = 0
        elif self.dash_iniciado and self.dash_finalizado:
            # print("Finalizo dash\n")
            self.velocidad.x = 0
            self.timer_cooldown_dash = self.cooldown_dash
            self.dash_iniciado = False
            self.dash_finalizado = False
            self.animacion_activa = False

    def calcular_colisiones_horizontales(self):
        super().calcular_colisiones_horizontales()
        moneda = pygame.sprite.spritecollideany(self, self.nivel.monedas)
        if moneda:
            moneda.kill()

        enemigo = pygame.sprite.spritecollideany(self, self.juego.enemigos)
        if enemigo:
            if self.dash_iniciado:
                enemigo.kill()
            else:
                self.kill()

    def en_colision_vertical(self, obj, vy):
        super().en_colision_vertical(obj, vy)
        if vy > 0:
            self.doble_salto = False


class EnemigoDeambulante(Entidad):
    VELOCIDAD_SALTO = -9
    COLOR = 'brown'

    def __init__(self, pos: pygame.Vector2, nivel: Nivel, juego: Juego):
        super().__init__(pos, (50, 30), self.COLOR, -1, nivel, juego, 1)

    def determinar_accion(self):
        if self.flag_colision_horizontal:
            return [-self.orientacion, 0]
        else:
            return [self.orientacion, 0]

    def actualizar_animacion(self):
        self.image.fill(self.COLOR)
        self.image.fill('black',
                        pygame.rect.Rect(self.rect.w-self.rect.w/3 if self.orientacion == 1 else 0,
                                         self.rect.h/6, self.rect.w/3+1, self.rect.h/6))


class EnemigoSaltarin(Entidad):
    VELOCIDAD_SALTO = -9
    COLOR = 'darkred'

    def __init__(self, pos: pygame.Vector2, nivel: Nivel, juego: Juego):
        super().__init__(pos, (50, 30), self.COLOR, -1, nivel, juego, 1)
        self.prev_x = self.pos.x
        self.intentar_salto = False

    def determinar_accion(self):
        if self.flag_colision_horizontal and self.en_suelo:
            if not self.intentar_salto or self.prev_x != self.pos.x:
                self.intentar_salto = True
                self.prev_x = self.pos.x
                # self.velocidad_x = 4  # Ajusta velocidad para saltar
                return [self.orientacion, 1]
            else:
                # if self.prev_x == self.pos.x:
                return [-self.orientacion, 0]
                # else:
                #     self.prev_x = self.pos.x
                #     return [self.orientacion, 1]
        else:
            if self.intentar_salto and self.en_suelo:
                self.intentar_salto = False
                # self.velocidad_x = 1  # Ajusta velocidad tras saltar
            return [self.orientacion, 0]

        # return [self.orientacion, 1 if self.flag_colision_horizontal else 0]

    def actualizar_animacion(self):
        self.image.fill(self.COLOR)
        self.image.fill('black',
                        pygame.rect.Rect(self.rect.w-self.rect.w/3 if self.orientacion == 1 else 0,
                                         self.rect.h/6, self.rect.w/3+1, self.rect.h/6))


class EnemigoTirador(Tirador):
    COLOR = 'darkred'
    VELOCIDAD_SALTO = -9

    def __init__(self, pos: pygame.Vector2, nivel: Nivel, juego: Juego):
        super().__init__(pos, (32, 50), self.COLOR, -1, nivel, juego, 1)
        self.prev_x = self.pos.x
        self.intentar_salto = False

        self.disparos_efectuados = 0
        self.rafaga = 3
        self.cooldown_rafaga = 60 * 5
        self.cooldown_disparo = self.cooldown_disparo * 1.2
        self.timer_rafaga = 0

    def actualizar_timers(self):
        super().actualizar_timers()
        if self.timer_rafaga > 0:
            self.timer_rafaga -= 1

    def determinar_accion(self):
        if self.flag_colision_horizontal and self.en_suelo:
            if not self.intentar_salto or self.prev_x != self.pos.x:
                self.intentar_salto = True
                self.prev_x = self.pos.x
                # self.velocidad_x = 4  # Ajusta velocidad para saltar
                accion = [self.orientacion, 1, 0]
            else:
                # if self.prev_x == self.pos.x:
                accion = [-self.orientacion, 0, 0]
                # else:
                #     self.prev_x = self.pos.x
                #     return [self.orientacion, 1]
        else:
            if self.intentar_salto and self.en_suelo:
                self.intentar_salto = False
                # self.velocidad_x = 1  # Ajusta velocidad tras saltar
            accion = [self.orientacion, 0, 0]

        if self.disparos_efectuados < self.rafaga:
            if self.timer_rafaga == 0 and self.timer_disparo == 0:
                accion[2] = 1
                self.disparos_efectuados += 1
        else:
            self.timer_rafaga = self.cooldown_rafaga
            self.disparos_efectuados = 0

        return accion

    def actualizar_animacion(self):
        self.image.fill(self.COLOR)
        self.image.fill('black',
                        pygame.rect.Rect(self.rect.w-self.rect.w/3 if self.orientacion == 1 else 0,
                                         self.rect.h/6, self.rect.w/3+1, self.rect.h/6))


class Disparo(Entidad):
    DIMENSION = (16, 8)
    COLOR = 'white'
    VELOCIDAD_X = 16
    ACCION_1 = [1, 0, 0, 0]
    ACCION_2 = [-1, 0, 0, 0]

    def __init__(self, pos: pygame.Vector2, orientacion, grupo: pygame.sprite.AbstractGroup, nivel: Nivel, juego: Juego):
        super().__init__(pos, self.DIMENSION, self.COLOR, orientacion, nivel, juego,
                         self.VELOCIDAD_X, self.ACCION_1 if orientacion == 1 else self.ACCION_2)

        self.comprobar_colisiones_verticales = False
        self.afectado_por_gravedad = False
        self.grupo = grupo

    def calcular_colisiones_horizontales(self):
        super().calcular_colisiones_horizontales()
        if self.grupo != self.juego.jugador and (jugador := pygame.sprite.spritecollideany(self, self.juego.jugador)):
            self.flag_colision_horizontal = True
            self.en_colision_horizontal(jugador, self.velocidad.x)
        elif self.grupo != self.juego.enemigos and (enemigo := pygame.sprite.spritecollideany(self, self.juego.enemigos)):
            self.flag_colision_horizontal = True
            self.en_colision_horizontal(enemigo, self.velocidad.x)

    def en_colision_horizontal(self, obj, vx):
        super().en_colision_horizontal(obj, vx)
        if isinstance(obj, Entidad):
            obj.kill()

    def resolver_flags_y_timers(self):
        super().resolver_flags_y_timers()
        if self.flag_colision_horizontal:
            self.kill()


class Rayo:
    COLOR = {
        0: (255, 255, 255),
        1: 'darkgreen',
        2: (255, 0, 0),
        3: 'yellow',
        4: 'blue'
    }

    def __init__(self, entidad: Entidad, ang, longitud_maxima=25+64*14):
        self.entidad = entidad
        self.x1 = entidad.pos.x
        self.y1 = entidad.pos.y
        self.ang = ang
        self.x2 = entidad.pos.x
        self.y2 = entidad.pos.y
        self.longitud_maxima = longitud_maxima
        self.longitud = longitud_maxima
        self.longitud_interp = 1
        self.flag_interseccion = False
        self.objeto_impactado = 0

    def actualizar(self):
        def interseccion(x1, y1, x2, y2, x3, y3, x4, y4):
            denominador = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if denominador:
                t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominador
                u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominador
                if 0 < t < 1 and 0 < u < 1:  # u>0 o 0 < u < 1
                    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1)), t
            return None

        # Actualizamos poisición en función de la del entidad
        self.x1 = self.entidad.rect.centerx
        self.y1 = self.entidad.rect.centery

        # Actualizamos ángulo en función del ángulo del entidad
        # self.ang = self.ang_offset + self.entidad.ang

        # Actualizamos puntos de destino
        self.x2 = self.x1 + np.cos(self.ang) * self.longitud_maxima
        self.y2 = self.y1 + np.sin(self.ang) * self.longitud_maxima

        # Comprobamos colisiones con entorno para ajustar el rayo
        pts_corte = None
        dist_min = 1
        objeto = None
        for bloque in (*self.entidad.nivel.bloques, *self.entidad.juego.enemigos,
                       *self.entidad.nivel.monedas, *self.entidad.juego.disparos_jugador):
            b = bloque.rect
            dist_min_borde = 1
            res_bloque = None
            for borde in ((b.left, b.top, b.right, b.top), (b.right, b.top, b.right, b.bottom),
                          (b.left, b.bottom, b.right, b.bottom), (b.left, b.top, b.left, b.bottom)):
                res_borde = interseccion(self.x1, self.y1, self.x2, self.y2, *borde)
                if res_borde:
                    _, dist_borde = res_borde
                    if dist_borde < dist_min_borde:
                        res_bloque = res_borde
                        dist_min_borde = dist_borde

            # Si se devuelve una intersección con algún borde, entonces comprobamos si es mínimo
            if res_bloque:
                pts_borde, dist_borde = res_bloque
                if dist_borde < dist_min:
                    dist_min = dist_borde
                    pts_corte = pts_borde
                    objeto = bloque

        # Si existe un punto de corte (ya calculado como el mínimo), entonces lo establecemos como (x2, y2)
        if pts_corte:
            self.x2, self.y2 = pts_corte
            self.longitud = dist_min * self.longitud_maxima
            self.longitud_interp = np.interp(self.longitud, [0, self.longitud_maxima], [-1, 1])
            self.flag_interseccion = True
            self.objeto_impactado = 1 if isinstance(objeto, Bloque) else 3 if isinstance(objeto, Moneda) else \
                4 if isinstance(objeto, Disparo) else 2
        else:
            self.longitud = self.longitud_maxima
            self.longitud_interp = 1
            self.flag_interseccion = False
            self.objeto_impactado = 0

    def render(self, ventana, offset):
        """
        Renderiza el rayo.
        :param ventana: display o ventana donde se mostrará el rayo
        """
        pygame.draw.aaline(ventana, self.COLOR[self.objeto_impactado],
                           (self.x1-offset.x, self.y1-offset.y),
                           (self.x2-offset.x, self.y2-offset.y))


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
    @property
    def sprite(self) -> Sprite:
        """
        Property for the single sprite contained in this group

        :return: The sprite.
        """
        return super().sprite

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
