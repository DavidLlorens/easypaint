#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from typing import *

from easypaint import EasyPaint


class Demo7(EasyPaint):
    x2: Optional[float] = None
    y2: Optional[float] = None
    lines_ids: List[Any] = []

    def on_mouse_button(self, button, x, y):
        if button == 2:
            self.close()

    def on_mouse_release(self, button, x, y):
        if button == 1:
            self.x2 = self.y2 = None

    def on_mouse_motion(self, button, x, y):
        if button == 1:
            if self.x2 is not None:
                self.lines_ids.append(self.create_line(self.x2, self.y2, x, y))
                while len(self.lines_ids) > 200:
                    self.erase(self.lines_ids[0])
                    del self.lines_ids[0]
            self.x2, self.y2 = x, y

    def main(self):
        self.easypaint_configure(title='Demo 7 - Dibujando con el ratón',
                                 background='white',
                                 size=(600, 600),
                                 coordinates=(0, 0, 1000, 1000))
        self.create_text(500, 50, "Dibuja con el botón izquierdo.", 8, 's')
        self.create_text(500, 0, "Termina programa pulsando el boton derecho.", 8, 's')


Demo7().run()
