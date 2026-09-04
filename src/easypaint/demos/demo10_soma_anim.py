#!/usr/bin/env python3
"""
Created on 30/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""

from __future__ import annotations

from math import cos, pi, sin

from easypaint import EasyPaint
from easypaint.libsimple3d import Cubo3D, Escena3D, Matriz3D, Punto3D


class SomaAnim(EasyPaint):
    ppd: int = 1000
    escena: Escena3D = Escena3D(ppd)

    colores_piezas: list[str] = ['red', 'green', 'blue', 'orange', 'gold', 'brown', 'cyan']

    sol: list[list[list[int]]]
    cubos: dict[int, list[Cubo3D]]

    def __init__(self, sol: list[list[list[int]]]) -> None:
        EasyPaint.__init__(self)
        self.sol = sol
        self.cubos = {}

    def build(self) -> dict[int, list[tuple[int, int, int]]]:
        self.cubos = {}
        f: dict[int, list[tuple[int, int, int]]] = {}
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    key = self.sol[x][y][z]
                    if key in f:
                        f[key].append((x, y, z))
                    else:
                        f[key] = [(x, y, z)]
        lado = 800
        piezas = sorted(f)
        colores = {key: self.colores_piezas[i % len(self.colores_piezas)] for i, key in enumerate(piezas)}
        for key in piezas:
            for cube in f[key]:
                p = Punto3D(cube[0] * lado, cube[1] * lado, cube[2] * lado)
                cubo = Cubo3D(lado * 0.9999999999, p, colores[key])
                if key in self.cubos:
                    self.cubos[key].append(cubo)
                else:
                    self.cubos[key] = [cubo]
                m = Matriz3D()
                m.traslacion(-1 * lado, -1 * lado, -1 * lado)
                cubo.transforma3d(m)
                cubo.setup()
                self.escena.insertar(cubo)
        return f

    def on_key_press(self, keysym: str) -> None:
        self.close()

    def main(self) -> None:
        def anim(step: int, max_step: int) -> None:
            nonlocal t, nl2, lin2, sc_old, ii
            if step < max_step // 2:
                ii = step
            else:
                ii = 100 - step

            pv.posParametrica(t)
            self.escena.puntoVista(pv)
            lineas = self.escena.dibuja()
            self.erase('linea')
            for i in range(len(lineas)):
                self.create_line(*lineas[i], tag='linea')

            self.update()

            t = (t + inc) % pi2
            sc = 30 * ii
            for key in self.cubos:
                xm = sum([cubo[0] for cubo in f[key]]) / len(f[key])
                ym = sum([cubo[1] for cubo in f[key]]) / len(f[key])
                zm = sum([cubo[2] for cubo in f[key]]) / len(f[key])

                for cubo in self.cubos[key]:
                    m = Matriz3D()
                    if sc_old is not None:
                        m.traslacion(-(xm - 1) * sc_old, -(ym - 1) * sc_old, -(zm - 1) * sc_old)
                    m.traslacion((xm - 1) * sc, (ym - 1) * sc, (zm - 1) * sc)
                    cubo.transforma3d(m)
                    cubo.setup()
            sc_old = sc

            step = (step + 1) % max_step
            self.after(10, lambda: anim(step, max_step))

        window_size = 500, 500
        s = 480
        coordinates = (-s, -s, s, s)

        self.easypaint_configure(title='Soma Cube - Animated Solution',
                                     background='black',
                                 size=window_size,
                                 coordinates=coordinates)
        self.create_text(0, -s+20, "Press any key to exit", 10, 'S', 'darkgray')

        f = self.build()

        pi2 = 2 * pi
        lin2: list[int] = []
        nl2 = 0
        sc_old: float | None = None
        t = 0.0000001

        pv = Punto3D(lambda tt: 8000 * sin(tt),
                     lambda tt: 5000,
                     lambda tt: 8000 * cos(tt))

        inc: float = 1.003 * pi / 100  # 0.042
        ii = 0
        self.after(0, lambda: anim(0, 100))


if __name__ == '__main__':
    sol1 = [[[1, 7, 7], [4, 4, 7], [3, 4, 4]], [[1, 5, 2], [1, 5, 7], [3, 3, 6]], [[2, 2, 2], [5, 5, 6], [3, 6, 6]]]
    sol2 = [[[3, 6, 6], [1, 5, 6], [1, 5, 4]], [[3, 3, 6], [1, 7, 4], [5, 5, 4]], [[3, 7, 7], [2, 7, 4], [2, 2, 2]]]
    sa = SomaAnim(sol1)
    sa.run()
