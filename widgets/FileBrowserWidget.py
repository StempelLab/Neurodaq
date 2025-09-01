import platform, os
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal


class FileBrowserWidget(QtWidgets.QTreeView):

    """ Reimplement QTreeWidget Class 
    
    Set Model to QFileSystemModel.
    Allows setting size hint and Home Folder
           
    TabWidget(width, height, [homeFolder=None])
    """
    fileDeletePressed = pyqtSignal()
    def __init__(self, width, height, homeFolder=None):
        QtWidgets.QTreeView.__init__(self)
        self._width = width
        self._height = height 
        self.model = QtWidgets.QFileSystemModel()
        self.setModel(self.model)
        self.setIndentation(15)

        # Set home folder and file filters
        if not homeFolder: 
            if os.path.isdir('/home/tiago'):
                #homeFolder = '/home/tiago/Code/py/NeuroDAQanalysis/testData/'
                self.homeFolder = '/home/tiago/Data/Lab.local/'
            elif platform.system()=='Darwin':
                print('Mac OS X detected')
                self.homeFolder = '/Users/'
            elif platform.system()=='Linux':
                self.homeFolder = '/home/'      
            else:
                self.homeFolder = '/'              
        self.model.setRootPath(QtCore.QDir.absolutePath(QtCore.QDir(self.homeFolder)))
        self.setRootIndex(self.model.index(QtCore.QDir.absolutePath(QtCore.QDir(self.homeFolder))))                
        self.model.setNameFilters(['*.hdf5', '*.tdms', '*.abf', '*.avi', '*.mp4' ])
 
        # Hide some default columns
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)   

    def __lt__(self, otherItem):
        """ Reimplement sorting function to sort numbers properly
        """
        column = self.treeWidget().sortColumn()
        item1 = str(self.text(column)) #.toLower())
        item2 = str(otherItem.text(column)) #.toLower())
        
        # Check if there are numbers in both strings to be sorted
        s1 = re.search(r"\d+(\.\d+)?", item1)  # this returns numbers if they exist
        s2 = re.search(r"\d+(\.\d+)?", item2)
        if (bool(s1) & bool(s2)): 
            # Check if there is a mix of numbers and other characters
            base1 = item1.strip(s1.group()) 
            base2 = item2.strip(s2.group())
            if (bool(base1) & bool(base2)):
                if base1==base2:
                    # The basenames are the same, sort by numbers
                    return int(s1.group()) < int(s2.group())
                else:
                    # The basenames are different, sort by characters
                    return item1 < item2
            else:
                # Only one string has numbers and other characters, or both are numbers only
                try:
                    return int(item1) < int(item2)
                except ValueError:         
                    return item1 < item2                             
        else:
            # There are no numbers (or only one string has a number)
            return item1 < item2
        
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)

    def keyPressEvent(self, event):
        """ Specify some key press events.
        """
        super(FileBrowserWidget, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Delete:
            self.fileDeletePressed.emit()


