""" Functions for dealing with images
"""

import numpy as np
import tifffile

def array2image(data, shape):
    """ Converts a 1D array of pixels into a 
    2D array with shape 'shape'. 
    
    'shape' is a tuple, eg: (512, 512)
    """
    
    image = np.reshape(data, shape)
    return image

def saveTiff(items, basename):
    """ Save 2D arrays in selected H5 items to 
    individual tiff files, using the tifffile module.

    'items' is a list of H5 items      
    """
    for n in np.range(len(items)):
        tifffile.imsave(item.data, basename+'_'+str(n)+'.tif')
    
