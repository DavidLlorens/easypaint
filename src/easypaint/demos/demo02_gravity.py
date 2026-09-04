#!/usr/bin/env python3
"""
Created on 29/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Planeta:
    x: float
    y: float
    vx: float
    vy: float
    masa: float
    color: str

    def __init__(self, x: float, y: float, vx: float, vy: float, masa: float, color: str) -> None:
        self.x, self.y, self.vx, self.vy, self.masa, self.color = x, y, vx, vy, masa, color

    def dibuja(self, ec: EasyPaint) -> int:
        return ec.create_circle(self.x, self.y, self.masa, self.color)


def gravedad(p1: Planeta, lp: list[Planeta]) -> None:
    for p2 in lp:
        x21 = p2.x - p1.x
        y21 = p2.y - p1.y
        x12 = p1.x - p2.x
        y12 = p1.y - p2.y
        r3 = (x21 * x21 + y21 * y21) ** 1.5
        masa1r3 = p1.masa / r3
        masa2r3 = p2.masa / r3
        p1.vx += masa2r3 * x21
        p1.vy += masa2r3 * y21
        p2.vx += masa1r3 * x12
        p2.vy += masa1r3 * y12
    p1.x += p1.vx
    p1.y += p1.vy


class Demo2(EasyPaint):
    planets_ids: list[int]
    planets: list[Planeta]

    def __init__(self) -> None:
        super().__init__()
        self.planets_ids = []
        self.planets = []

    def on_key_press(self, keysym: str) -> None:
        self.close()

    def animation(self, c: int) -> None:
        old_x: list[float] = []
        old_y: list[float] = []
        for p in self.planets:
            old_x.append(p.x)
            old_y.append(p.y)
        for _ in range(5):
            for i in range(len(self.planets)):
                gravedad(self.planets[i], self.planets[i + 1:])
        old_lc, self.planets_ids = self.planets_ids, []
        for i in range(len(self.planets)):
            self.planets_ids.append(self.planets[i].dibuja(self))
            self.erase(old_lc[i])
            self.create_line(old_x[i], old_y[i], self.planets[i].x, self.planets[i].y, self.planets[i].color)
        self.update()
        if c > 0:
            self.after(5, lambda: self.animation(c - 1))

    def main(self) -> None:
        t: int = 400
        self.easypaint_configure(title='Demo 2 - Gravitational Chaos',
                                     background='black',
                                 size=(600, 600),
                                 coordinates=(-t, -t, t, t))

        # Si quieres añadir mas planetas, adelante...
        self.planets.append(Planeta(-200.0, -200.0, 0.1, 0.0, 20.0, 'red'))
        self.planets.append(Planeta(200.0, 200.0, -0.1, 0.0, 20.0, 'magenta'))
        self.planets.append(Planeta(0.0, 0.0, 0.1, 0.1, 0.01, 'green'))

        for p in self.planets: self.planets_ids.append(p.dibuja(self))

        self.create_text(0, -400, "Press any key to exit", 10, 'S', 'white')
        self.after(0, lambda: self.animation(2000))


Demo2().run()
