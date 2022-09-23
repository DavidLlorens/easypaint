#!/usr/bin/env python3
"""
Created on 28/09/2021

@author: David Llorens
@contact: dllorens@lsi.uji.es
@copyright: Universitat Jaume I de Castelló (2021)
"""
from math import sin, cos, pi

from easypaint import EasyPaint


def rueda(x0, y0, radio, num_dientes, prof_diente, ini):
    r1 = radio - prof_diente / 2.0
    r2 = radio + prof_diente / 2.0
    values = []
    da = 2.0 * pi / num_dientes / 4.0
    cte = 2.0 * pi / num_dientes
    ini = ini - da * 3 / 2
    for i in range(0, num_dientes):
        angle = i * cte + ini
        values.append((r1 * cos(angle) + x0, r1 * sin(angle) + y0))
        values.append((r2 * cos(angle + da) + x0, r2 * sin(angle + da) + y0))
        values.append((r2 * cos(angle + 2 * da) + x0, r2 * sin(angle + 2 * da) + y0))
        values.append((r1 * cos(angle + 3 * da) + x0, r1 * sin(angle + 3 * da) + y0))
    return values + [values[0]]


def mcm(i, j):
    while 1:
        r = i % j
        if r == 0: return j
        i, j = j, r


class Demo6(EasyPaint):
    rold = []
    # Cambiando estos valores se obtiene dibujos diferentes
    radioCirculo = 200
    radioDisco = 75
    distLapizCentroDisco = 50
    velocidad = 0.04  # reducir para aumentar velocidad
    dientesCirculo = 40  # no es necesario cambiar este valor

    def spyro(self, a, b, rd, di):
        def anim(cc):
            nonlocal ang, theta, x2, y2, xx2, yy2, o_id
            ang += 1
            theta += thetad
            phi = -ang * inc
            xx, yy = rab * cos(theta), rab * sin(theta)
            x, y = xx + rd * cos(phi), yy - rd * sin(phi)
            self.create_line(x, y, x2, y2)
            self.move('lapiz', x - x2, y - y2)
            c = rueda(xx, yy, b - prof_d / 2, n2, prof_d, -phi)
            self.dibuja_rueda(c, 'blue')
            self.move('disco', xx - xx2, yy - yy2)
            self.erase(o_id)
            o_id = self.create_line(x, y, xx, yy, 'blue')
            x2, y2 = x, y
            xx2, yy2 = xx, yy
            self.update()
            # time.sleep(self.velocidad)
            if cc > 0:
                self.after(int(self.velocidad * 1000), lambda: anim(cc - 1))

        prof_d = 10  # profundidad diente
        self.create_filled_circle(0, 0, 3, 'red')
        xx2, yy2 = a - b, 0
        print("Tamaño diente: %g" % (float(a) / di))
        print("Nº dientes agujero:", di)
        o_id = rueda(0, 0, a - prof_d / 2, di, prof_d, 0)
        self.dibuja_rueda(o_id, 'red')
        self.rold = []  # para que no se borre la rueda roja (es fija)
        n2 = int(di * float(b) / a)
        print("Nº dientes disco:", n2)
        b2 = n2 * float(a) / di
        if b2 != b:
            print("Ajustado radio del disco: %g -> %g" % (b, b2))
            b = b2

        rab = (a - b)
        o_id = rueda(rab, 0, b - prof_d / 2, n2, prof_d, 0)
        self.dibuja_rueda(o_id, 'blue')
        self.create_filled_circle(rab, 0, 3, 'blue', tags='disco')
        self.create_filled_circle(rab + rd, 0, 3, 'black', tags='lapiz')
        theta = 0.0
        thetad = pi * 0.02  # 12#52
        n = n2 / mcm(di, n2)
        print("Vueltas:", n)
        x2, y2 = rab + rd, 0.0
        ang = 0
        inc = -((di - n2) * (2 * pi / n2)) / 100
        o_id = self.create_line(x2, y2, xx2, yy2, 'blue')
        self.after(0, lambda: anim(int(100 * n)))

    def dibuja_rueda(self, o_id, color):
        r = []
        x2, y2 = o_id[0]
        for x, y in o_id[1:]:
            r.append(self.create_line(x, y, x2, y2, color))
            if len(self.rold) > 0:
                self.erase(self.rold[0])
                del self.rold[0]
            x2, y2 = x, y
        self.erase(self.rold)
        self.rold = r

    def on_key_press(self, keysym):
        self.close()

    def main(self):
        self.easypaint_configure(title='Demo 6 - Spyro',
                                 background='white',
                                 size=(600, 600),
                                 coordinates=(-250, -250, 250, 250))
        self.spyro(self.radioCirculo, self.radioDisco, self.distLapizCentroDisco, self.dientesCirculo)

        self.create_text(0, -250, "Press any key to exit", 12, 's')


Demo6().run()
