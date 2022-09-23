#!/usr/bin/env python3
"""
Created on 29/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
import time
from math import sin, cos, pi
from typing import *

from easypaint import EasyPaint
from easypaint.libsimple3d import Escena3D, Cubo3D, Piramide3D, Punto3D  # importa módulo de 3D

t_inc = 0.04  # incremento de t en cada frame
pi2 = 2 * pi


class Demo3(EasyPaint):
    t: float
    pv: Punto3D
    n_frames: int
    fps_id: Optional[Any]
    prev_time: float
    prev_num_lines: int
    prev_lines_ids: List[Any]

    ppd = 1500
    escena = Escena3D(ppd)

    def on_key_press(self, keysym):
        if keysym == 'Return':
            self.close()

    def animation(self):
        global t_inc
        self.n_frames += 1
        self.t = (self.t + t_inc) % pi2
        self.pv.posParametrica(self.t)
        self.escena.puntoVista(self.pv)
        lineas = self.escena.dibuja()
        num_lines = len(lineas)
        lines_ids = []
        for i in range(num_lines):
            lines_ids.append(self.create_line(*lineas[i]))
            if i < self.prev_num_lines: self.erase(self.prev_lines_ids[i])
        self.erase(self.prev_lines_ids[num_lines:])
        # if t>pi: break
        if self.t > pi - 1e-2 or self.t < 1e-2: t_inc = -t_inc
        self.prev_lines_ids = lines_ids
        self.prev_num_lines = num_lines
        if self.fps_id is not None: self.erase(self.fps_id)
        c_time = time.time()
        if c_time != self.prev_time:
            self.fps_id = self.create_text(0, -450, f"FPS: {self.n_frames / (c_time - self.prev_time):.2f}", 10, 'S')
        self.update()
        self.after(0, self.animation)

    def main(self):
        self.easypaint_configure(title='Demo 3 - Paseo 3D',
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
        self.create_text(0, -500, "Pulsa <Return> para salir", 10, 'S')

        self.t = 0
        self.pv = Punto3D(lambda t: 10000 * sin(t), lambda t: 10000 * sin(t), lambda t: 10000 * cos(t))
        self.n_frames = 0
        self.prev_num_lines = 0
        self.prev_lines_ids = []
        self.fps_id = None
        self.prev_time = time.time()
        self.after(0, self.animation)


Demo3().run()
