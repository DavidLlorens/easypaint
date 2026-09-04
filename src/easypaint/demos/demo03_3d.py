#!/usr/bin/env python3
"""
Created on 29/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
import time
from math import sin, cos, pi

from easypaint import EasyPaint
from easypaint.libsimple3d import Escena3D, Cubo3D, Piramide3D, Punto3D  # importa módulo de 3D

t_inc = 0.02  # incremento de t en cada frame
pi2: float = 2 * pi
frame_period: int = 16  # 16 ms por frame => 62.5 FPS, 17 ms por frame => 58.8 FPS, 10 ms por frame => 100 FPS
target_fps: float = 1.0 / frame_period


class Demo3(EasyPaint):
    t: float
    pv: Punto3D
    n_frames: int
    fps_id: int | None
    prev_time: list[float]

    ppd: int = 1500
    escena: Escena3D = Escena3D(ppd)

    def on_key_press(self, keysym: str) -> None:
        self.close()

    def animation(self) -> None:
        global t_inc
        self.after(frame_period, self.animation)

        self.prev_time.append(time.time())
        if len(self.prev_time) > 30:
            self.prev_time.pop(0)

        if len(self.prev_time) > 1:
            if self.fps_id is not None: 
                self.erase(self.fps_id)
            self.fps_id = self.create_text(0, -450, f"FPS: {len(self.prev_time)/(self.prev_time[-1] - self.prev_time[0]):.2f}", 10, 'S')

        self.t = (self.t + t_inc) % pi2
        self.pv.posParametrica(self.t)
        self.escena.puntoVista(self.pv)
        lineas = self.escena.dibuja()
        
        self.erase('linea')
        for linea in lineas:
            self.create_line(*linea, tag='linea')

        # if t>pi: break
        if self.t > pi - 1e-2 or self.t < 1e-2: t_inc = -t_inc
        self.update()

    def main(self) -> None:
        self.easypaint_configure(title='Demo 3 - 3D Animation',
                                 background='steelblue',
                                 size=(600, 600),
                                 coordinates=(-500, -500, 500, 500))
        for x, y, z in [(1000, 1000, 1000), (1000, 1000, -1000),
                        (1000, -1000, 1000), (1000, -1000, -1000),
                        (-1000, 1000, 1000), (-1000, 1000, -1000),
                        (-1000, -1000, 1000), (-1000, -1000, -1000)]:
            if y == -1000:
                cubo = Cubo3D(1500, Punto3D(x, y, z))
            else:
                cubo = Piramide3D(Punto3D(1500, 1500, 1500), Punto3D(x, y, z))
            self.escena.insertar(cubo)
        self.create_text(0, -500, "Press any key to exit", 10, 'S')

        self.t = 0
        self.pv = Punto3D(lambda t: 10000 * sin(t), lambda t: 10000 * sin(t), lambda t: 10000 * cos(t))
        self.fps_id = None
        self.prev_time = []
        self.after(0, self.animation)


Demo3().run()
