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
    Initial = 1
    Delete = 2
    Exit = 3


class Demo4(EasyPaint):
    state: State = State.Initial
    textId = None

    def on_key_press(self, keysym):
        if self.state == State.Initial:
            pass
        elif self.state == State.Delete:
            self.erase(['c2', self.textId])
            self.create_text(500, 0, "Press any key to exit", 12, 's')
            self.state = State.Exit
        elif self.state == State.Exit:
            self.close()

    def animation(self, c):
        self.move('c', 1, 0)
        self.move('c2', -1, 0)
        if c > 0:
            self.after(10, lambda: self.animation(c - 1))
        else:
            self.textId = self.create_text(500, 0, "Press any key to delete left circles", 12, 's')
            self.state = State.Delete

    def main(self):
        self.easypaint_configure(title='Demo 4 - Interferencia',
                                 background='steelblue',
                                 size=(600, 600),
                                 coordinates=(0, 0, 1000, 1000))
        for i in range(1, 16):
            self.create_circle(300, 500, i * 20, 'black', tags='c')
            self.create_circle(700, 500, i * 20, 'black', tags='c2')

        self.after(0, lambda: self.animation(400))


Demo4().run()
