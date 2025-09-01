import numpy as np
import matplotlib.pylab as plt
from console import utils as ndaq


# Get selected images
items = browser.ui.workingDataTree.selectedItems()
        
# Make 3D array
image = [i.data for i in items]
image = np.array(image)

# Show
browser.ui.dataImageWidget.setImage(image)
