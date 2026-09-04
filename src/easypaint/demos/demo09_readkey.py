#!/usr/bin/env python3
"""
Created on 30/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from easypaint import EasyPaint


class Demo9(EasyPaint):
    text_id: int | None

    def __init__(self) -> None:
        super().__init__()
        self.text_id = None

    def on_key_release(self, keysym: str) -> None:
        if self.text_id is not None:
            self.erase(self.text_id)

    def on_key_press(self, keysym: str) -> None:
        if self.text_id is not None:
            self.erase(self.text_id)
        self.text_id = self.create_text(200, 100, f"{keysym}", 40, 'c')
        if keysym == 'Escape':
            self.close()

    def main(self) -> None:
        self.easypaint_configure(title='Demo 9 - Read Key',
                                     background='white',
                                 size=(401, 201),
                                 coordinates=(0, 0, 400, 200))
        self.create_text(200, 0, "Press any key. 'Escape' to exit.", 10, 's')


Demo9().run()
