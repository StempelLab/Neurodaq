import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PIL import Image
from PIL.ImageQt import ImageQt


class GraphicsWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent = None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setSceneRect(QtCore.QRectF(self.viewport().rect()))
        self.scene = self.scene()
        self.lineItem = None
        #self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 0,0,90)))
        #self.add_widget()
        #self.display_image()

    def mousePressEvent(self, event):
        self.start = QtCore.QPointF(self.mapToScene(event.pos()))
        self.end = QtCore.QPointF(self.mapToScene(event.pos()))
        self.line = QtCore.QLineF(self.start, self.end)
        if not self.lineItem:
            self.lineItem = QtWidgets.QGraphicsLineItem(self.line)
            self.lineItem.setPen((QtGui.QPen(QtGui.QBrush(QtGui.QColor('#FAFA00')), 1.5)))
            self.scene.addItem(self.lineItem)
        else:
            self.line.setPoints(self.start, self.end)
            self.lineItem.setLine(self.line)

    def mouseReleaseEvent(self, event):
        self.end = QtCore.QPointF(self.mapToScene(event.pos()))

    def mouseMoveEvent(self, event):
        curPos = QtCore.QPointF(self.mapToScene(event.pos()))
        self.line.setPoints(self.start, curPos)
        self.lineItem.setLine(self.line)

    def display_image(self, array):
        #array = np.load('/Users/tiago/test.npy')
        img = Image.fromarray(array)
        self.scene.clear()
        self.lineItem = None
        w, h = img.size
        w=w*1.2
        h=h*1.2
        self.imgQ = ImageQt(img)  # we need to hold reference to imgQ, or it will crash
        pixMap = QPixmap.fromImage(self.imgQ)
        pixItem = QtWidgets.QGraphicsPixmapItem(pixMap)
        self.scene.addItem(pixItem)
        #self.scene.addPixmap(pixMap)
        self.fitInView(0.,0.,w,h,QtCore.Qt.KeepAspectRatio)
        #self.fitInView(QtCore.QRectF(0, 0, w, h), QtCore.Qt.KeepAspectRatio)
        self.scene.update()


    def add_widget(self):
        w = QtWidgets.QWidget()
        self.scene.addWidget(w)
        self.fitInView(QtCore.QRectF(self.viewport().rect()), QtCore.Qt.KeepAspectRatio)
        self.scene.update()
