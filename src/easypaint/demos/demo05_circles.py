#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from random import randrange

from easypaint import EasyPaint


class Demo5(EasyPaint):
    t_id: int | None
    o_ids: list[int]
    colores: list[str] = ['red', 'green', 'blue', 'yellow', 'orange', 'black', 'pink']

    def __init__(self) -> None:
        super().__init__()
        self.t_id = None
        self.o_ids = []

    def dibuja_circulo_azar(self) -> int:
        x = randrange(0, 1000)
        y = randrange(0, 1000)
        tam = randrange(10, 300)
        col = self.colores[randrange(0, len(self.colores))]
        return self.create_filled_circle(x, y, tam, col)

    def on_key_press(self, keysym: str) -> None:
        self.close()

    def animation(self) -> None:
        if len(self.o_ids) == 100:
            self.erase(self.o_ids[0])
            del self.o_ids[0]
        self.o_ids.append(self.dibuja_circulo_azar())
        if self.t_id:
            self.tag_raise(self.t_id)
        self.update()
        self.after(0, self.animation)

    def main(self) -> None:
        self.easypaint_configure(title='Demo 5 - Random Circles',
                                     background='steelblue',
                                 size=(600, 600),
                                 coordinates=(0, 0, 1000, 1000))

        self.t_id = self.create_text(500, 0, "Press any key to exit", 12, anchor="s")
        self.after(0, self.animation)


Demo5().run()
