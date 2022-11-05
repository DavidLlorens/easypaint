#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo1(EasyPaint):
    def __init__(self, size=(400, 400)):
        super().__init__(title='Demo 0 - Window size and window coordinates',
                         size=size)
        x1, y1, x2, y2 = self.coordinates
        # Dibuja borde
        c = 'red'
        self.create_line(x1, y1, x1, y2, c)
        self.create_line(x1, y1, x2, y1, c)
        self.create_line(x2, y2, x2, y1, c)
        self.create_line(x2, y2, x1, y2, c)
        # Escribe texto
        self.create_text((x1 + x2) / 2, (y1 + y2) / 2, "Press any key to exit", 12, 'c')

    def on_key_press(self, keysym):
        self.close()


Demo1(size=(400, 400)).run()
