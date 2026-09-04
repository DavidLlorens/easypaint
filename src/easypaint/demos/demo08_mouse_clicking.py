#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo8(EasyPaint):
    ls: list[int]

    def __init__(self) -> None:
        super().__init__()
        self.ls = []

    def on_mouse_button(self, button: int, x: float, y: float) -> None:
        if button == 1:
            self.ls.append(self.create_circle(x, y, 20))
            if len(self.ls) > 20:  # como máximo se permiten 20 círculos
                self.erase(self.ls[0])
                del self.ls[0]
        elif button == 3:
            self.close()

    def main(self) -> None:
        self.easypaint_configure(title='Demo 8 - Using the Mouse Buttons',
                                     background='white',
                                 size=(600, 600),
                                 coordinates=(0, 0, 599, 599))
        self.create_text(300, 310, "Botón izq.: dibuja círculo", 8, 'c')
        self.create_text(300, 290, "Botón der.: termina programa", 8, 'c')


Demo8().run()
