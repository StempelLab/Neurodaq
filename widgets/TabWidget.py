from PyQt5 import QtGui, QtCore, QtWidgets


class TabWidget(QtWidgets.QTabWidget):

    """ Reimplement QTabWidget Class to allow setting a size hint.  
        TabWidget(width, height)
    """

    def __init__(self, width, height):
        QtWidgets.QTabWidget.__init__(self)
        self._width = width
        self._height = height
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)


