#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from enum import Enum

from easypaint import EasyPaint


class State(Enum):
    ToDelete = 1
    ToExit = 2


class Demo1(EasyPaint):
    state: State = State.ToDelete

    def on_key_press(self, keysym):
        if self.state == State.ToDelete:
            self.erase()
            self.create_text(250, 250, "Press any key to exit", 12)
            self.state = State.ToExit
        elif self.state == State.ToExit:
            self.close()

    def main(self):
        self.easypaint_configure(title='Demo 1 - Funciones predefinidas',
                                 size=(501, 501),
                                 coordinates=(0, 0, 500, 500))
        o_ids = []
        # Dibuja matriz de puntos
        for x in range(25, 225, 21):
            for y in range(275, 475, 21):
                o_ids.append(self.create_point(x, y, ['black', 'red'][(x + y) % 2]))

        # Dibuja dos circulos (uno relleno y otro no)
        o_ids.append(self.create_filled_circle(375, 375, 125, 'black', 'blue'))
        o_ids.append(self.create_circle(125, 125, 125, 'red'))

        # Dibuja dos rectangulos (uno relleno y otro no)
        o_ids.append(self.create_rectangle(150, 75, 200, 175, 'red'))
        o_ids.append(self.create_filled_rectangle(50, 75, 100, 175, 'black', 'red'))

        # Dibuja dos lineas en cruz
        o_ids.append(self.create_line(250, 125, 500, 125, 'green'))
        o_ids.append(self.create_line(375, 0, 375, 250, 'black'))

        # escribe texto
        o_ids.append(self.create_text(250, 250, "Press any key to delete all", 12))


Demo1().run()
