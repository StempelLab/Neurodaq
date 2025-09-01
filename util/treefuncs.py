""" Functions for managing trees
"""

import sys, os, re, copy
import sip
import h5py
from widgets import h5Item
from PyQt5 import QtGui, QtCore, QtWidgets


def add_treeGroup(browser, tree, level, name):
    if level=='root':
        item = h5Item([name])
        parentWidget = browser.ui.workingDataTree.invisibleRootItem()
        browser.make_nameUnique(parentWidget, item, name)
        tree.addTopLevelItem(item)        
    elif level=='child':
        item = h5Item([name])
        parentWidget = tree.currentItem()
        browser.make_nameUnique(parentWidget, item, name) 
        parentWidget.addChild(item)

def rename_treeItem(browser, tree, text):
    item = tree.currentItem()    
    parentWidget = item.parent()
    if not parentWidget:  # item in top level
        parentWidget = browser.ui.workingDataTree.invisibleRootItem()
    browser.make_nameUnique(parentWidget, item, text)
    
def remove_treeItem(browser, tree):
    """ Remove selected items from the tree. Because data is stored 
    separately also need to deal with it, but deleting the matching
    items from the data list and updating all of the data indexes 
    is a bit of a headache, so just make them empty.
    """ 
    items = tree.selectedItems()
    for item in items:
        if item.listIndex:   # Only dataset items have a listIndex
            browser.ui.workingDataTree.dataItems[item.listIndex] = []       
        sip.delete(item)

def clone_item(item):
    """ Clone h5 item. Useful for Drag & Drop
    """
    i = h5Item(item.text(0))
    i.path = item.path
    i.listIndex = item.dataIndex
    i.originalIndex = item.originalIndex
    i.data = item.data
    return i

def set_loadFolder(browser, tree, homeFolder):
    tree.model.setRootPath(QtCore.QDir.absolutePath(QtCore.QDir(homeFolder)))
    tree.setRootIndex(tree.model.index(QtCore.QDir.absolutePath(QtCore.QDir(homeFolder))))      
    
    

