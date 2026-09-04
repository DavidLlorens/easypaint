# EasyPaint

Biblioteca de dibujo para Python 3.12 o superior.

## Instalación

El paquete publicado se instala con `pip`:

```bash
pip install easypaint
```

Si estás trabajando desde este repositorio, puedes instalarlo en modo editable:

```bash
pip install -e .
```

Requiere que la biblioteca *tkinter* esté instalada:
- En MS Windows se incluye con la instalación de Python.
- En Ubuntu hay que instalar el paquete *python3-tk*.

## Uso rápido

La librería expone una clase base `EasyPaint` para crear ventanas con un lienzo coordenado. Se usa heredando la clase y definiendo el método `main()`:

```python
from easypaint import EasyPaint


class Demo(EasyPaint):
    def main(self) -> None:
        self.easypaint_configure(size=(400, 300), coordinates=(0, 0, 399, 299))
        self.create_text(200, 150, "Hola EasyPaint", 16, justify="center")


Demo().run()
```

Si prefieres probar la biblioteca sin escribir código propio, puedes lanzar cualquiera de las demos del directorio [src/easypaint/demos/](src/easypaint/demos/).

## Notas técnicas

- El proyecto necesita Python 3.12 o superior.
- El paquete publicado en `pip` es `easypaint`.
- La implementación depende de `tkinter`, así que en sistemas Unix puede ser necesario instalar el paquete del sistema.

