import ast
import math

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from scipy.optimize import fsolve
import numpy as np

LINE_CP_ROUNDNESS = 100

#### THIS IS WHERE ALL THE PAINTING IS DONE

class QGraphicsLine(QGraphicsPathItem):
    def __init__(self, line, color="#000000", parent=None):
        super().__init__(parent)

        self.line = line

        self._color = color
        self._color = QColor(self._color)
        self._pen = QPen(self._color)
        self._pen_dragging = QPen(self._color)
        self._pen.setWidthF(15)
        self.pen.setColor(self._color)

        self.posSource = [0, 0]
        self.posDestination = [200, 200]

        self.initUI()

    def initUI(self):
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(15)
        # shadow.setColor(QColor("#000000"))
        # self.setGraphicsEffect(shadow)
        pass

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    @property
    def pen(self):
        return self._pen

    @pen.setter
    def pen(self, value):
        self._color = value
        self.pen.setColor(QColor(self._color))

    # this caused an error
    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        path = self.calcPath()
        return path

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())

        # CHANGE LATER FOR MORE INTERACTIVE DRAWING
        # if self.line.end_socket is None:
        #     painter.setPen(self._pen_dragging)
        # else:
        #     painter.setPen(self._pen if not self.isSelected() else self._pen_selected)

        painter.setPen(self._pen)
        # painter.setBrush(QColor(169, 232, 205, 255))
        # painter.setBrush(self._color)
        painter.drawPath(self.path())

    def calcPath(self):
        """Will handle drawing QPainterPath from point A to B"""
        raise NotImplemented("This method had to overriden in a child class")


class QGraphicsLineDirect(QGraphicsLine):
    def __init__(self, line, color, section="top", IC=None, OC=None, BP=None):
        super().__init__(line, color)

        self.IC, self.OC, self.BP = IC, OC, BP

        self.main_win = line.main_win
        self.ui = self.main_win.ui

        self.color = color
        self.section = section

    def calcPath(self):

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))

        if self.IC == None or self.OC ==None or self.BP == None:
            #### DEFINE VARIABLES
            A_m = self.text_to_list(self.ui.le_A_i.text())[0]
            B_m = self.text_to_list(self.ui.le_B_i.text())[0]
            a_m = self.text_to_list(self.ui.le_a_i.text())[0]
            b_m = self.text_to_list(self.ui.le_b_i.text())[0]
            Ri_m = self.text_to_list(self.ui.le_Ri_i.text())[0]
            L_m = self.text_to_list(self.ui.le_L_i.text())[0]
            Req_m = self.text_to_list(self.ui.le_Req_i.text())[0]

            ### left end cell
            A_el = self.text_to_list(self.ui.le_A_ol.text())[0]
            B_el = self.text_to_list(self.ui.le_B_ol.text())[0]
            a_el = self.text_to_list(self.ui.le_a_ol.text())[0]
            b_el = self.text_to_list(self.ui.le_b_ol.text())[0]
            Ri_el = self.text_to_list(self.ui.le_Ri_ol.text())[0]
            L_el= self.text_to_list(self.ui.le_L_ol.text())[0]
            Req_el = self.text_to_list(self.ui.le_Req_ol.text())[0]

            ### right end cell
            A_er = self.text_to_list(self.ui.le_A_or.text())[0]
            B_er = self.text_to_list(self.ui.le_B_or.text())[0]
            a_er = self.text_to_list(self.ui.le_a_or.text())[0]
            b_er = self.text_to_list(self.ui.le_b_or.text())[0]
            Ri_er = self.text_to_list(self.ui.le_Ri_or.text())[0]
            L_er= self.text_to_list(self.ui.le_L_or.text())[0]
            Req_er = self.text_to_list(self.ui.le_Req_or.text())[0]

            if self.ui.cb_Outer_Cell_L.checkState() == 0:
                if self.ui.cb_Outer_Cell_R.checkState() == 2:
                    A_el, B_el, a_el, b_el, Ri_el, L_el, Req_el = A_er, B_er, a_er, b_er, Ri_er, L_er, Req_er
                else:
                    A_el, B_el, a_el, b_el, Ri_el, L_el, Req_el = A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m

            if self.ui.cb_Outer_Cell_R.checkState() == 0:
                if self.ui.cb_Outer_Cell_L.checkState() == 2:
                    A_er, B_er, a_er, b_er, Ri_er, L_er, Req_er = A_el, B_el, a_el, b_el, Ri_el, L_el, Req_el
                else:
                    A_er, B_er, a_er, b_er, Ri_er, L_er, Req_er = A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m

            #### ADD BEAM PIPES IF ONLY MID CELLS IS CHECKED AND ABCI CODE SELECTED
            if self.ui.cb_Inner_Cell.checkState() == 2 and self.ui.cb_LBP.checkState() == 0 and self.ui.cb_RBP.checkState() == 0:
                L_bp_l, L_bp_r = 0, 0
            else:
                if self.ui.cb_LBP.checkState() == 2:
                    L_bp_l = 4*L_m
                else:
                    L_bp_l = 0

                if self.ui.cb_RBP.checkState() == 2:
                    L_bp_r = 4*L_m
                else:
                    L_bp_r = 0

        else:
            A_m, B_m, a_m, b_m, Ri_m, L_m, Req_m, _ = self.IC
            A_el, B_el, a_el, b_el, Ri_el, L_el, Req_el, _ = self.OC
            A_er, B_er, a_er, b_er, Ri_er, L_er, Req_er, _ = self.OC

            if self.BP.lower() == "none":
                L_bp_l, L_bp_r = 0, 0
            elif self.BP.lower() == "left":
                L_bp_l, L_bp_r = 4*L_m, 0
            elif self.BP.lower() == "right":
                L_bp_l, L_bp_r = 0, 4*L_m
            else:
                L_bp_l, L_bp_r = 4*L_m, 4*L_m

        n_cell = self.ui.sb_N_Cells.value()

        # calculate shift
        shift = (L_bp_r+L_bp_l + (n_cell-1)*2*L_m + L_el + L_er)/2

        #### SHIFT POINT TO START POINT
        path.moveTo(-shift, 0)

        #### START PATH
        path.lineTo(-shift, Ri_el)

        #### ADD BEAM PIPE LENGTH
        path.lineTo(L_bp_l-shift, Ri_el)

        # calculate angles outside loop
        ### CALCULATE x1_el, y1_el, x2_el, y2_el
        data = ([0+L_bp_l, Ri_el+b_el, L_el+L_bp_l, Req_el-B_el], [a_el, b_el, A_el, B_el]) # data = ([h, k, p, q], [a_m, b_m, A_m, B_m])
        x1el, y1el, x2el, y2el = fsolve(self.f, np.array([a_el+L_bp_l, Ri_el+0.85*b_el, L_el-A_el + L_bp_l, Req_el-0.85*B_el]), args=data) # [a_m, b_m-0.3*b_m, L_m-A_m, Req_m-0.7*B_m] initial guess
        # calculate iris angle
        alpha1_el = np.arctan((Ri_el+b_el-y1el)/(x1el-L_bp_l))
        alpha1_el = np.rad2deg(alpha1_el)
        # calculate equator angle
        alpha2_el = np.arctan((B_el - (Req_el-y2el))/(L_el + L_bp_l - x2el))
        alpha2_el = np.rad2deg(alpha2_el)

        ### CALCULATE x1, y1, x2, y2
        data = ([0+L_bp_l, Ri_m+b_m, L_m+L_bp_l, Req_m-B_m], [a_m, b_m, A_m, B_m]) # data = ([h, k, p, q], [a_m, b_m, A_m, B_m])
        x1, y1, x2, y2 = fsolve(self.f, np.array([a_m+L_bp_l, Ri_m+0.85*b_m, L_m-A_m + L_bp_l, Req_m-0.85*B_m]), args=data) # [a_m, b_m-0.3*b_m, L_m-A_m, Req_m-0.7*B_m] initial guess
        # calculate angle
        alpha1 = np.arctan((Ri_m+b_m-y1)/(x1-L_bp_l))
        alpha1 = np.rad2deg(alpha1)
        # calculate angle
        alpha2 = np.arctan((B_m - (Req_m-y2))/(L_m + L_bp_l - x2))
        alpha2 = np.rad2deg(alpha2)

        ### CALCULATE x1_er, y1_er, x2_er, y2_er
        data = ([0+L_bp_l, Ri_er+b_er, L_er+L_bp_l, Req_er-B_er], [a_er, b_er, A_er, B_er]) # data = ([h, k, p, q], [a_m, b_m, A_m, B_m])
        x1er, y1er, x2er, y2er = fsolve(self.f, np.array([a_er+L_bp_l, Ri_er+0.85*b_er, L_er-A_er + L_bp_l, Req_er-0.85*B_er]), args=data) # [a_m, b_m-0.3*b_m, L_m-A_m, Req_m-0.7*B_m] initial guess
        # calculate angle
        alpha1_er = np.arctan((Ri_er+b_er-y1er)/(x1er-L_bp_l))
        alpha1_er = np.rad2deg(alpha1_er)
        # calculate equator angle
        alpha2_er = np.arctan((B_er - (Req_er-y2er))/(L_er + L_bp_l - x2er))
        alpha2_er = np.rad2deg(alpha2_er)

        for i in range(n_cell):
            if i == 0:
                # print(1)
                # DRAW ARC:
                path.arcTo(QRectF(-a_el + L_bp_l-shift, Ri_el, 2*a_el, 2*b_el), 90, -90+alpha1_el)

                #### DRAW LINE CONNECTING ARCS
                path.lineTo(-shift + x2el, y2el)

                #### DRAW ARC, FIRST EQUATOR ARC TO NEXT POINT
                path.arcTo(QRectF(L_el-A_el + L_bp_l-shift, Req_el-2*B_el, 2*A_el, 2*B_el), 180+alpha2_el, 90-alpha2_el) #180-2*alpha2_el

            else:
                # print(2)
                #### DRAW ARC: CALCULATE x1, y1, x2, y2
                path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el - a_m + L_bp_l-shift, Ri_m, 2*a_m, 2*b_m), 90, -90+alpha1)

                #### DRAW LINE CONNECTING ARCS
                path.lineTo(2*(i-1)*L_m + L_m + L_el-shift + x2, y2)

                #### DRAW ARC, FIRST EQUATOR ARC TO NEXT POINT
                path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el + L_m-A_m + L_bp_l-shift, Req_m-2*B_m, 2*A_m, 2*B_m), 180+alpha2, 90-alpha2)

            if i == (n_cell-1) and A_er:
                # print(3)
                if i == 0:
                    # EQUATOR ARC TO NEXT POINT
                    path.arcTo(QRectF(+ L_m-A_er + L_bp_l-shift, Req_er-2*B_er, 2*A_er, 2*B_er), 270, 90-alpha2_er)

                    #### STRAIGHT LINE TO NEXT POINT
                    path.lineTo(+ 2*L_er - x1er + 2*L_bp_l-shift, y1er)

                    #### ARC
                    path.arcTo(QRectF(+ 2*L_er-a_er + L_bp_l-shift, Ri_er, 2*a_er, 2*b_er), 180-alpha1_er, -90+alpha1_er)
                else:
                    # EQUATOR ARC TO NEXT POINT
                    path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el + L_m-A_er + L_bp_l-shift, Req_er-2*B_er, 2*A_er, 2*B_er), 270, 90-alpha2_er)

                    #### STRAIGHT LINE TO NEXT POINT
                    path.lineTo(2*(i-1)*L_m + L_m + L_el + 2*L_er - x1er + 2*L_bp_l-shift, y1er)

                    #### ARC
                    path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el + 2*L_er-a_er + L_bp_l-shift, Ri_er, 2*a_er, 2*b_er), 180-alpha1_er, -90+alpha1_er)
            else:
                # print(4)
                # SECOND EQUATOR ARC TO NEXT POINT
                if i == 0:
                    path.arcTo(QRectF(+ L_m-A_m + L_bp_l-shift, Req_m-2*B_m, 2*A_m, 2*B_m), 270, 90-alpha2)

                    #### STRAIGHT LINE TO NEXT POINT
                    path.lineTo( + 2*L_m - x1 + 2*L_bp_l-shift, y1)

                    #### ARC
                    path.arcTo(QRectF(+ 2*L_m-a_m + L_bp_l-shift, Ri_m, 2*a_m, 2*b_m), 180-alpha1, -90+alpha1)
                else:
                    path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el + L_m-A_m + L_bp_l-shift, Req_m-2*B_m, 2*A_m, 2*B_m), 270, 90-alpha2)

                    #### STRAIGHT LINE TO NEXT POINT
                    path.lineTo(2*(i-1)*L_m + L_m + L_el + 2*L_m - x1 + 2*L_bp_l-shift, y1)

                    #### ARC
                    path.arcTo(QRectF(2*(i-1)*L_m + L_m + L_el + 2*L_m-a_m + L_bp_l-shift, Ri_m, 2*a_m, 2*b_m), 180-alpha1, -90+alpha1)


        #### BEAM PIPE
        path.lineTo(2*n_cell*L_er + L_bp_l+L_bp_r-shift, Ri_er)

        #### END PATH
        path.lineTo(2*n_cell*L_er + L_bp_l+L_bp_r-shift, 0)

        if self.section == "top":
            self.setTransform(QTransform.fromScale(1, -1))
        elif type == "bottom":
            pass

        # path.closeSubpath()
        self.setPath(path)

        return path

    def f(self, z, *data):
        coord, dim = data
        h, k, p, q = coord
        a, b, A, B = dim
        x1, y1, x2, y2 = z

        f1 = A**2*b**2*(x1-h)*(y2-q)/(a**2*B**2*(x2-p)*(y1-k)) - 1
        f2 = (x1-h)**2/a**2 + (y1-k)**2/b**2 - 1
        f3 = (x2-p)**2/A**2 + (y2-q)**2/B**2 - 1
        f4 = -b**2*(x1-x2)*(x1-h)/(a**2*(y1-y2)*(y1-k)) - 1

        return f1, f2, f3, f4

    def text_to_list(self, txt):
        if "range" in txt:
            txt = txt.replace('range', '')
            l = ast.literal_eval(txt)
            return range(l[0], l[1], l[2])
        elif 'linspace' in txt:
            l = eval(f'np.{txt}')
            return l
        else:
            l = ast.literal_eval(txt)
            if isinstance(l, int) or isinstance(l, float):
                return [l]
            else:
                return list(l)
