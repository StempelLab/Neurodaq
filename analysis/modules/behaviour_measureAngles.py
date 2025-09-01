from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import os
import numpy as np
import matplotlib.pylab as plt
import matplotlib.cm as colormap
import matplotlib.colors as colors
from analysis import auxfuncs as aux
from widgets import h5Item
from moviepy.editor import *

####################################

class AnalysisModule():

    def __init__(self, browser):

        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Measure angles'
        ############################################

        # Get main browser and widgets
        self.browser = browser
        self.plotWidget = browser.ui.dataPlotsWidget
        self.toolsWidget = browser.ui.oneDimToolStackedWidget
        self.videoWidget = browser.ui.dataVideoWidget
        self.plotWidget = browser.ui.dataPlotsWidget
        self.graphicsWidget = browser.ui.graphicsWidget
        self.canvas =  browser.ui.mplWidget.canvas
        self.ax = browser.ui.mplWidget.canvas.ax
        # Add entry to AnalysisSelectWidget
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.behaviourToolSelect
        selectWidget.model.appendRow(selectItem)
        # Add entry to tool selector
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()
        # Initialise main function variables
        self.refPoints = None


    def make_option_widgets(self):
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []

        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.drawLineButton = QtWidgets.QPushButton('Draw line')
        self.toolOptions.append([self.drawLineButton])
        self.setReferenceButton = QtWidgets.QPushButton('Set reference')
        self.toolOptions.append([self.setReferenceButton])

        # Connect buttons to functions
        self.drawLineButton.clicked.connect(self.draw_line)
        self.setReferenceButton.clicked.connect(self.set_ref)
        ############################################

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Take the current frame in the Video tab and show it in the GraphicsScene
        window to allow drawing of a reference and a measurement line,
        and output the angle between the two. Lines are drawn by selecting two
        end points. Pressing "Analyse" creates a new item in the data tree
        under "Angles". Item name is frame time.

        Buttons:
        1) Draw line
        2) Set reference line
        """


        ############################################
        # ANALYSIS FUNCTION

        # Plot current frame in new window
        currentTime = self.videoWidget.player.currentTime()/1000.
        currentFrame = self.videoWidget.clip.get_frame(currentTime)

        # Read angle between lines
        angle = self.graphicsWidget.line.angleTo(self.refLine)
        print(angle)

        # Store in data tree
        self.store_angle(angle, currentTime)

        # (re)Focus on video tab
        self.browser.ui.displayTabWidget.setCurrentIndex(2)
        ############################################

    def draw_line(self):
        # Draw current frame
        currentTime = self.videoWidget.player.currentTime()/1000.
        currentFrame = self.videoWidget.clip.get_frame(currentTime)
        self.graphicsWidget.display_image(currentFrame)

        # Draw reference line if it exists
        if self.refPoints is not None:
            self.refLine = QtCore.QLineF(self.refPoints[0], self.refPoints[1])
            lineItem = QtWidgets.QGraphicsLineItem(self.refLine)
            lineItem.setPen((QtGui.QPen(QtGui.QBrush(QtGui.QColor('#FA003A')), 1.5)))
            self.graphicsWidget.scene.addItem(lineItem)

        # Focus on graphics tab
        self.browser.ui.displayTabWidget.setCurrentIndex(3)

    def set_ref(self):
        # Read reference line points
        self.refPoints = [self.graphicsWidget.start, self.graphicsWidget.end]

    def store_angle(self, angle, currentTime):
        root = self.browser.ui.workingDataTree.invisibleRootItem()
        angleItem = aux.getItemFromPath(['Angle measurements'], root)
        if angleItem is None:
            angleItem = h5Item(['Angle measurements'])
            root.addChild(angleItem)
        frameItem = h5Item([str(currentTime)])
        frameItem.data = [angle]
        angleItem.addChild(frameItem)
