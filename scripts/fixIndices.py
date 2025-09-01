# Fix protocol indices when they are screwed up and non-integer
# Use by selecting "Indices" item

import numpy as np
from console import utils as ndaq

# Get item
item = browser.ui.workingDataTree.selectedItems()[0]

# Make everthing above a threshold = 2 ('triggers') 
# This will of course screw up non triggers, sort out later
ths = 0.5
i = item.data>ths
item.data[i] = 2

