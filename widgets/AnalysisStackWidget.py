from PyQt5 import QtGui, QtCore, QtWidgets

class AnalysisStackWidget(QtWidgets.QStackedWidget):

    """ Stack widget for listing 1D Analysis tool options.
     
    Allows setting a size hint.    
        
    AnalysisSelectWidget(width, height)
    """

    def __init__(self, width, height):
        QtWidgets.QStackedWidget.__init__(self)
        self._width = width
        self._height = height
        self.widgetList = []   # List containing index in stack and matching name in Select Widget
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)
     
    def add_options(self, optionsList, groupBox, name):
        make_label_layout(optionsList, groupBox)
        index = self.addWidget(groupBox)
        self.widgetList.append([name, index])

def make_groupBox_layout(optionsList, groupBox):
    """ Layout widgets vertically:
    
          |Option 1|
          |Option 2|
          |Option 3|
    """
    vbox = QtWidgets.QVBoxLayout()
    for widget in optionsList:
        vbox.addWidget(widget)
    vbox.addStretch(1)
    groupBox.setLayout(vbox)

def make_label_layout(optionsList, groupBox):
    """ Layout labels and widgets side by side, vertically
    using a grid layout:
    
         |Label 1    Option 1|
         |Label 2    Option 2|
         |Label 3    Option 3|                  
    """
    gridbox = QtWidgets.QGridLayout()
    row = 0
    for item in optionsList:
        try: 
            len(item)
        except TypeError:
            item = [item]
        if len(item)==1:
            gridbox.addWidget(item[0], row, 0)
        elif len(item)==2: 
            gridbox.addWidget(item[0], row, 0)
            gridbox.addWidget(item[1], row, 1)  
        row+=1
    gridbox.setRowMinimumHeight(row,0)    
    gridbox.setRowStretch(row,1)        
    groupBox.setLayout(gridbox)

