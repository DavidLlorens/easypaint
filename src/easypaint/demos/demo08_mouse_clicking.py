#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo8(EasyPaint):
    def __init__(self):
        super().__init__()
        self.ls = []

    def on_mouse_button(self, button, x, y):
        if button == 1:
            self.ls.append(self.create_circle(x, y, 20))
            if len(self.ls) > 20:  # como máximo se permiten 20 círculos
                self.erase(self.ls[0])
                del self.ls[0]
        elif button == 2:
            self.close()

    def main(self):
        self.easypaint_configure(title='Demo 8 - Uso de los botones del ratón',
                                 background='white',
                                 size=(600, 600),
                                 coordinates=(0, 0, 599, 599))
        self.create_text(300, 290, "Botón izq.: dibuja círculo", 8, 'c')
        self.create_text(300, 310, "Botón der.: termina programa", 8, 'c')


Demo8().run()
