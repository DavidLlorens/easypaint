#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo1(EasyPaint):
    def on_key_press(self, keysym):
        self.close()

    def main(self):
        x1, y1, x2, y2 = (0, 0, 399, 399)
        self.easypaint_configure(title='Demo 0 - Window size and window coordinates',
                                 background='white',
                                 size=(400, 400),
                                 coordinates=(x1, y1, x2, y2))
        print(self.scale, self.size, self.coordinates)

        c = 'red'
        self.create_line(x1, y1, x1, y2, c)
        self.create_line(x1, y1, x2, y1, c)
        self.create_line(x2, y2, x2, y1, c)
        self.create_line(x2, y2, x1, y2, c)

        # escribe texto
        self.create_text((x1 + x2) / 2, (y1 + y2) / 2, "Press any key to exit", 12, 'c')


Demo1().run()
