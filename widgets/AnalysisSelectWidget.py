from PyQt5 import QtGui, QtCore, QtWidgets

class AnalysisSelectWidget(QtWidgets.QListView):

    """ Reimplement QListView Class for displaying a list of tools
    
    Allows setting a size hint.    
    AnalysisSelectWidget(width, height)
    """

    def __init__(self, width, height):
        QtWidgets.QListView.__init__(self)
        self._width = width
        self._height = height
        self.internal_model()
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)
        
    def internal_model(self):
        self.model = QtGui.QStandardItemModel(self)
        self.setModel(self.model)
