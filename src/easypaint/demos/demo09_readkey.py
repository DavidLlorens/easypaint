#!/usr/bin/env python3
"""
Created on 30/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo9(EasyPaint):
    id = None

    def on_key_release(self, keysym):
        if self.id is not None:
            self.erase(self.id)

    def on_key_press(self, keysym):
        if self.id is not None:
            self.erase(self.id)
        self.id = self.create_text(200, 100, f"{keysym}", 40, 'c')
        if keysym == 'Escape':
            self.close()

    def main(self):
        self.easypaint_configure(title='Demo 9 - readkey',
                                 background='white',
                                 size=(401, 201),
                                 coordinates=(0, 0, 400, 200))
        self.create_text(200, 0, "Press any key. 'Escape' to exit.", 10, 's')


Demo9().run()
