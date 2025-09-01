Python 3 and Qt5 port from: https://github.com/ineuron/NeuroDAQ-Analysis


NeuroDAQ-Analysis
=================

Analysis enviroment for .HDF5 files, implemented in pure Python 2.7

Currently it allows fast browsing, plotting and analysis of 1-D data.
Numbers can be displayed in a table for exporting elsewhere.


Requirements:
-------------
. The GUI runs on PyQt4
. HDF5 data management is done by the h5py module
. Plotting is done by pyqtgraph. Get it here: http://www.pyqtgraph.org, and install with "python setup.py install"

This package has been tested in Ubuntu and Mac OS X.

For Mac OS X the easiest is to use the Anaconda distribution and just get pyqtgraph.

For Linux get PyQt4 and h5py.
#
To install neurodaq:

First you need access to the institute's GitHub repo. Email scientific computing (Fritz) regarding that.

Then, you visit this website https://gitlab.mpdcdf.mpg.de/mpibr/scic/neurodaq-analysis and download the code.

Create a python environment with python 3.10 and do a pip install of required packages using the requirements.txt file found in the code folder you downloaded from the repository.

##
Start neurodaq by moving to the code folder location and running 'python -m start'.

###
To load files, go to the IPython tab, load your files (.npy, h5) and then import them to neurodaq using ndaq.store_data('name_of_your_array'). 

You should see 'data' appearing on the right-side column.
Using the left-side file explorer column navigate to your video files and double click on them.
The video file should appear on a column right next to the file explorer column. Drag it to the data column.
Go to the video tab. On top you will have the video and on the bottom a plotting space. Click on 'data' and it should show all the rows of your array.
Click on one and then hit the button 'Plot' which is under the plotting area.

Enjoy!
