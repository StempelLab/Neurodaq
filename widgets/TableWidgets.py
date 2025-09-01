from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal

class tableItem(QtWidgets.QTableWidgetItem):

    def __init__(self, parent=None):
        QtWidgets.QTableWidgetItem.__init__(self, parent)
        self.h5item = False
        self.h5link = ''

class TablePropsWidget(pg.TableWidget):

    """ Reimplement Pyqtgraph TableWidget Class to 
    catch some keyPresses
    """

    def __init__(self, *args, **kwargs):
        pg.TableWidget.__init__(self, *args, **kwargs)

    def keyPressEvent(self, event):
        """ Emit SIGNAL to update H5 attribute on keypress
        """
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.updateAttr.emit()
            # Currently only works for one property, dt            
            #attr = str(self.verticalHeaderItem(0).text())
            #attrValue = float(self.item(self.currentItem().row(), 0).text())
            #print(self.verticalHeaderItem(0).text(), self.item(0,0).text())
            
        
class SpreadSheet2(QtWidgets.QMainWindow):

    def __init__(self, rows, cols, parent = None):
        super(SpreadSheet, self).__init__(parent)

        self.toolBar = QtWidgets.QToolBar()
        self.addToolBar(self.toolBar)
        self.formulaInput = QtWidgets.QLineEdit()
        #self.cellLabel = QtWidgets.QLabel(self.toolBar)
        #self.cellLabel.setMinimumSize(80, 0)
        #self.toolBar.addWidget(self.cellLabel)
        self.toolBar.addWidget(self.formulaInput)
        self.table = QtWidgets.QTableWidget(rows, cols, self)
        self.table.setDragEnabled(True)
        self.table.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.table.setDefaultDropAction(QtCore.Qt.MoveAction)
        #for c in range(cols):
        #    character = chr(ord('A') + c)
        #    self.table.setHorizontalHeaderItem(c, QtWidgets.QTableWidgetItem(character))

        #self.table.setItemPrototype(self.table.item(rows - 1, cols - 1))
        self.setCentralWidget(self.table)


        
class SpreadSheet(QtWidgets.QTableWidget):
    # Define custom signals
    droppedInTable = pyqtSignal(object, object)
    tableTargetPosition = pyqtSignal(int, int)
    
    def __init__(self, rows, cols, parent = None):
        QtWidgets.QTableWidget.__init__(self, rows, cols, parent)  
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        for col in range(self.columnCount()):
            self.setColumnWidth(col,50)
            for row in range(self.rowCount()):            
                self.setRowHeight(row,20)
        

    def dropEvent(self, event):   
        super(SpreadSheet, self).dropEvent(event)
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        self.droppedInTable.emit(event.source(), modifiers)
        print('dropped', event.source())
            
    def dropMimeData(self, col, row, data, action):
        super(SpreadSheet, self).dropMimeData(row, col, data, action)
        self.tableTargetPosition.emit(col, row)
        print(row, col, action)
        if action == QtCore.Qt.MoveAction:
            return True
        return False