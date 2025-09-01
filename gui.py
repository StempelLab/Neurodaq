# -*- coding: utf-8 -*-

import os
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.qtconsoleapp import JupyterQtConsoleApp
# from IPython.qt.console.rich_ipython_widget import RichJupyterWidget
# from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

from PyQt5 import QtCore, QtGui, QtWidgets
from widgets import *
import pyqtgraph as pg
#import vlc


# try:
#     _fromUtf8 = QtCore.QString.fromUtf8
# except AttributeError:
_fromUtf8 = lambda s: s


class Ui_MainWindow(object):

    """ User interface main window for NeuroDAQ.
    Creates all the widgets and organizes geometry and layouts
    """

    def setupUi(self, MainWindow):

        """ Initialises the main window user interface
        """
        # Size policies
        preferredSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        expandingSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        # -----------------------------------------------------------------------------
        # Central Widget
        # -----------------------------------------------------------------------------

        # Geometry and Layout
        self.MainWindow = MainWindow
        #self.MainWindow.resize(1500, 780)
        self.MainWindow.setSizePolicy(preferredSizePolicy)
        self.MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)
        self.gridLayout_centralwidget = QtWidgets.QGridLayout(self.centralwidget)
        self.splitter_centralwidget = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_centralwidget.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_centralwidget.addWidget(self.splitter_centralwidget, 0, 0, 1, 1)
        self.MainWindow.setCentralWidget(self.centralwidget)
        self.MainWindow.setWindowTitle('NeuroDAQ Analysis')
        self.centralwidget.setMinimumHeight(50)

        # -----------------------------------------------------------------------------
        # Left pane -> SelectionTabs Widget and SinglePlot Widget
        # -----------------------------------------------------------------------------
        # Geometry and Layout
        self.splitter_leftPane = QtWidgets.QSplitter(self.splitter_centralwidget)
        self.splitter_leftPane.setOrientation(QtCore.Qt.Vertical)
        self.splitter_leftPane.setSizePolicy(preferredSizePolicy)
        #self.splitter_leftPane.setMinimumSize(10,10)  # to disable automatically set minimumSizeHints

        # SelectionTabs Widget
        # -----------------------------------------------------------------------------
        # Geometry and Layout
        self.selectionTabWidget = TabWidget(0,500)
        self.selectionTabWidget.setSizePolicy(preferredSizePolicy)
        self.selectionTabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.selectionTabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.selectionTabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.splitter_leftPane.addWidget(self.selectionTabWidget)

        # Minimum sizes for the leftPane
        # [Data, 1D, Behaviour, Image, Graph, Custom]
        self.leftPaneSizes = [100,400,500,500,500,500]

        # ------
        # TAB 1   (DataTab) -> dirTree and fileDataTree
        # ------
        # Geometry and Layout
        self.dataTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.dataTab, _fromUtf8("Data"))
        self.gridLayout_dataTab = QtWidgets.QGridLayout(self.dataTab)
        self.verticalsplitter_dataTab = QtWidgets.QSplitter(self.dataTab)
        self.verticalsplitter_dataTab.setSizePolicy(preferredSizePolicy)
        self.verticalsplitter_dataTab.setOrientation(QtCore.Qt.Vertical)
        self.verticalsplitter_dataTab_layout = QtWidgets.QGridLayout(self.verticalsplitter_dataTab)

        # TAB 1 content > Folder input
        self.dataFolderWidget = NeuroWidget(0,0, parent=self.verticalsplitter_dataTab)
        self.folderLayout = QtWidgets.QGridLayout(self.dataFolderWidget)
        self.loadFolderInput = QtWidgets.QLineEdit()
        #self.loadFolderLabel = QtWidgets.QLabel('Load Folder')
        self.loadFolderButton = QtWidgets.QPushButton('Load Folder')
        self.folderLayout.addWidget(self.loadFolderInput, 0, 0)
        self.folderLayout.addWidget(self.loadFolderButton, 0, 1)
        self.saveFolderInput = QtWidgets.QLineEdit()
        #self.saveFolderLabel = QtWidgets.QLabel('Save Folder')
        self.saveFolderButton = QtWidgets.QPushButton('Save Folder')
        self.folderLayout.addWidget(self.saveFolderInput, 1, 0)
        self.folderLayout.addWidget(self.saveFolderButton, 1, 1)


        # TAB 1 content > DirTree
        self.horizontalsplitter_dataTab = QtWidgets.QSplitter(self.verticalsplitter_dataTab)
        self.horizontalsplitter_dataTab.setSizePolicy(preferredSizePolicy)
        self.horizontalsplitter_dataTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_dataTab.addWidget(self.verticalsplitter_dataTab, 0, 0, 1, 1)
        self.dirTree = FileBrowserWidget(0,0) #, homeFolder = '/home/tiago/Code/py/NeuroDAQanalysis/testData/')
        self.horizontalsplitter_dataTab.addWidget(self.dirTree)
        self.dirTree.setSizePolicy(preferredSizePolicy)
        self.dirTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # TAB 1 content > FileDataTree
        self.fileDataTree = h5TreeWidget(0,0)
        self.horizontalsplitter_dataTab.addWidget(self.fileDataTree)
        self.fileDataTree.setSizePolicy(preferredSizePolicy)
        self.fileDataTree.setAcceptDrops(True)
        self.fileDataTree.setDragEnabled(True)
        self.fileDataTree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.fileDataTree.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.fileDataTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.fileDataTree.setSortingEnabled(True)
        self.fileDataTree.headerItem().setText(0, _fromUtf8("Data"))

        self.verticalsplitter_dataTab.setSizes([1,500])

        # -----
        # TAB 2   (oneDimAnalysisTab) -> toolSelect and toolStackedWidget
        # -----
        # Geometry and Layout
        self.oneDimAnalysisTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.oneDimAnalysisTab, _fromUtf8("1D Analysis"))
        self.gridLayout_oneDimAnalysisTab = QtWidgets.QGridLayout(self.oneDimAnalysisTab)
        self.splitter_oneDimAnalysisTab = QtWidgets.QSplitter(self.oneDimAnalysisTab)
        self.splitter_oneDimAnalysisTab.setSizePolicy(preferredSizePolicy)
        self.splitter_oneDimAnalysisTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_oneDimAnalysisTab.addWidget(self.splitter_oneDimAnalysisTab, 0, 0, 1, 1)

        # TAB 2 content > Tool Select
        self.oneDimToolSelect = AnalysisSelectWidget(0,0)
        self.splitter_oneDimAnalysisTab.addWidget(self.oneDimToolSelect)
        self.oneDimToolSelect.setMinimumWidth(150)
        self.oneDimToolSelect.setSizePolicy(preferredSizePolicy)


        # TAB 2 content > Tools Stacked Widget
        self.toolStackContainerWidget = NeuroWidget(0,0)
        self.toolStackGrid = QtWidgets.QGridLayout(self.toolStackContainerWidget)
        self.splitter_oneDimAnalysisTab.addWidget(self.toolStackContainerWidget)
        self.toolDataSourceBox = QtWidgets.QComboBox()
        self.toolDataSourceBox.addItem("Plot")
        self.toolDataSourceBox.addItem("Selection")
        self.toolStackGrid.addWidget(self.toolDataSourceBox)
        self.oneDimToolStackedWidget = AnalysisStackWidget(0,0)
        self.toolStackGrid.addWidget(self.oneDimToolStackedWidget)
        self.toolStackContainerWidget.setSizePolicy(preferredSizePolicy)
        #self.oneDimToolStackedWidget.setSizePolicy(preferredSizePolicy)


        # -----
        # TAB 3   (behaviourAnalysisTab) -> toolSelect and toolStackedWidget
        # -----
        # Geometry and Layout
        self.behaviourAnalysisTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.behaviourAnalysisTab, _fromUtf8("Behaviour Analysis"))
        self.gridLayout_behaviourAnalysisTab = QtWidgets.QGridLayout(self.behaviourAnalysisTab)
        self.splitter_behaviourAnalysisTab = QtWidgets.QSplitter(self.behaviourAnalysisTab)
        self.splitter_behaviourAnalysisTab.setSizePolicy(preferredSizePolicy)
        self.splitter_behaviourAnalysisTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_behaviourAnalysisTab.addWidget(self.splitter_behaviourAnalysisTab, 0, 0, 1, 1)

        # TAB 3 content > Tool Select
        self.behaviourToolSelect = AnalysisSelectWidget(0,0)
        self.splitter_behaviourAnalysisTab.addWidget(self.behaviourToolSelect)
        self.behaviourToolSelect.setMinimumWidth(200)
        self.behaviourToolSelect.setSizePolicy(preferredSizePolicy)

        # TAB 3 content > Tools Stacked Widget
        self.behaviourToolStackContainerWidget = NeuroWidget(0,0)
        self.behaviourToolStackGrid = QtWidgets.QGridLayout(self.behaviourToolStackContainerWidget)
        self.splitter_behaviourAnalysisTab.addWidget(self.behaviourToolStackContainerWidget)
        self.behaviourToolDataSourceBox = QtWidgets.QComboBox()
        self.behaviourToolDataSourceBox.addItem("Plot")
        self.behaviourToolDataSourceBox.addItem("Selection")
        self.behaviourToolStackGrid.addWidget(self.behaviourToolDataSourceBox)
        self.behaviourToolStackedWidget = AnalysisStackWidget(0,0)
        self.behaviourToolStackGrid.addWidget(self.behaviourToolStackedWidget)
        self.behaviourToolStackedWidget.setSizePolicy(preferredSizePolicy)

        # -----
        # TAB 4   (imageAnalysisTab) -> toolSelect and toolStackedWidget
        # -----
        # Geometry and Layout
        self.imageTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.imageTab, _fromUtf8("Image Anaysis"))
        self.gridLayout_imageTab = QtWidgets.QGridLayout(self.imageTab)
        self.splitter_imageTab = QtWidgets.QSplitter(self.imageTab)
        self.splitter_imageTab.setSizePolicy(preferredSizePolicy)
        self.splitter_imageTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_imageTab.addWidget(self.splitter_imageTab, 0, 0, 1, 1)

        # TAB 4 content > Tool Select
        self.imageToolSelect = AnalysisSelectWidget(0,0)
        self.splitter_imageTab.addWidget(self.imageToolSelect)
        self.imageToolSelect.setSizePolicy(preferredSizePolicy)

        # TAB 4 content > Tools Stacked Widget
        self.imageToolStackContainerWidget = NeuroWidget(0,0)
        self.imageToolStackGrid = QtWidgets.QGridLayout(self.imageToolStackContainerWidget)
        self.splitter_imageTab.addWidget(self.imageToolStackContainerWidget)
        self.imageToolStackedWidget = AnalysisStackWidget(0,0)
        self.imageToolStackGrid.addWidget(self.imageToolStackedWidget)
        self.imageToolStackedWidget.setSizePolicy(preferredSizePolicy)


        # -----
        # TAB 5   (graphTab) -> toolSelect and toolStackedWidget
        # -----
        # Geometry and Layout
        self.graphTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.graphTab, _fromUtf8("Graph"))
        self.gridLayout_graphTab = QtWidgets.QGridLayout(self.graphTab)
        self.splitter_graphTab = QtWidgets.QSplitter(self.graphTab)
        self.splitter_graphTab.setSizePolicy(preferredSizePolicy)
        self.splitter_graphTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_graphTab.addWidget(self.splitter_graphTab, 0, 0, 1, 1)

        # TAB 5 content > Tool Select
        self.graphToolSelect = AnalysisSelectWidget(0,0)
        self.splitter_graphTab.addWidget(self.graphToolSelect)
        self.graphToolSelect.setSizePolicy(preferredSizePolicy)

        # TAB 5 content > Tools Stacked Widget
        self.graphToolStackContainerWidget = NeuroWidget(0,0)
        self.graphToolStackGrid = QtWidgets.QGridLayout(self.graphToolStackContainerWidget)
        self.splitter_graphTab.addWidget(self.graphToolStackContainerWidget)
        self.graphToolStackedWidget = AnalysisStackWidget(0,0)
        self.graphToolStackGrid.addWidget(self.graphToolStackedWidget)
        self.graphToolStackedWidget.setSizePolicy(preferredSizePolicy)


        # -----
        # TAB 6   (customAnalysisTab) -> toolSelect and toolStackedWidget
        # -----
        # Geometry and Layout
        self.customAnalysisTab = NeuroWidget(0,0)
        self.selectionTabWidget.addTab(self.customAnalysisTab, _fromUtf8("Custom Analysis"))
        self.gridLayout_customAnalysisTab = QtWidgets.QGridLayout(self.customAnalysisTab)
        self.splitter_customAnalysisTab = QtWidgets.QSplitter(self.customAnalysisTab)
        self.splitter_customAnalysisTab.setSizePolicy(preferredSizePolicy)
        self.splitter_customAnalysisTab.setOrientation(QtCore.Qt.Horizontal)
        self.gridLayout_customAnalysisTab.addWidget(self.splitter_customAnalysisTab, 0, 0, 1, 1)

        # TAB 6 content > Tool Select
        self.customToolSelect = AnalysisSelectWidget(0,0)
        self.splitter_customAnalysisTab.addWidget(self.customToolSelect)
        self.customToolSelect.setSizePolicy(preferredSizePolicy)


        # TAB 6 content > Tools Stacked Widget
        self.customToolStackContainerWidget = NeuroWidget(0,0)
        self.customToolStackGrid = QtWidgets.QGridLayout(self.customToolStackContainerWidget)
        self.splitter_customAnalysisTab.addWidget(self.customToolStackContainerWidget)
        self.customToolDataSourceBox = QtWidgets.QComboBox()
        self.customToolDataSourceBox.addItem("Plot")
        self.customToolDataSourceBox.addItem("Selection")
        self.customToolStackGrid.addWidget(self.customToolDataSourceBox)
        self.customToolStackedWidget = AnalysisStackWidget(0,0)
        self.customToolStackGrid.addWidget(self.customToolStackedWidget)
        self.customToolStackedWidget.setSizePolicy(preferredSizePolicy)


        # SinglePlots Widget
        # -----------------------------------------------------------------------------
        # Geometry and Layout
        #self.singlePlotWidget = matplotlibWidget(0,200)
        self.singlePlotWidget = pg.PlotWidget(background='#ECEDEB')
        self.singlePlotWidget.getAxis('bottom').setPen('k')
        self.singlePlotWidget.getAxis('left').setPen('k')
        self.splitter_leftPane.addWidget(self.singlePlotWidget)
        self.singlePlotWidget.setSizePolicy(preferredSizePolicy)

        # -----------------------------------------------------------------------------
        # Middle pane -> DisplayTabs Widget
        # -----------------------------------------------------------------------------

        # DisplayTabs Widget
        # -----------------------------------------------------------------------------
        # Geometry and Layout
        self.displayTabWidget = TabWidget(0,0)
        self.displayTabWidget.setSizePolicy(preferredSizePolicy)
        self.splitter_centralwidget.addWidget(self.displayTabWidget)


        # ------
        # TAB 1   (PlotTab)
        # ------
        # Geometry and Layout
        self.dataPlotsTab = NeuroWidget(0,0)
        self.displayTabWidget.addTab(self.dataPlotsTab, 'Plot')
        self.gridLayout_plots = QtWidgets.QGridLayout(self.dataPlotsTab)

        # TAB 1 content > dataPlotsWidget
        #self.dataPlotsWidget = matplotlibWidget(0,0)
        #self.dataPlotsWidget = pg.PlotWidget(background='#ECEDEB')
        self.dataPlotsWidget = plotWidget(background='#ECEDEB')
        self.dataPlotsWidget.getAxis('bottom').setPen('k')
        self.dataPlotsWidget.getAxis('left').setPen('k')
        self.dataPlotsWidget.showGrid(x=True, y=True, alpha=0.3)
        self.dataPlotsWidget.setSizePolicy(preferredSizePolicy)
        self.gridLayout_plots.addWidget(self.dataPlotsWidget)
        # Cursors
        self.dataPlotsWidget.cursor1 = pg.InfiniteLine(angle=90, movable=True,
                                      pen=pg.mkPen('#2AB825', width=2, style=QtCore.Qt.DotLine))
        self.dataPlotsWidget.cursor2 = pg.InfiniteLine(angle=90, movable=True,
                                      pen=pg.mkPen('#2AB825', width=2, style=QtCore.Qt.DotLine))
        self.dataPlotsWidget.cursor = False
        # Toolbar
        self.plotToolBar = QtWidgets.QToolBar()
        self.plotToolBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.gridLayout_plots.addWidget(self.plotToolBar)

        # ------
        # TAB 2   (ImageTab)
        # ------
        # Geometry and Layout
        self.dataImageTab = NeuroWidget(0,0)
        self.displayTabWidget.addTab(self.dataImageTab, 'Image')
        self.gridLayout_images = QtWidgets.QGridLayout(self.dataImageTab)

        # TAB 2 content > dataPlotsWidget
        #self.dataPlotsWidget = matplotlibWidget(0,0)
        self.dataImageWidget = pg.ImageView()
        self.dataImageWidget.setSizePolicy(preferredSizePolicy)
        self.gridLayout_images.addWidget(self.dataImageWidget)
        # Toolbar
        #self.plotToolBar = QtWidgets.QToolBar()
        #self.plotToolBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        #self.gridLayout_images.addWidget(self.plotToolBar)

        # ------
        # TAB X   (videoTab)
        # ------
        # Geometry and Layout
        self.dataVideoTab = NeuroWidget(0,0)
        self.displayTabWidget.addTab(self.dataVideoTab, 'Video')
        self.gridLayout_video = QtWidgets.QGridLayout(self.dataVideoTab)

        # content
        self.dataVideoWidget = videoPlayerWidget()
        self.dataVideoWidget.setSizePolicy(preferredSizePolicy)
        self.gridLayout_video.addWidget(self.dataVideoWidget, 0, 0, 1, 1)

        # toolbar
        self.videoPlotToolBar = QtWidgets.QToolBar()
        self.videoPlotToolBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.gridLayout_video.addWidget(self.videoPlotToolBar)

        # ------
        # TAB X   (graphicsTab)
        # ------
        # Geometry and Layout
        self.graphicsTab = NeuroWidget(0,0)
        self.displayTabWidget.addTab(self.graphicsTab, 'Graphics')
        self.gridLayout_graphics = QtWidgets.QGridLayout(self.graphicsTab)

        # content
        self.graphicsWidget = GraphicsWidget()
        self.graphicsWidget.setSizePolicy(preferredSizePolicy)
        self.gridLayout_graphics.addWidget(self.graphicsWidget, 0, 0, 1, 1)

        # toolbar
        self.graphicsToolBar = QtWidgets.QToolBar()
        self.graphicsToolBar.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.gridLayout_graphics.addWidget(self.graphicsToolBar)

        # ------
        # TAB 3   (TableTab)
        # ------
        # Geometry and Layout
        # TAB 3 content > tableWidget
        #self.dataTableWidget = QtWidgets.QTableWidget()
        #self.dataTableWidget = pg.TableWidget(editable=False)
        self.dataTableWidget = SpreadSheet(100,100)
        #self.dataTableWidget.setDragEnabled(True)
        #self.dataTableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        #self.dataTableWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.dataTableWidget.setAlternatingRowColors(True)
        self.dataTableWidget.setColumnCount(100)
        self.dataTableWidget.setRowCount(100)
        self.displayTabWidget.addTab(self.dataTableWidget, _fromUtf8("Table"))


        # ------
        # TAB 4   (IPythonTab)
        # ------
        # Geometry and Layout
        # TAB 4 content > IPython console
        self.IPythonWidget = QIPythonWidget()
        self.displayTabWidget.addTab(self.IPythonWidget, _fromUtf8("IPython"))

        # ------
        # TAB 5   (Matplotlib Tab)
        # ------
        # Geometry and Layout
        # TAB 5 content > Matplotlib axes
        self.mplWidget = matplotlibWidget()
        self.displayTabWidget.addTab(self.mplWidget, _fromUtf8("MatplotLib"))


        # ------
        # TAB 6   (Notes Tab)
        # ------
        # Geometry and Layout
        # TAB 6 content > Notes text edit
        self.notesWidget = QtWidgets.QTextEdit()
        self.displayTabWidget.addTab(self.notesWidget, _fromUtf8("Notes"))


        # -----------------------------------------------------------------------------
        # Right pane -> Working Data Tree and Properties Table
        # -----------------------------------------------------------------------------
        # Geometry and Layout
        self.splitter_rightPane = QtWidgets.QSplitter(self.splitter_centralwidget)
        self.splitter_rightPane.setSizePolicy(preferredSizePolicy)
        self.splitter_rightPane.setOrientation(QtCore.Qt.Vertical)

        # WorkingDataTree Widget
        # -----------------------------------------------------------------------------
        self.workingDataTree = h5TreeWidget(0,0)
        self.splitter_rightPane.addWidget(self.workingDataTree)
        self.workingDataTree.setSizePolicy(preferredSizePolicy)
        self.workingDataTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.workingDataTree.setAcceptDrops(True)
        self.workingDataTree.setDragEnabled(True)
        self.workingDataTree.setDropIndicatorShown(True)
        #self.workingDataTree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        #self.workingDataTree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.workingDataTree.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.workingDataTree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.workingDataTree.headerItem().setText(0, _fromUtf8("Working Data"))

        # Properties Table Widget
        # -----------------------------------------------------------------------------
        #self.propsTableWidget = pg.TableWidget(self.splitter_rightPane, editable=True)
        self.propsTableWidget = TablePropsWidget(self.splitter_rightPane, editable=True)
        #self.propsTableWidget = QtWidgets.QTableWidget(self.splitter_rightPane)
        self.propsTableWidget.setSizePolicy(preferredSizePolicy)
        self.propsTableWidget.setRowCount(0)
        self.propsTableWidget.setColumnCount(0)
        self.propsTableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.propsTableWidget.horizontalHeader().setStretchLastSection(True)

        self.splitter_leftPane.setSizes([300,1])
        self.splitter_centralwidget.setSizes([400,800,200])
        self.splitter_rightPane.setSizes([500,1])

        # -----------------------------------------------------------------------------
        # Status Bar
        # -----------------------------------------------------------------------------
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.setLayoutDirection(QtCore.Qt.RightToLeft)
        #self.statusbar.showMessage('Ready')

        # -----------------------------------------------------------------------------
        # ToolBars
        # -----------------------------------------------------------------------------
        # Top toolbar
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)


        # -----------------------------------------------------------------------------
        # Actions
        # -----------------------------------------------------------------------------
        # Top Toolbar
        self.actionLoadData = QtWidgets.QAction('Load', MainWindow)
        self.actionNewFile = QtWidgets.QAction('New', MainWindow)
        self.actionSaveFile = QtWidgets.QAction('Save', MainWindow)
        self.actionSaveFileAs = QtWidgets.QAction('Save As', MainWindow)
        self.toolBar.addAction(self.actionNewFile)
        self.toolBar.addAction(self.actionLoadData)
        self.toolBar.addAction(self.actionSaveFile)
        self.toolBar.addAction(self.actionSaveFileAs)

        # Plot Toolbar
        self.actionPlotData = QtWidgets.QAction('Plot', MainWindow)
        self.actionBrowseData = QtWidgets.QAction('Browse', MainWindow)
        self.actionBrowseData.setCheckable(True)
        self.actionShowCursors = QtWidgets.QAction('Cursors', MainWindow)
        self.actionShowCursors.setCheckable(True)
        self.actionAnalyseData = QtWidgets.QAction('Analyse', MainWindow)
        self.plotToolBar.addAction(self.actionBrowseData)
        self.plotToolBar.addAction(self.actionPlotData)
        self.plotToolBar.addAction(self.actionShowCursors)
        self.plotToolBar.addAction(self.actionAnalyseData)

        # Graphics Toolbar
        self.graphicsToolBar.addAction(self.actionAnalyseData)

        # Video Plot Toolbar
        self.videoPlotToolBar.addAction(self.actionAnalyseData)
        self.actionVideoPlotData = QtWidgets.QAction('Plot', MainWindow)
        self.videoPlotToolBar.addAction(self.actionVideoPlotData)
        self.actionClearAllTags = QtWidgets.QAction('Clear all', MainWindow)
        self.videoPlotToolBar.addAction(self.actionClearAllTags)
        self.actionClearTag = QtWidgets.QAction('Clear tag', MainWindow)
        self.videoPlotToolBar.addAction(self.actionClearTag)
        self.actionShowVideoTags = QtWidgets.QAction('Show tag', MainWindow)
        self.actionShowVideoTags.setCheckable(True)
        self.videoPlotToolBar.addAction(self.actionShowVideoTags)
        self.actionTagVideoData = QtWidgets.QAction('Tag', MainWindow)
        self.videoPlotToolBar.addAction(self.actionTagVideoData)
        self.videoTagSelection = QtWidgets.QComboBox()
        self.videoTagSelection.addItem('A')
        self.videoTagSelection.addItem('B')
        self.videoTagSelection.addItem('C')
        self.videoTagSelection.addItem('D')
        self.videoTagSelection.addItem('E')
        self.videoTagSelection.addItem('F')
        self.videoTagSelection.addItem('G')
        self.videoTagSelection.addItem('H')
        self.videoTagSelection.addItem('I')
        self.videoTagSelection.addItem('J')
        self.videoTagSelection.addItem('K')
        self.videoTagSelection.addItem('L')
        self.videoTagSelection.addItem('M')
        self.videoTagSelection.addItem('N')
        self.videoTagSelection.addItem('O')
        self.videoTagSelection.addItem('P')
        self.videoTagSelection.addItem('Q')
        self.videoTagSelection.addItem('R')
        self.videoTagSelection.addItem('S')
        self.videoTagSelection.addItem('T')
        self.videoPlotToolBar.addWidget(self.videoTagSelection)

        # File data tree context menu
        self.actionAddRootGroup = QtWidgets.QAction('Add Root Group', MainWindow)
        self.actionAddChildGroup = QtWidgets.QAction('Add Child Group', MainWindow)
        self.actionAddDataset = QtWidgets.QAction('Add Dataset', MainWindow)
        self.actionRenameTreeItem = QtWidgets.QAction('Rename', MainWindow)
        self.actionShowInTable = QtWidgets.QAction('Show in Table', MainWindow)
        self.actionRemoveTreeItem = QtWidgets.QAction('Remove', MainWindow)

        # -----------------------------------------------------------------------------
        # House keeping jobs
        # -----------------------------------------------------------------------------
        # Group data source boxes [selectionTabWidget index, dataSource combo box]
        self.dataSource = []
        self.dataSource.append([1, self.toolDataSourceBox])
        self.dataSource.append([2, self.behaviourToolDataSourceBox])


    def setSize(self, fraction):
        """ Resize MainWindow to a fraction of the total screen size
        """
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        height = int(screen.height() * fraction)
        width = int(screen.width() * fraction)
        self.MainWindow.resize(width, height)
