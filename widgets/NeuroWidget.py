from PyQt5 import QtGui, QtCore, QtWidgets


class NeuroWidget(QtWidgets.QWidget):

    """ Reimplement QWidget Class to allow setting a size hint.    
        NeuroWidget(width, height)
    """

    def __init__(self, width, height, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self._width = width
        self._height = height
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)
