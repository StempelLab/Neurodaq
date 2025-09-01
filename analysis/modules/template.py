""" Template for adding new analysis modules.

To create a new module the user has to define the following:

1) The name to be listed in the tab [entryName]

2) The analysis options [make_option_widgets]. These are PyQt
widgets, such as a QCheckBox or a QLineEdit, to input parameters
to the analysis functions. 

3) The analysis function [func]

Currently the tab to which the modules are added is hard coded,
and it is the Custom Analysis tab.
 
To add the new module to NeuroDAQ rename the template.py file
and place it in the NeuroDAQ/analysis/modules folder.
"""

from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'myModule'  
        ############################################
        
        # Get main browser
        self.browser = browser          
        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.customToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()

    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.customToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.toolOptions.append(QtWidgets.QCheckBox('myOption 1', self.toolGroupBox))
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)


    def func(self, browser):
    
        ############################################
        # ANALYSIS FUNCTION
        print('My custom analysis function')
        for option in self.toolOptions:
            if option.isChecked():        
                print(option.text(), 'is checked')
        ############################################            
        
        
        
        
