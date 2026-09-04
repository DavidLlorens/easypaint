#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo7(EasyPaint):
    x2: float | None
    y2: float | None
    lines_ids: list[int | None]

    def __init__(self) -> None:
        super().__init__()
        self.x2 = None
        self.y2 = None
        self.lines_ids = []

    def on_mouse_button(self, button: int, x: float, y: float) -> None:
        if button == 3:
            self.close()

    def on_mouse_release(self, button: int, x: float, y: float) -> None:
        if button == 1:
            self.x2 = self.y2 = None

    def on_mouse_motion(self, button: int, x: float, y: float) -> None:
        if button == 1:
            if  self.x2 is not None and self.y2 is not None:
                self.lines_ids.append(self.create_line(self.x2, self.y2, x, y))
                while len(self.lines_ids) > 200:
                    self.erase(self.lines_ids[0])
                    del self.lines_ids[0]
            self.x2, self.y2 = x, y

    def main(self) -> None:
        self.easypaint_configure(title='Demo 7 - Drawing with the Mouse',
                                     background='white',
                                 size=(600, 600),
                                 coordinates=(0, 0, 1000, 1000))
        self.create_text(500, 50, "Dibuja con el botón izquierdo.", 8, 's')
        self.create_text(500, 0, "Termina programa pulsando el boton derecho.", 8, 's')


Demo7().run()
