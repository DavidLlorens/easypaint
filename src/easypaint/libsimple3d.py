'''
Created on 22/10/2021

@author: David Llorens
@contact: dllorens@uji.es
@copyright: Universitat Jaume I de Castelló (2021)
@licence: GNU Affero General Public License v3
'''

# Descripción: Módulo para dibujar objetos 3D simples en EasyPaint.
#              Todavía muy optimizable.
#              El algoritmo de ocultación de lineas es la versión
#              Python del que aparece en el libro 'Gráficos por
#              Computador' de Ian O. Angell.
# Versión: 0.2 (beta)

from __future__ import annotations

import copy
import types
from math import cos, sin, atan2, sqrt
from dataclasses import dataclass
from typing import Callable, overload

epsilon = 0.000001
epsilon1 = 1 + epsilon

OCULTAR_NO = 0
OCULTAR_SI = 1
OCULTAR_CARAS_TRASERAS = 2


@dataclass
class CaraP:
    lInd: list[int]
    visible: int = 1


class Escena3D:
    o: list[Objeto3D]
    lin: list[tuple[float, float, float, float, str]]
    ppd: int
    dist: float
    ocultar: int
    verb: int

    def __init__(self, ppd: int = 600, ocultar: int = OCULTAR_SI, verb: int = 0) -> None:
        self.o: list[Objeto3D] = []
        self.lin: list[tuple[float, float, float, float, str]] = []
        self.ppd: int = ppd
        self.dist: float = 0.0
        self.ocultar: int = ocultar
        self.verb: int = verb

    def insertar(self, o: Objeto3D) -> None:
        self.o.append(o)

    def transforma3d(self, m: Matriz3D) -> None:
        for obj in self.o:
            obj.transforma3d(m)

    def puntoVista(self, pv: Punto3D, ppd: int | None = None) -> None:
        if ppd != None: self.ppd = ppd
        x, y, z = pv.x, pv.y, pv.z
        m = Matriz3D()
        m.traslacion(-x, -y, -z)
        rho = atan2(x, z)
        m.rotacionY(rho)
        phi = atan2(y, sqrt(x * x + z * z))
        m.rotacionX(-phi)
        self.transforma3d(m)

    def puntoVistaObj(self, pv: Punto3D, obj: Objeto3D, ppd: int | None = None) -> None:
        if ppd != None: self.ppd = ppd
        x, y, z = pv.x, pv.y, pv.z
        m = Matriz3D()
        m.traslacion(-x, -y, -z)
        rho = atan2(x, z)
        m.rotacionY(rho)
        phi = atan2(y, sqrt(x * x + z * z))
        m.rotacionX(-phi)
        obj.transforma3d(m)

    def dibuja(self) -> list[tuple[float, float, float, float, str]]:
        a = len(self.o)
        self.lin = []
        verb = self.verb
        if self.ocultar == OCULTAR_SI:
            no = 1
            if verb:
                print("\nverb: Obteniendo caras visibles:")
            for obj in self.o:
                if verb:
                    print("verb: Objeto %d de %d" % (no, a))
                    no += 1
                obj.averiguarCarasVisibles(self.verb)
                obj.proyectarSiVisible(self.ppd, self.dist)
            if verb:
                print("\nverb: Obteniendo segmentos de línea visibles:")
            no = 1
            for obj in self.o:
                if verb:
                    print("verb: Objeto %d de %d" % (no, a))
                    no += 1
                lineas = obj.lineasR[1:]
                nl = 1
                old = -1
                for milinea in lineas:
                    if verb:
                        new = int(nl * 100.0 / len(lineas))
                        if new % 10 == 0 and new != old:
                            print("verb:     líneas %d%%" % (new))
                        nl += 1
                        old = new
                    pp1, pp2 = milinea
                    p1 = obj.puntos3dT[pp1]
                    p2 = obj.puntos3dT[pp2]
                    if not (p1.visible and p2.visible): continue
                    seg = self._oculta(p1, p2, milinea, obj)
                    self.lin.extend(seg)
        elif self.ocultar == OCULTAR_CARAS_TRASERAS:
            no = 1
            if verb:
                print("\nverb: Obteniendo caras visibles:")
            for obj in self.o:
                if verb:
                    print("verb: Objeto %d de %d" % (no, a))
                    no += 1
                obj.averiguarCarasVisibles(self.verb)
                obj.proyectarSiVisible(self.ppd, self.dist)
            for obj in self.o:
                if verb:
                    print("verb: Objeto %d de %d" % (no, a))
                    no += 1
                # obj.proyectar(self.ppd,self.dist)
                lineas = obj.lineasR[1:]
                nl = 0
                old = -1
                for pp1, pp2 in lineas:
                    if verb:
                        new = int(nl * 100.0 / len(lineas) + 0.5)
                        if new % 10 == 0 and old != new:
                            print("verb:     líneas %d%%" % (new))
                        old = new
                        nl += 1
                    try:
                        x1, y1 = obj.puntos3dT[pp1].proy
                        x2, y2 = obj.puntos3dT[pp2].proy
                        self.lin.append((x1, y1, x2, y2, obj.color))
                    except:
                        pass
        else:
            no = 1
            for obj in self.o:
                if verb:
                    print("verb: Objeto %d de %d" % (no, a))
                    no += 1
                obj.proyectar(self.ppd, self.dist)
                lineas = obj.lineasR[1:]
                nl = 0
                old = -1
                for pp1, pp2 in lineas:
                    if verb:
                        new = int(nl * 100.0 / len(lineas) + 0.5)
                        if new % 10 == 0 and old != new:
                            print("verb:     líneas %d%%" % (new))
                        old = new
                        nl += 1
                    x1, y1 = obj.puntos3dT[pp1].proy
                    x2, y2 = obj.puntos3dT[pp2].proy
                    self.lin.append((x1, y1, x2, y2, obj.color))
        return self.lin

    def _oculta(self, p1: Punto3D, p2: Punto3D, mi_linea: tuple[int, int], mi_obj: Objeto3D) -> list[tuple[float, float, float, float, str]]:
        x1, y1 = p1.proy
        x2, y2 = p2.proy
        rm = [[0.0, 1.0]]
        segmentos: list[tuple[float, float, float, float, str]] = []
        xd, yd = x2 - x1, y2 - y1
        for obj in self.o:
            l = list(range(len(obj.carasP)))
            for i in l:
                if obj.carasP[i].visible == 0: continue  # mira si es visible
                ok = 0
                if obj is mi_obj:
                    cx = obj.caras[i]
                    for x in cx:
                        if mi_linea == obj.lineasR[abs(x)]:
                            ok = 1
                            break
                    if ok: continue
                c = obj.carasP[i].lInd
                cc = c + [c[0]]
                # Posibilidad A)
                xx1, yy1 = obj.puntos3dT[c[0]].proy
                fval = (yy1 - y1) * xd - (xx1 - x1) * yd
                if fval > 0:
                    fval = 1
                elif fval < 0:
                    fval = -1
                else:
                    fval = 0
                if fval != 0:
                    ok = 1
                    for p in cc[1:]:
                        xx1, yy1 = obj.puntos3dT[p].proy
                        fval2 = (yy1 - y1) * xd - (xx1 - x1) * yd
                        if fval2 > 0:
                            fval2 = 1
                        elif fval2 < 0:
                            fval2 = -1
                        else:
                            fval2 = 0
                        if fval - fval2 != 0:
                            ok = 0
                            break
                    if ok: continue
                # Posibilidad B)
                gval = (y2 - y1) * yd + (x2 - x1) * xd
                if gval > 0:
                    gval = 1
                elif gval < 0:
                    gval = -1
                else:
                    gval = 0
                if gval != 0:
                    ok = 1
                    for p in cc:
                        xx1, yy1 = obj.puntos3dT[p].proy
                        gval2 = (yy1 - y1) * yd + (xx1 - x1) * xd
                        if gval2 > 0:
                            gval2 = 1
                        elif gval2 < 0:
                            gval2 = -1
                        else:
                            gval2 = 0
                        if abs(gval - gval2) < 1.1:
                            ok = 0
                            break
                    if ok: continue
                # Posibilidad C)
                hval = (y1 - y2) * yd + (x1 - x2) * xd
                if hval > 0:
                    hval = 1
                elif hval < 0:
                    hval = -1
                else:
                    hval = 0
                if hval != 0:
                    ok = 1
                    for p in cc:
                        xx1, yy1 = obj.puntos3dT[p].proy
                        hval2 = (yy1 - y2) * yd + (xx1 - x2) * xd
                        if hval2 > 0:
                            hval2 = 1
                        elif hval2 < 0:
                            hval2 = -1
                        else:
                            hval2 = 0
                        if abs(hval - hval2) < 1.1:
                            ok = 0
                            break
                    if ok: continue
                #
                # Averiguar dos puntos de interseccion
                #
                rmax, rmin = 0.0, 1.0
                xx2, yy2 = obj.puntos3dT[c[0]].proy
                for p in cc[1:]:
                    xx1, yy1 = xx2, yy2
                    xx2, yy2 = obj.puntos3dT[p].proy
                    xe, ye = xx1 - xx2, yy1 - yy2
                    xf, yf = xx1 - x1, yy1 - y1
                    disk = xd * ye - xe * yd
                    if abs(disk) < epsilon:
                        # Si linea solapa una linea de la cara, salir bucle cara
                        if abs(xd) > epsilon:
                            xsi = xf / xd
                            if abs(yf - xsi * yd) < epsilon:
                                ok = 1
                                break
                        elif abs(xf) < epsilon:
                            ok = 1
                            break
                    else:
                        xsi = (xd * yf - yd * xf) / disk
                        # Si linea evita la cara salir bucle cara
                        if xsi < -epsilon or xsi > epsilon1: continue
                        rmu = (ye * xf - xe * yf) / disk
                        rmax, rmin = max(rmax, rmu), min(rmin, rmu)
                if ok: continue
                #
                if rmin > 1.0 or rmax < 0.0: continue
                rmax, rmin = min(1.0, rmax), max(0.0, rmin)
                if rmax - rmin <= 0.0: continue
                # Averiguar xmid y ymid
                rmid = (rmax + rmin) * 0.5
                rxx = 1.0 - rmid
                xmid = rxx * x1 + rmid * x2
                ymid = rxx * y1 + rmid * y2
                # Averiguar xhat, yhat y zhat del valor de phi
                denom = self.ppd * (p2.x - p1.x) - xmid * (p2.z - p1.z)
                if abs(denom) < epsilon:
                    denom = self.ppd * (p2.y - p1.y) - ymid * (p2.z - p1.z)
                    phi = (ymid * (p1.z + self.dist) - self.ppd * p1.y) / denom
                else:
                    phi = (xmid * (p1.z + self.dist) - self.ppd * p1.x) / denom
                zhat = (1.0 - phi) * p1.z + phi * p2.z
                ddd = (zhat + self.dist) / self.ppd
                xhat = xmid * ddd
                yhat = -ymid * ddd
                # calcular coef. plano a.x+b.y+c.z=d
                p1b = obj.puntos3dT[c[0]]
                p2b = obj.puntos3dT[c[1]]
                p3b = obj.puntos3dT[c[2]]
                dx1 = p1b.x - p2b.x
                dy1 = p1b.y - p2b.y
                dz1 = p1b.z - p2b.z
                dz3 = p3b.z - p2b.z
                dy3 = p3b.y - p2b.y
                dx3 = p3b.x - p2b.x
                a = dy1 * dz3 - dy3 * dz1
                b = dz1 * dx3 - dz3 * dx1
                c = dx1 * dy3 - dx3 * dy1
                d = a * p1b.x + b * p1b.y + c * p1b.z
                f1 = a * xhat + b * yhat + c * zhat - d
                if abs(f1) < epsilon: continue
                if f1 > 0:
                    f1 = 1
                elif f1 < 0:
                    f1 = -1
                else:
                    f1 = 0
                f2 = -self.dist * c - d
                if f2 > 0:
                    f2 = 1
                elif f2 < 0:
                    f2 = -1
                else:
                    f2 = 0
                if abs(f1 - f2) <= 1.0: continue
                # parte de la linea está oculta
                lrm = len(rm)
                for ii in range(lrm):
                    r1, r2 = rm[ii]
                    if r1 > rmax or r2 < rmin:
                        continue
                    elif r1 >= rmin and r2 <= rmax:
                        rm[ii][0] = -1.0
                    elif r1 < rmin:
                        if r2 > rmax: rm.append([rmax, r2])
                        rm[ii][1] = rmin
                    else:
                        rm[ii][0] = rmax
                # limpiar rm
                rm2: list[list[float]] = []
                for r1, r2 in rm:
                    if r1 >= 0.0: rm2.append([r1, r2])
                if len(rm2) == 0: return []
                rm = rm2
        for s in rm:
            r1 = s[0]
            r2 = 1.0 - r1
            xp1 = x1 * r2 + x2 * r1
            yp1 = y1 * r2 + y2 * r1
            r1 = s[1]
            r2 = 1.0 - r1
            xp2 = x1 * r2 + x2 * r1
            yp2 = y1 * r2 + y2 * r1
            if (xp1 - xp2) != 0.0 and (yp1 - yp2) != 0.0:
                segmentos.append((xp1, yp1, xp2, yp2, mi_obj.color))
        return segmentos


class Objeto3D:
    puntos3d: list[Punto3D]
    puntos3dT: list[Punto3D]
    caras: list[list[int]]
    carasP: list[CaraP]
    lineas: dict[tuple[int, int], int]
    lineasR: list[tuple[int, int]]
    lin: list[tuple[float, float, float, float, str]]
    numLin: int
    color: str

    def __init__(self, puntos3d: list[Punto3D], caras: list[list[int]] | None = None,
                 carasP: list[CaraP] | None = None,
                 lineas: dict[tuple[int, int], int] | None = None,
                 lineasR: list[tuple[int, int]] | None = None,
                 color: str = 'black') -> None:
        self.puntos3d: list[Punto3D] = copy.deepcopy(puntos3d)
        self.puntos3dT: list[Punto3D] = []  # [0.0]*len(self.puntos3d)
        self.caras: list[list[int]] = copy.deepcopy(caras) if caras is not None else []
        self.carasP: list[CaraP] = copy.deepcopy(carasP) if carasP is not None else []
        self.lineas: dict[tuple[int, int], int] = copy.deepcopy(lineas) if lineas is not None else {}
        self.lineasR: list[tuple[int, int]] = copy.deepcopy(lineasR) if lineasR is not None else [(0, 0)]
        self.lin: list[tuple[float, float, float, float, str]] = []
        self.numLin: int = 1  # tiene 1 de mas
        self.color: str = color
        if not self.carasP or not self.lineas or self.lineasR == [(0, 0)]:
            for c in self.caras: self.nuevaCara(c)

    def setup(self) -> None:
        self.puntos3d = copy.deepcopy(self.puntos3dT)

    def copia(self) -> Objeto3D:
        return Objeto3D(self.puntos3d, self.caras, self.carasP,
                        self.lineas, self.lineasR, self.color)

    def nuevaCara(self, lInd: list[int]) -> None:
        self.carasP.append(CaraP(lInd[:], 1))
        cara: list[int] = []
        aux = lInd[1:] + [lInd[0]]
        pOld = lInd[0]
        for p in aux:
            try:
                lin = self.lineas[(pOld, p)]
            except:
                try:
                    lin = -self.lineas[(p, pOld)]
                except:
                    self.lineas[(pOld, p)] = lin = self.numLin
                    self.lineasR.append((pOld, p))
                    self.numLin += 1
            cara.append(lin)
            pOld = p
        self.caras.append(cara)

    def transforma3d(self, m: Matriz3D) -> None:
        self.puntos3dT = []
        aux: Callable[[Punto3D], None] = self.puntos3dT.append
        for punto in self.puntos3d:
            aux(m * punto)
        # for i in range(len(self.puntos3d)):
        #    self.puntos3dT[i] = m*self.puntos3d[i]

    def proyectar(self, ppd: float, dist: float = 0.0) -> None:
        for p3d in self.puntos3dT:
            dd = ppd / (p3d.z + dist)
            p3d.proy = (p3d.x * dd, -p3d.y * dd)

    def proyectarSiVisible(self, ppd: float, dist: float = 0.0) -> None:
        L = iter([p for p in self.puntos3dT if p.visible])
        for p3d in L:
            dd = ppd / (p3d.z + dist)
            p3d.proy = (p3d.x * dd, -p3d.y * dd)

    def averiguarCarasVisibles(self, verb: int = 0) -> None:
        aux = self.puntos3dT
        for p in self.puntos3dT: p.visible = 0
        nc = 0
        old = -1
        for cc in self.carasP:
            if verb:
                new = int(nc * 100.0 / len(self.carasP))
                if new % 10 == 0 and new != old:
                    print("verb:     caras %d%%" % new)
                old = new
                nc += 1
            c = cc.lInd
            p = aux[c[1]]
            v1 = aux[c[0]] - p  # de 1 a 0
            # normaliza v1
            longx = sqrt(v1.x * v1.x + v1.y * v1.y + v1.z * v1.z)
            v1.x /= longx;
            v1.y /= longx;
            v1.z /= longx

            v2 = aux[c[2]] - p  # de 1 a 2
            # normaliza v2
            longx = sqrt(v2.x * v2.x + v2.y * v2.y + v2.z * v2.z)
            v2.x /= longx;
            v2.y /= longx;
            v2.z /= longx

            if (v1 ** v2) * p > 0:  # cara invisible
                cc.visible = 0
            else:  # cara visible
                cc.visible = 1
                for pp in c:  # marcamos puntos visibles
                    aux[pp].visible = 1


class Punto3D:
    x: float
    y: float
    z: float
    fx: Callable[[float], float] | None
    fy: Callable[[float], float] | None
    fz: Callable[[float], float] | None
    proy: tuple[float, float]
    visible: int

    @overload
    def __init__(self, x: Callable[[float], float], y: Callable[[float], float],
                 z: Callable[[float], float]) -> None:
        ...

    @overload
    def __init__(self, x: float, y: float, z: float) -> None:
        ...

    def __init__(self, x: float | Callable[[float], float], y: float | Callable[[float], float],
                 z: float | Callable[[float], float]) -> None:
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.fx = None
        self.fy = None
        self.fz = None
        self.proy: tuple[float, float] = (0.0, 0.0)
        self.visible: int = 0
        if isinstance(x, types.FunctionType):
            assert isinstance(y, types.FunctionType) and isinstance(z, types.FunctionType)
            self.fx = x
            self.fy = y
            self.fz = z
            self.posParametrica(0.0)
        else:
            assert isinstance(x, (float, int)) and isinstance(y, (float, int)) and isinstance(z, (float, int))
            self.x = x
            self.y = y
            self.z = z

    def __add__(self, otro: Punto3D) -> Punto3D:
        x = self.x + otro.x
        y = self.y + otro.y
        z = self.z + otro.z
        return Punto3D(x, y, z)

    def __sub__(self, otro: Punto3D) -> Punto3D:
        x = self.x - otro.x
        y = self.y - otro.y
        z = self.z - otro.z
        return Punto3D(x, y, z)

    def __pow__(self, otro: Punto3D) -> Punto3D:
        # <x1,y1,z1> X <x2,y2,z2> = <y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2>
        x = self.y * otro.z - self.z * otro.y
        y = self.z * otro.x - self.x * otro.z
        z = self.x * otro.y - self.y * otro.x
        return Punto3D(x, y, z)

    def posParametrica(self, t: float) -> None:
        fx = self.fx
        fy = self.fy
        fz = self.fz
        assert fx is not None and fy is not None and fz is not None
        self.x = fx(t)
        self.y = fy(t)
        self.z = fz(t)

    def __mul__(self, otro: Punto3D) -> float:
        return (self.x * otro.x + self.y * otro.y + self.z * otro.z)

    def __str__(self) -> str:
        return '[%.2f %.2f %.2f]' % (self.x, self.y, self.z)

    def __repr__(self) -> str:
        return self.__str__()


class Matriz3D:
    mat: list[list[float]]

    def __init__(self, ini: list[list[float]] | None = None) -> None:
        if ini == None:
            self.mat = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]
        else:
            self.mat = copy.deepcopy(ini)

    def puntoVista(self, pv: Punto3D) -> None:
        x, y, z = pv.x, pv.y, pv.z
        self.traslacion(-x, -y, -z)
        rho = atan2(x, z)
        self.rotacionY(rho)
        phi = atan2(y, sqrt(x * x + z * z))
        self.rotacionX(-phi)

    def identidad(self) -> None:
        self.mat = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]

    def rotacionX(self, a: float) -> None:
        ca = cos(a)
        sa = sin(a)
        res = Matriz3D(self.mat)
        m0, m1, m2, m3 = self.mat
        r0, r1, r2, r3 = res.mat
        r0[1] = m0[1] * ca + m0[2] * sa
        r0[2] = m0[2] * ca - m0[1] * sa
        r1[1] = m1[1] * ca + m1[2] * sa
        r1[2] = m1[2] * ca - m1[1] * sa
        r2[1] = m2[1] * ca + m2[2] * sa
        r2[2] = m2[2] * ca - m2[1] * sa
        r3[1] = m3[1] * ca + m3[2] * sa
        r3[2] = m3[2] * ca - m3[1] * sa
        self.mat = res.mat

    def rotacionY(self, a: float) -> None:
        res = Matriz3D(self.mat)
        ca = cos(a)
        sa = sin(a)
        m0, m1, m2, m3 = self.mat
        r0, r1, r2, r3 = res.mat
        r0[0] = m0[0] * ca - m0[2] * sa
        r0[2] = m0[0] * sa + m0[2] * ca
        r1[0] = m1[0] * ca - m1[2] * sa
        r1[2] = m1[0] * sa + m1[2] * ca
        r2[0] = m2[0] * ca - m2[2] * sa
        r2[2] = m2[0] * sa + m2[2] * ca
        r3[0] = m3[0] * ca - m3[2] * sa
        r3[2] = m3[0] * sa + m3[2] * ca
        self.mat = res.mat

    def rotacionZ(self, a: float) -> None:
        res = Matriz3D(self.mat)
        ca = cos(a)
        sa = sin(a)
        m0, m1, m2, m3 = self.mat
        r0, r1, r2, r3 = res.mat
        r0[0] = m0[0] * ca + m0[1] * sa
        r0[1] = m0[1] * ca - m0[0] * sa
        r1[0] = m1[0] * ca + m1[1] * sa
        r1[1] = m1[1] * ca - m1[0] * sa
        r2[0] = m2[0] * ca + m2[1] * sa
        r2[1] = m2[1] * ca - m2[0] * sa
        r3[0] = m3[0] * ca + m3[1] * sa
        r3[1] = m3[1] * ca - m3[0] * sa
        self.mat = res.mat

    def escalado(self, x: float, y: float, z: float) -> None:
        rot = Matriz3D([[x, 0.0, 0.0, 0.0],
                        [0.0, y, 0.0, 0.0],
                        [0.0, 0.0, z, 0.0],
                        [0.0, 0.0, 0.0, 1.0]])
        self.mat = self.__mul__(rot).mat

    def traslacion(self, x: float, y: float, z: float) -> None:
        m0, m1, m2, m3 = self.mat
        m0[0] += m0[3] * x
        m0[1] += m0[3] * y
        m0[2] += m0[3] * z
        m1[0] += m1[3] * x
        m1[1] += m1[3] * y
        m1[2] += m1[3] * z
        m2[0] += m2[3] * x
        m2[1] += m2[3] * y
        m2[2] += m2[3] * z
        m3[0] += m3[3] * x
        m3[1] += m3[3] * y
        m3[2] += m3[3] * z

    def demo(self) -> None:
        for i in [0, 1, 2, 3]:
            for j in [0, 1, 2, 3]:
                self.mat[i][j] = float(i * 4 + j + 1)

    def copia(self) -> Matriz3D:
        return Matriz3D(self.mat)

    def __str__(self) -> str:
        res = ''
        for i in [0, 1, 2, 3]:
            res += '|'
            for j in [0, 1, 2, 3]:
                res += ' %6.2f' % self.mat[i][j]
            res = res + ' |\n'
        return res

    def __add__(self, otro: Matriz3D) -> Matriz3D:
        mat = Matriz3D()
        print(type(otro))
        for i in [0, 1, 2, 3]:
            for j in [0, 1, 2, 3]:
                mat.mat[i][j] = self.mat[i][j] + otro.mat[i][j]
        return mat

    @overload
    def __mul__(self, otro: Matriz3D) -> Matriz3D:
        ...

    @overload
    def __mul__(self, otro: Punto3D) -> Punto3D:
        ...

    def __mul__(self, otro: Matriz3D | Punto3D) -> Matriz3D | Punto3D:
        m0, m1, m2, m3 = self.mat
        if isinstance(otro, Matriz3D):
            o0, o1, o2, o3 = otro.mat
            res = Matriz3D()
            r0, r1, r2, r3 = res.mat

            r0[0] = m0[0] * o0[0] + m0[1] * o1[0] + m0[2] * o2[0] + m0[3] * o3[0]
            r0[1] = m0[0] * o0[1] + m0[1] * o1[1] + m0[2] * o2[1] + m0[3] * o3[1]
            r0[2] = m0[0] * o0[2] + m0[1] * o1[2] + m0[2] * o2[2] + m0[3] * o3[2]
            r0[3] = m0[0] * o0[3] + m0[1] * o1[3] + m0[2] * o2[3] + m0[3] * o3[3]

            r1[0] = m1[0] * o0[0] + m1[1] * o1[0] + m1[2] * o2[0] + m1[3] * o3[0]
            r1[1] = m1[0] * o0[1] + m1[1] * o1[1] + m1[2] * o2[1] + m1[3] * o3[1]
            r1[2] = m1[0] * o0[2] + m1[1] * o1[2] + m1[2] * o2[2] + m1[3] * o3[2]
            r1[3] = m1[0] * o0[3] + m1[1] * o1[3] + m1[2] * o2[3] + m1[3] * o3[3]

            r2[0] = m2[0] * o0[0] + m2[1] * o1[0] + m2[2] * o2[0] + m2[3] * o3[0]
            r2[1] = m2[0] * o0[1] + m2[1] * o1[1] + m2[2] * o2[1] + m2[3] * o3[1]
            r2[2] = m2[0] * o0[2] + m2[1] * o1[2] + m2[2] * o2[2] + m2[3] * o3[2]
            r2[3] = m2[0] * o0[3] + m2[1] * o1[3] + m2[2] * o2[3] + m2[3] * o3[3]

            r3[0] = m3[0] * o0[0] + m3[1] * o1[0] + m3[2] * o2[0] + m3[3] * o3[0]
            r3[1] = m3[0] * o0[1] + m3[1] * o1[1] + m3[2] * o2[1] + m3[3] * o3[1]
            r3[2] = m3[0] * o0[2] + m3[1] * o1[2] + m3[2] * o2[2] + m3[3] * o3[2]
            r3[3] = m3[0] * o0[3] + m3[1] * o1[3] + m3[2] * o2[3] + m3[3] * o3[3]
            return res

        punto = otro
        x = punto.x * m0[0] + punto.y * m1[0] + punto.z * m2[0] + m3[0]
        y = punto.x * m0[1] + punto.y * m1[1] + punto.z * m2[1] + m3[1]
        z = punto.x * m0[2] + punto.y * m1[2] + punto.z * m2[2] + m3[2]
        return Punto3D(x, y, z)


class Malla3D(Objeto3D):
    def __init__(self, mat: list[list[float]], color: str = 'black') -> None:
        fil = len(mat)
        col = len(mat[0])
        self.lp: list[Punto3D] = [Punto3D(f * 10, mat[f][c], c * 10) for f in range(fil) for c in range(col)]

        # m = Matriz3D()
        # m.escalado(1,1,1)
        # m.traslacion(0,0,0)
        # self.transforma3d(m)
        # self.setup()
        self.lc: list[list[int]] = []
        for f in range(fil - 1):
            for c in range(col - 1):
                # print(f,c)
                p = f * fil + c
                p2 = (f + 1) * fil + c
                self.lc.append([p2 + 1, p + 1, p])
                self.lc.append([p2, p2 + 1, p])

        Objeto3D.__init__(self, self.lp, caras=self.lc, color=color)
        m = Matriz3D()
        # m.escalado(1,1,1)
        # m.traslacion(0,0,0)
        self.transforma3d(m)
        self.setup()
        # list(map(self.nuevaCara,self.lc))


class Rectangulo3D(Objeto3D):
    lp: list[Punto3D] = [Punto3D(1, -1, -1), Punto3D(1, -1, 1),
                         Punto3D(1, 1, 1), Punto3D(1, 1, -1),
                         Punto3D(-1, -1, -1), Punto3D(-1, -1, 1),
                         Punto3D(-1, 1, 1), Punto3D(-1, 1, -1)]
    lc: list[list[int]] = [[0, 1, 2, 3], [7, 6, 5, 4], [3, 2, 6, 7],
                   [0, 4, 5, 1], [1, 5, 6, 2], [0, 3, 7, 4]]

    def __init__(self, pTam: Punto3D, pPos: Punto3D, color: str = 'black') -> None:
        Objeto3D.__init__(self, self.lp, color=color)
        m = Matriz3D()
        m.escalado(pTam.x / 2, pTam.y / 2, pTam.z / 2)
        m.traslacion(pPos.x, pPos.y, pPos.z)
        self.transforma3d(m)
        self.setup()
        list(map(self.nuevaCara, self.lc))


class Piramide3D(Objeto3D):
    lp: list[Punto3D] = [Punto3D(1, -1, 1), Punto3D(1, -1, -1),
                         Punto3D(-1, -1, -1), Punto3D(-1, -1, 1),
                         Punto3D(0, 1, 0)]
    lc: list[list[int]] = [[0, 1, 2, 3], [1, 0, 4], [2, 1, 4], [3, 2, 4], [0, 3, 4]]

    def __init__(self, pTam: Punto3D, pPos: Punto3D, color: str = 'black') -> None:
        Objeto3D.__init__(self, self.lp, color=color)
        m = Matriz3D()
        m.escalado(pTam.x / 2, pTam.y / 2, pTam.z / 2)
        m.traslacion(pPos.x, pPos.y, pPos.z)
        self.transforma3d(m)
        self.setup()
        list(map(self.nuevaCara, self.lc))


class Cubo3D(Rectangulo3D):
    def __init__(self, lado: float, p: Punto3D, color: str = 'black') -> None:
        Rectangulo3D.__init__(self, Punto3D(lado, lado, lado), p, color)


if __name__ == '__main__':
    m = Matriz3D()
    m.demo()
    m2 = m.copia()
    print(m)
    v = Punto3D(1, 2, 3)
    # c=m+m
    print(m)
    m.rotacionX(0.5)
    print(m)
