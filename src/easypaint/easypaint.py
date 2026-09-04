"""
2026/09/04 - 1.0.10 - Cambia 'tkinter.Event[tkinter.Canvas]' por 'tkinter.Event' en los métodos 
                      on_mouse_release, on_mouse_button y on_mouse_motion para evitar errores 
                      de tipado en Python 3.12.
2026/06/08 - 1.0.9 - Añade `py.typed` al paquete para publicar tipos correctamente en PyPI.
                   - Ajusta el empaquetado para eliminar el aviso de stub ausente.
2026/06/06 - 1.0.8 - Añade tipado compatible con Python 3.12 y actualiza metadatos de versión.
                   - Ajusta la API pública del módulo con anotaciones explícitas.
2024/09/30 - 1.0.7 - Corregido bug cuando self.coordinates es None.
2024/09/27 - 1.0.6 - Corregido __slots__ y tipo del método after.
                   - Added 'TVERSION' constant
                   - Corrige bug en 'FIT' (ver 1.0.5).
2023/09/21 - 1.0.5 - Added 'VERSION' constant
                   - easypaint_configure(...): Parameter 'size' now has three options:
                        'FIT'   : max available size keaping aspect ratio (see param 'coordinates')
                        'FULL'  : max available size
                        (width, height)
2022/09/22 - 1.0.4 - Corregido create_filled_polygon(...)
2022/09/22 - 1.0.3 - Añade create_filled_polygon(...)
2022/09/22 - 1.0.2 - Añade create_polygon(...)
2022/09/01 - 1.0.1 - Biblioteca para crear ventanas con un lienzo.

@author: David Llorens
@contact: dllorens@uji.es
@copyright: Universitat Jaume I de Castelló (2024)
@licence: GNU Affero General Public License v3
"""

import tkinter
from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, cast

TVERSION = (1, 0, 10)
VERSION = '.'.join([str(e) for e in TVERSION])

DEFAULT_CANVAS_WIDTH = 500
DEFAULT_CANVAS_HEIGHT = 500


class _PostscriptCanvas(Protocol):
    def postscript(self, *, height: int, width: int, pagewidth: str) -> str: ...


class _MovableCanvas(Protocol):
    def move(self, tag: str | int, x: float, y: float) -> None: ...


class EasyPaintException(Exception):
    def __init__(self, message: str, value: object = None) -> None:
        self.value = value
        self.message = message
        super().__init__(self.message)


class EasyPaint(ABC):
    __slots__ = ('_title', '_background', '_root', '_canvas',
                 '_width', '_height', '_xscale', '_yscale',
                 '_left', '_right', '_top', '_bottom', '_screensize', 'closing')

    _title: str
    _background: str
    _root: tkinter.Tk
    _canvas: tkinter.Canvas
    _width: int
    _height: int
    _xscale: float
    _yscale: float
    _left: float
    _right: float
    _top: float
    _bottom: float
    _screensize: tuple[int, int]
    closing: bool

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._root.title(self._title)

    @property
    def size(self) -> tuple[int, int]:
        return self._width, self._height

    @size.setter
    def size(self, value: tuple[int, int] | str):
        self.erase()

        self._width, self._height = self._calc_size(value)
        self._set_scale()

        self._canvas.configure(width=min(self._width, self._screensize[0]),
                               height=min(self._height, self._screensize[1]))
        
    @property
    def coordinates(self) -> tuple[float, float, float, float]:
        return self._left, self._bottom, self._right, self._top

    @coordinates.setter
    def coordinates(self, value: tuple[float, float, float, float]):
        self.erase()

        self._left, self._bottom, self._right, self._top = value
        self._set_scale()

    @property
    def background(self) -> str:
        return self._background

    @background.setter
    def background(self, value: str) -> None:
        self._background = value
        self._canvas.configure(background=value)

    @property
    def left(self) -> float:
        return self._left

    @property
    def right(self) -> float:
        return self._right

    @property
    def top(self) -> float:
        return self._top

    @property
    def bottom(self) -> float:
        return self._bottom

    @property
    def scale(self) -> tuple[float, float]:
        return self._xscale, self._yscale

    @property
    def center(self) -> tuple[float, float]:
        return (self._right + self._left) / 2, (self._top + self._bottom) / 2

    def __init__(self) -> None:
        self.closing = False

        self._background = 'white'

        self._width, self._height = DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
        self._left, self._bottom, self._right, self._top = 0, 0, self._width - 1, self._height - 1
        self._set_scale()

        self._root = tkinter.Tk()
        self._screensize = self._root.maxsize()
        self.title = 'EasyPaint'
        self._root.resizable(width=False, height=False)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root.bind('<KeyPress>', lambda e: self.on_key_press(e.keysym))
        self._root.bind('<KeyRelease>', lambda e: self.on_key_release(e.keysym))

        self._canvas = tkinter.Canvas(self._root, borderwidth=0, highlightthickness=0,
                                      height=self._height, width=self._width, background=self._background)
        self._canvas.pack(padx=0, pady=0)
        self._canvas.bind('<Button>', self._on_mouse_button)
        self._canvas.bind('<ButtonRelease>', self._on_mouse_release)
        self._canvas.bind('<B1-Motion>', lambda e: self._on_mouse_motion(1, e))
        self._canvas.bind('<B2-Motion>', lambda e: self._on_mouse_motion(2, e))
        self._canvas.bind('<B3-Motion>', lambda e: self._on_mouse_motion(3, e))
        self._canvas.bind('<Leave>', self.on_mouse_leave)

    def easypaint_configure(self, size: tuple[int, int] | str = 'FIT',
                            coordinates: tuple[float, float, float, float] | None = None,
                            title: str = 'EasyPaint',
                            background: str = 'white') -> None:
        """Configure the window

        Arguments:
            size -- 'FIT'   : max available size keeping aspect ratio (see param 'coordinates')
                    'FULL'  : max available size
                    (width, height)

                When coordinates is None, 'FIT' uses the same fallback as 'FULL'.

            coordinates -- (left, bottom, right, top). Default is (0, 0, width-1, height-1)

            title -- window title. Default is 'EasyPaint'

            background -- color name. Default is 'white'
        """
        
        if self.closing: 
            return

        self.erase()

        self.title = title

        self._background = background
        
        if coordinates is None:
            if isinstance(size, tuple):
                ww, hh = size
            else:
                ww, hh = self._screensize
            self._left, self._bottom, self._right, self._top = 0, 0, ww - 1, hh - 1
        else:
            self._left, self._bottom, self._right, self._top = coordinates
        self._width, self._height = self._calc_size(size)
        self._set_scale()

        self._canvas.configure(width=min(self._width, self._screensize[0]),
                               height=min(self._height, self._screensize[1]),
                               background=self._background)

    # PRIVATE METHODS ----------------------------------------------------------------

    def _calc_size(self, value: object) -> tuple[int, int]:
        msg = "easypaint_configure: Parameter 'size' must be a tuple of two integers greater than 0 or 'FIT' or 'FULL'"
        if isinstance(value, str):
            if value == 'FULL':
                size_t = self._screensize
            elif value == 'FIT':
                l, b, r, t = self.coordinates
                ar = abs(r - l)/abs(t - b)

                size_t = self._screensize
                ar2 = size_t[0]/size_t[1]
                if ar < ar2:
                    size_t = int(ar*size_t[1]), size_t[1]
                elif ar > ar2:
                    size_t = size_t[0], int(size_t[0]/ar)
            else:
                raise EasyPaintException(msg)
        elif isinstance(value, tuple):
            size_pair = cast(tuple[Any, Any], value)
            if (
                len(size_pair) == 2
                and isinstance(size_pair[0], int)
                and isinstance(size_pair[1], int)
                and size_pair[0] > 0
                and size_pair[1] > 0
            ):
                size_t = cast(tuple[int, int], size_pair)
            else:
                raise EasyPaintException(msg)
        else:
            raise EasyPaintException(msg)    
        return size_t
    
    def _set_scale(self) -> None:
        ww = self._right - self._left
        if ww == 0:
            raise EasyPaintException(
                f"Degenerate coordinates: left and right are equal ({self._left}, {self._right})"
            )
        iw = 1 if ww >= 0 else -1
        self._xscale = self._width / float(ww + iw)
        hh = self._top - self._bottom
        if hh == 0:
            raise EasyPaintException(
                f"Degenerate coordinates: bottom and top are equal ({self._bottom}, {self._top})"
            )
        ih = 1 if hh >= 0 else -1
        self._yscale = self._height / float(hh + ih)

    def _canvas_postscript(self) -> str:
        return cast(_PostscriptCanvas, self._canvas).postscript(height=self._height, width=self._width,
                                                                pagewidth='20.0c')

    def _canvas_move(self, tag: str | int, x: float, y: float) -> None:
        cast(_MovableCanvas, self._canvas).move(tag, x, y)

    def _transform(self, x: float, y: float) -> tuple[int, int]:
        xb = int((x - self._left) * self._xscale)
        yb = int((self._top - y) * self._yscale)
        return xb, yb

    def _transform_x(self, x: float) -> int:
        return int((x - self._left) * self._xscale)

    def _transform_y(self, y: float) -> int:
        return int((self._top - y) * self._yscale)

    def _on_mouse_release(self, event: tkinter.Event) -> None:
        if self.closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_release(event.num, x, y)

    def _on_mouse_button(self, event: tkinter.Event) -> None:
        if self.closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_button(event.num, x, y)

    def _on_mouse_motion(self, button: int, event: tkinter.Event) -> None:
        if self.closing: return
        x = event.x / self._xscale + self._left
        y = self._top - event.y / self._yscale
        self.on_mouse_motion(button, x, y)

    # -----------------------------------------------------------------

    def on_mouse_release(self, button: int, x: float, y: float) -> None:
        pass

    def on_mouse_button(self, button: int, x: float, y: float) -> None:
        pass

    def on_mouse_motion(self, button: int, x: float, y: float) -> None:
        pass

    def on_mouse_leave(self, event: tkinter.Event) -> None:
        pass

    def on_key_press(self, keysym: str) -> None:
        pass

    def on_key_release(self, keysym: str) -> None:
        pass

    # -----------------------------------------------------------------

    def update(self) -> None:
        """Enter event loop until all pending events have been processed by Tcl.
        """
        if self.closing: return
        self._canvas.update()  # animaciones más suaves
        # self._canvas.update_idletasks()    # animaciones más bruscas y rapidas

    def create_rectangle(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black',
                         fill: str | None = None, **args: Any) -> int:
        """Draws a rectangle

        Arguments:
            x1, y1 -- lower left point coordinates

            x2, y2 -- upper right point coordinates

            color -- color name (default is 'black')

            fill -- fill color. Default is no fill.

        Returns:
            Canvas item identifier.
        """
        if self.closing:
            raise EasyPaintException("Cannot create rectangle: EasyPaint is closing")
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
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in {fn}: {(x1, y1, x2, y2)}")

        try:
            return self._canvas.create_rectangle(*(x1b, y1b, x2b, y2b), **args)
        except Exception as _e:
            raise EasyPaintException(f"{fn}")

    def create_filled_rectangle(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black',
                                fill: str | None = None, **args: Any) -> int:
        """Draws a filled rectangle.

        Arguments:
            x1, y1 -- lower left point coordinates

            x2, y2 -- upper right point coordinates

            color -- color name (default is 'black')

            fill -- color name (default is same as color)

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create filled rectangle: EasyPaint is closing")
        if fill is None: fill = color
        return self.create_rectangle(x1, y1, x2, y2, color, fill, **args)

    def create_circle(self, x: float, y: float, radius: float, color: str = 'black',
                      fill: str | None = None, **args: Any) -> int:
        """Draws a circle.

        Arguments:
            x, y -- point coordinates

            radius -- float

            color -- color name (default is 'black')

            fill -- fill color. Default is no fill.

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create circle: EasyPaint is closing")
        fn = 'create_circle' if fill is None else 'create_filled_circle'
        args['outline'] = color[:]
        if fill is not None: args['fill'] = fill[:]
        try:
            x1b, y1b = self._transform(x - radius, y - radius)
            x2b, y2b = self._transform(x + radius, y + radius)
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in {fn}: {(x, y)}")
        try:
            return self._canvas.create_oval(*(x1b, y1b, x2b, y2b), **args)
        except Exception as _e:
            raise EasyPaintException(f"{fn}")

    def create_filled_circle(self, x: float, y: float, radius: float, color: str = 'black',
                             fill: str | None = None, **args: Any) -> int:
        """Draws a filled circle.

        Arguments:
            x, y -- point coordinates

            radius -- float

            color -- color name (default is 'black')

            fill -- color name (default is same as color)

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create filled circle: EasyPaint is closing")
        if fill is None: fill = color
        return self.create_circle(x, y, radius, color, fill, **args)

    def create_polygon(self, *params: float, color: str = 'black', fill: str | None = None,
                       **args: Any) -> int:
        """Draws a polygon.

        Arguments:
            x0, y0, x1, y1, ...  -- point coordinates

            color -- outline color name (default is 'black')

            fill -- fill color. Default is no fill.

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create polygon: EasyPaint is closing")
        args['fill'] = '' if fill is None else fill
        args['outline'] = color
        try:
            params2 = [self._transform_x(e) if i % 2 == 0 else self._transform_y(e) for i, e in enumerate(params)]
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in create_polygon: {params}")
        try:
            return self._canvas.create_polygon(*params2, **args)
        except Exception as e:
            raise EasyPaintException(f"create_polygon: {e}")

    def create_filled_polygon(self, *params: float, color: str = 'black', fill: str | None = None,
                              **args: Any) -> int:
        """Draws a filled polygon.

        Arguments:
            x0, y0, x1, y1, ...  -- point coordinates

            color -- outline color name (default is 'black')

            fill -- color name (default is same as color)

        Returns:
            Canvas item identifier.
        """
        
        if self.closing: 
            raise EasyPaintException("Cannot create filled polygon: EasyPaint is closing")
        if fill is None:
            fill = color
        return self.create_polygon(*params, color=color, fill=fill, **args)

    def create_point(self, x: float, y: float, color: str = 'black', **args: Any) -> int:
        """Draws a point.

        Arguments:
            x, y -- point coordinates

            color -- color name (default is 'black')

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create point: EasyPaint is closing")
        args['fill'] = color[:]
        args['width'] = 2
        try:
            x1b, y1b = self._transform(x, y)
            x2b = x1b + 2
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in create_point: {(x, y)}")
        try:
            return self._canvas.create_line(*(x1b, y1b, x2b, y1b), **args)
        except Exception as _e:
            raise EasyPaintException("create_point")

    def create_line(self, x1: float, y1: float, x2: float, y2: float, color: str = 'black',
                    **args: Any) -> int:
        """Draws a line between two points.

        Arguments:
            x1, y1 -- start point coordinates
            x2, y2 -- end point coordinates
            color -- color name (default is 'black')

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create line: EasyPaint is closing")
        args['fill'] = color
        try:
            x1b, y1b = self._transform(x1, y1)
            x2b, y2b = self._transform(x2, y2)
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in create_line: {(x1, y1, x2, y2)}")
        try:
            # id = self.canvas.create_line(x1b, y1b, x2b, y2b, args.copy())
            return self._canvas.create_line(*(x1b, y1b, x2b, y2b), **args)
        except Exception as _e:
            raise EasyPaintException("create_line")

    def create_text(self, x: float, y: float, text: str, font_size: int = 10,
                    anchor: str = 'center', color: str = 'black', justify: str = "left",
                    **args: Any) -> int:
        """Draws a line of text.

        Arguments:
            x, y -- point coordinates

            text -- string

            font_size -- int (default is 10)

            anchor -- string (default is 'center')

            color -- color name (default is 'black')

            justify -- string (default is 'left')

        Returns:
            Canvas item identifier.
        """
        if self.closing: 
            raise EasyPaintException("Cannot create text: EasyPaint is closing")
        args['text'] = text
        args['anchor'] = anchor.lower()
        args['fill'] = color
        args['justify'] = justify
        args['font'] = ('courier', int(font_size * 1.15 + 2), 'bold')
        try:
            xb, yb = self._transform(x, y)
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in create_text: {(x, y)}")
        try:
            # return self.canvas.create_text(xb, yb, args)
            return self._canvas.create_text(*(xb, yb), **args)
        except Exception as _e:
            raise EasyPaintException("create_text")

    def erase(self, *param: str | int) -> None:
        """Remove one or more canvas items from the canvas.

        Uses:
                erase() -- clean the canvas

                erase(id1, id2, ...) -- remove several items

                erase(tag_or_id) -- remove a single item
        """
        if self.closing: return
        if len(param) == 0:  # Delete all elements
            try:
                for elem in self._canvas.find_all():
                    self._canvas.delete(elem)
            except tkinter.TclError:
                pass
        else:  # Delete single or multiple elements
            try:
                self._canvas.delete(*param)
            except Exception as _e:
                raise EasyPaintException(f"Wrong id in erase: {param}")

    def save_eps(self, nombre: str) -> int:
        """Write the current canvas contents to a PostScript file.

        Returns 1 on success and 0 on failure.
        """
        if self.closing: 
            raise EasyPaintException("Cannot save EPS: EasyPaint is closing")
        data = self._canvas_postscript()
        try:
            f = open(nombre, 'w')
            try:
                f.write(data)
            finally:
                f.close()
            res = 1
        except Exception as _e:
            res = 0
        return res

    def move(self, tag: str | int, x: float, y: float) -> None:
        """Move an item or tag by the given delta.
        """
        if self.closing: return
        try:
            xb = x * self._xscale
            yb = -y * self._yscale
        except Exception as _e:
            raise EasyPaintException(f"Wrong coordinates in move: x={x}, y={y}")
        try:
            self._canvas_move(tag, xb, yb)
        except Exception as _e:
            raise EasyPaintException("move")

    def close(self) -> None:
        """Terminates the program
        """
        if self.closing: return
        self.closing = True
        self._root.destroy()
        self._root.quit()

    def run(self) -> None:
        """ Launch the mainloop
        """
        if self.closing: return
        self.main()
        self._root.mainloop()

    def after(self, time: int, f: Callable[[], None]) -> None:
        """Call a callback once after the given delay.

        Arguments:
            time -- integer that specifies the time in milliseconds

            f -- the function which shall be called
        """
        if self.closing: return
        self._root.after(time, f)

    def tag_lower(self, tag: str | int) -> None:
        """Lower an item or tag in the z-order.
        """
        if self.closing: return
        self._canvas.tag_lower(tag)

    def tag_raise(self, tag: str | int) -> None:
        """Raise an item or tag in the z-order.
        """
        if self.closing: return
        self._canvas.tag_raise(tag)

    @abstractmethod
    def main(self) -> None:
        pass


# --------------------------------------------------------------------------


if __name__ == "__main__":
    class Demo(EasyPaint):
        def on_key_press(self, keysym: str) -> None:
            self.close()

        def main(self) -> None:
            """Run the small interactive example used for manual testing."""
            width = 400
            height = 300
            size = (width, height)  # (width, height) or 'FIT' or 'FULL'

            self.easypaint_configure(size=size, 
                                     coordinates=(0, height, width, 0))
            self.create_filled_rectangle(10, 10, width - 10, height - 10, "black", "white")
            x, y = self.center
            self.create_text(x, y, "To exit press any key\nor\nclose the window", 14, justify="center")
            #self.save_eps("kk.eps")


    Demo().run()
