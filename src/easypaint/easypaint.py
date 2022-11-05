"""
2022/09/22 - 1.0.4 - Corregido create_filled_polygon(...)
2022/09/22 - 1.0.3 - Añade create_filled_polygon(...)
2022/09/22 - 1.0.2 - Añade create_polygon(...)
2022/09/01 - 1.0.1 - Biblioteca para crear ventanas con un lienzo.

@author: David Llorens
@contact: dllorens@uji.es
@copyright: Universitat Jaume I de Castelló (2021)
@licence: GNU Affero General Public License v3
"""

import tkinter
from abc import ABC, abstractmethod
from typing import *
import platform

if platform.system() == "Windows":
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

SIZE_SCALING = 1.0

class EasyPaintException(Exception):
    def __init__(self, message, value=None):
        self.value = value
        self.message = message
        super().__init__(self.message)


class EasyPaint(ABC):
    __slots__ = ('_title', '_background', '_root', '_canvas',
                 '_width', '_height', '_xscale', '_yscale',
                 '_left', '_right', '_top', '_bottom', '_closing')

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._root.title(self._title)

    @property
    def size(self):
        return self._width/SIZE_SCALING, self._height/SIZE_SCALING

    @size.setter
    def size(self, value):
        self._width, self._height = value[0]*SIZE_SCALING, value[1]*SIZE_SCALING
        self._left, self._bottom, self._right, self._top = (0, 0, self._width - 1, self._height - 1)
        if hasattr(self, '_canvas'):
            self.erase()
            canvas_args = {"width": self._width, "height": self._height}
            self._canvas.configure(**canvas_args)
        self._set_scale()

    @property
    def coordinates(self):
        return self._left, self._bottom, self._right, self._top

    @coordinates.setter
    def coordinates(self, value):
        if hasattr(self, '_canvas'):
            self.erase()
        if value is None:
            self._left, self._bottom, self._right, self._top = 0, 0, self._width - 1, self._height - 1
        else:
            self._left, self._bottom, self._right, self._top = value
        self._set_scale()

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        if hasattr(self, '_canvas'):
            canvas_args = {"background": value if value is not None else 'white'}
            self._canvas.configure(**canvas_args)
            if value is None:
                self._set_transparent_background()

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._bottom

    @property
    def scale(self) -> Tuple[float, float]:
        return self._xscale, self._yscale

    @property
    def center(self) -> Tuple[float, float]:
        return (self._right + self._left) / 2, (self._top + self._bottom) / 2

    def __init__(self,
                 size: Tuple[int, int] = (500, 500),
                 coordinates: Optional[Tuple[float, float, float, float]] = None,
                 title: Optional[str] = 'EasyPaint',
                 background: Optional[str] = 'white'):
        self._closing = False

        self._width, self._height = size[0], size[1]
        if coordinates is None:
            self._left, self._bottom, self._right, self._top = 0, 0, size[0]-1, size[1]-1
        else:
            self._left, self._bottom, self._right, self._top = coordinates
        self._set_scale()

        self._title = title
        self._background = background

        self._root = tkinter.Tk()

        self._root.title(self._title)
        self._root.resizable(width=True, height=True)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root.bind('<KeyPress>', lambda e: self.on_key_press(e.keysym))
        self._root.bind('<KeyRelease>', lambda e: self.on_key_release(e.keysym))

        self._canvas = tkinter.Canvas(self._root, borderwidth=0, highlightthickness=0,
                                      height=self._height, width=self._width, background=self._background)
        self._canvas.pack(padx=0, pady=0, anchor="nw")
        self._canvas.bind('<Button>', self._on_mouse_button)
        self._canvas.bind('<ButtonRelease>', self._on_mouse_release)
        self._canvas.bind('<B1-Motion>', lambda e: self._on_mouse_motion(1, e))
        self._canvas.bind('<B2-Motion>', lambda e: self._on_mouse_motion(2, e))
        self._canvas.bind('<B3-Motion>', lambda e: self._on_mouse_motion(3, e))
        self._canvas.bind('<Leave>', self.on_mouse_leave)
        #self._root.resizable(width=False, height=False)

    def easypaint_configure_old(self, size: Tuple[int, int],
                            coordinates: Optional[Tuple[float, float, float, float]] = None,
                            title: Optional[str] = 'EasyPaint',
                            background: Optional[str] = 'white'):
        """Configure the window

        Arguments:
            size -- tuple (width, height)

            coordinates -- tuple (left, bottom, right, top). Default is (0, 0, width-1, height-1)

            title -- window tile. Default is 'EasyPaint'

            background -- color name. Default is 'white'
        """
        if self._closing: return
        self.erase()

        if not (isinstance(size, tuple) and len(size) == 2 and isinstance(size[0], int) and isinstance(size[1], int) and
                size[0] > 0 and size[1] > 0):
            raise EasyPaintException(
                "easypaint_configure: Parameter 'size' must be a tuple of two integers greater than 0")

        self.size = size  # Resetea self.coordinates y recalcula el escalado
        if coordinates is not None:
            self.coordinates = coordinates # Recalcula el escalado

        self._background = background

        if title is not None:
            self.title = title

    # PRIVATE METHODS ----------------------------------------------------------------

    def _set_scale(self):
        ww = self._right - self._left
        iw = 1 if ww >= 0 else -1
        self._xscale = self._width / float(ww + iw)
        hh = self._top - self._bottom
        ih = 1 if hh >= 0 else -1
        self._yscale = self._height / float(hh + ih)

    def _set_transparent_background(self):
        if self._closing: return
        self._root.wm_attributes("-transparent", True)
        self._root.config(bg='systemTransparent')
        self._canvas.config(bg='systemTransparent')

    def _transform(self, x, y):
        xb = int((x - self._left) * self._xscale)
        yb = int((self._top - y) * self._yscale)
        return xb, yb

    def _transform_x(self, x, ):
        return int((x - self._left) * self._xscale)

    def _transform_y(self, y):
        return int((self._top - y) * self._yscale)

    def _on_mouse_release(self, event):
        if self._closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_release(event.num, x, y)

    def _on_mouse_button(self, event):
        if self._closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_button(event.num, x, y)

    def _on_mouse_motion(self, button, event):
        if self._closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_motion(button, x, y)

    # -----------------------------------------------------------------

    def on_mouse_release(self, button, x, y):
        pass

    def on_mouse_button(self, button, x, y):
        pass

    def on_mouse_motion(self, button, x, y):
        pass

    def on_mouse_leave(self, event):
        pass

    def on_key_press(self, keysym):
        pass

    def on_key_release(self, keysym):
        pass

    # -----------------------------------------------------------------

    def update(self):
        """Enter event loop until all pending events have been processed by Tcl.
        """
        if self._closing: return
        self._canvas.update()  # animaciones más suaves
        # self._canvas.update_idletasks()    # animaciones más bruscas y rapidas

    def create_rectangle(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black', fill=None, **args):
        """Draws a rectangle

        Arguments:
            x1, y1 -- lower left point coordinates

            x2, y2 -- upper right point coordinates

            color -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the rectangle: erase(id)
        """
        if self._closing: return
        fn = 'create_rectangle' if fill is None else 'create_filled_rectangle'
        args['outline'] = color[:]
        if fill is not None: args['fill'] = fill[:]
        try:
            x1b, y1b = self._transform(x1, y1)
            x2b, y2b = self._transform(x2, y2)
            if x2b < x1b:
                x1b, x2b = x2b, x1b
            if y2b < y1b:
                y1b, y2b = y2b, y1b
        except:
            raise EasyPaintException(f"Wrong coordinates in {fn}: {(x1, y1, x2, y2)}")

        try:
            return self._canvas.create_rectangle(*(x1b, y1b, x2b, y2b), **args)
        except:
            raise EasyPaintException(f"{fn}")

    def create_filled_rectangle(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black', fill=None,
                                **args):
        """Draws a filled rectangle

        Arguments:
            x1, y1 -- lower left point coordinates

            x2, y2 -- upper right point coordinates

            color -- color name (default is 'black')

            fill -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the rectangle: erase(id)
        """
        if self._closing: return
        if fill is None: fill = color
        return self.create_rectangle(x1, y1, x2, y2, color, fill, **args)

    def create_circle(self, x: float, y: float, radius: float, color: str = 'black', fill=None, **args):
        """Draws a circle

        Arguments:
            x, y -- point coordinates

            radius -- float

            color -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the circle: erase(id)
        """
        if self._closing: return
        fn = 'create_circle' if fill is None else 'create_filled_circle'
        args['outline'] = color[:]
        if fill is not None: args['fill'] = fill[:]
        try:
            x1b, y1b = self._transform(x - radius, y - radius)
            x2b, y2b = self._transform(x + radius, y + radius)
        except:
            raise EasyPaintException(f"Wrong coordinates in {fn}: {(x, y)}")
        try:
            return self._canvas.create_oval(*(x1b, y1b, x2b, y2b), **args)
        except:
            raise EasyPaintException(f"{fn}")

    def create_filled_circle(self, x: float, y: float, radius: float, color='black', fill=None, **args):
        """Draws a filled circle

        Arguments:
            x, y -- point coordinates

            radius -- float

            color -- color name (default is 'black')

            fill -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the circle: erase(id)
        """
        if self._closing: return
        if fill is None: fill = color
        return self.create_circle(x, y, radius, color, fill, **args)

    def create_polygon(self, *params, color: str = 'black', fill: str = None, **args):
        """Draws a polygon

        Arguments:
            x0, y0, x1, y1, ...  -- point coordinates

            color -- outline color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the polygon: erase(id)
        """
        if self._closing: return
        args['fill'] = '' if fill is None else fill
        args['outline'] = color
        try:
            params2 = [self._transform_x(e) if i % 2 == 0 else self._transform_y(e) for i, e in enumerate(params)]
        except:
            raise EasyPaintException(f"Wrong coordinates in create_polygon: {params}")
        try:
            return self._canvas.create_polygon(*params2, **args)
        except Exception as e:
            raise EasyPaintException(f"create_polygon: {e}")

    def create_filled_polygon(self, *params, color: str = 'black', fill: str = None, **args):
        """Draws a filled polygon

        Arguments:
            x0, y0, x1, y1, ...  -- point coordinates

            color -- outline color name (default is 'black')

            fill -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the polygon: erase(id)
        """
        if self._closing: return
        return self.create_polygon(*params, color=color, fill=color, **args)

    def create_point(self, x: float, y: float, color: str = 'black', **args):
        """Draws a point

        Arguments:
            x, y -- point coordinates

            color -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move o delete the point: erase(id)
        """
        if self._closing: return
        args['fill'] = color[:]
        args['width'] = 2
        try:
            x1b, y1b = self._transform(x, y)
            x2b = x1b + 2
        except:
            raise EasyPaintException(f"Wrong coordinates in create_point: {(x, y)}")
        try:
            return self._canvas.create_line(*(x1b, y1b, x2b, y1b), **args)
        except:
            raise EasyPaintException("create_point")

    def create_line(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black', **args):
        """Draws a line between two points

        Arguments:
            x1, y1 -- start point coordinates
            x2, y2 -- end point coordinates
            color -- color name (default is 'black')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the line
        """
        if self._closing: return
        args['fill'] = color
        try:
            x1b, y1b = self._transform(x1, y1)
            x2b, y2b = self._transform(x2, y2)
        except:
            raise EasyPaintException(f"Wrong coordinates in create_line: {(x1, y1, x2, y2)}")
        try:
            # id = self.canvas.create_line(x1b, y1b, x2b, y2b, args.copy())
            return self._canvas.create_line(*(x1b, y1b, x2b, y2b), **args)
        except:
            raise EasyPaintException("create_line")

    def create_text(self, x: float, y: float, text: str, font_size: int = 10,
                    anchor: str = 'center', color: str = 'black', justify: str = "left", **args):
        """Draws a line of text

        Arguments:
            x, y -- point coordinates

            text -- string

            font_size -- int (default is 10)

            anchor -- string (default is 'center')

            color -- color name (default is 'black')

            justify -- string (default is 'left')

        Returns:
            A number (identifier). You can use this 'id' to move or delete the text: erase(id)
        """
        if self._closing: return
        args['text'] = text
        args['anchor'] = anchor.lower()
        args['fill'] = color
        args['justify'] = justify
        args['font'] = ('courier', int(font_size * 1.15 + 2), 'bold')
        try:
            xb, yb = self._transform(x, y)
        except:
            raise EasyPaintException(f"Wrong coordinates in create_text: {(x, y)}")
        try:
            # return self.canvas.create_text(xb, yb, args)
            return self._canvas.create_text(*(xb, yb), **args)
        except:
            raise EasyPaintException("create_text")

    def erase(self, param=None):
        """Remove element from canvas

        Uses:
        \t erase() -- clean the canvas

        \t erase(*tags_or_ids): remove elements

        \t erase(tag_or_id): remove the element
        """
        if self._closing: return
        if param is None:  # Delete all elements
            try:
                for elem in self._canvas.find_all():
                    self._canvas.delete(elem)
            except tkinter.TclError:
                pass
        elif isinstance(param, list):  # Delete list of elements
            if len(param) > 0:
                try:
                    for elem in param:
                        self._canvas.delete(elem)
                except:
                    raise EasyPaintException(f"Wrong id in erase: {param}")
        else:  # Delete single element
            try:
                self._canvas.delete(param)
            except:
                raise EasyPaintException("erase")

    def save_eps(self, nombre: str):
        """Print the contents of the canvas to a postscript file.
        """
        if self._closing: return
        data = self._canvas.postscript(height=self._height, width=self._width,
                                       pagewidth='20.0c')
        try:
            f = open(nombre, 'w')
            try:
                f.write(data)
            finally:
                f.close()
            res = 1
        except:
            res = 0
        return res

    def move(self, tags, x: float, y: float):
        """Move items with tags
        """
        if self._closing: return
        try:
            xb = x * self._xscale
            yb = -y * self._yscale
        except:
            raise EasyPaintException(f"Wrong coordinates in move: x={x}, y={y}")
        try:
            self._canvas.move(tags, xb, yb)
        except:
            raise EasyPaintException("move")

    def close(self):
        """Terminates the program
        """
        if self._closing: return
        self._closing = True
        self._root.destroy()
        self._root.quit()

    def run(self):
        """ Launch the mainloop
        """
        if self._closing: return
        self._root.mainloop()

    def after(self, time: int, f: Callable[[Any], Any]):
        """Call function once after given time.

        Arguments:
            time -- integer that specifies the time in milliseconds

            f -- the function which shall be called
        """
        if self._closing: return
        self._root.after(time, f)

    def tag_lower(self, tag):
        """Lower an item (z-index).
        """
        if self._closing: return
        self._canvas.tag_lower(tag)

    def tag_raise(self, tag):
        """Raise an item (z-index).
        """
        if self._closing: return
        self._canvas.tag_raise(tag)


# --------------------------------------------------------------------------


if __name__ == "__main__":
    class Demo(EasyPaint):
        def __init__(self, size):
            super().__init__(size=size, title="EasyPaint")

            print(self.size, self.coordinates, self.scale)
            self.create_filled_rectangle(10, 10, 590, 590, "black", "white")
            x, y = self.center
            self.create_text(x, y, "To exit press any key\nor\nclose the window", 14, justify="center")
            # self.save_eps("kk.eps")

        def on_key_press(self, keysym):
            self.close()

    Demo(size=(600,600)).run()
