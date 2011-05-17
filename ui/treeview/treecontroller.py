# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

from PyQt4.QtGui import QAbstractItemView, QTreeView
from PyQt4.QtCore import QObject, QString, pyqtSignal
from ui.partnode import PartNode
from ui.assemblynode import AssemblyNode
from treemodel import TreeModel
from model.assembly import Assembly


class TreeController(QObject):

    def __init__(self, treeview):
        super(TreeController, self).__init__()
        self.treeview = treeview
        self.treeview.setSelectionBehavior(QTreeView.SelectItems)
        self.treeview.setUniformRowHeights(True)
        headers = ["item", "visible", "lock"]
        self.treemodel = TreeModel(self.treeview)
        self.treemodel.headers = headers
        self.treeview.setDragDropMode(QAbstractItemView.InternalMove)
        #self.win.treeview.setItemDelegateForColumn(0, QString())
        self.treeview.setAllColumnsShowFocus(True)
        self.treeview.setModel(self.treemodel)

        # insert the base level assembly
        index = self.treeview.currentIndex()
        nodeparent = self.treemodel.nodeFromIndex(index)
        node = AssemblyNode("Assembly", Assembly(), None, None)

        if self.treemodel.insertRow(0, index, node):
            # set index to the inserted child
            index = self.treemodel.index(0, 0, index)
            self.setCurrentIndex(index)
        # end if
        self.createConnections()
    # end def

    def createConnections(self):
        # QItemSelectionModel.currentChange emits the previous and current
        # selected QModelIndex, but we don't use those values
        #self.treeview.selectionModel().currentChanged.connect(self.updateUi)
        #self.treeview.activated.connect()
        # 
        #self.treemodel.dataChanged.connect(self.setDirty_ind)
        #self.treemodel.rowsRemoved.connect(self.setDirty)
        #self.treemodel.modelReset.connect(self.setDirty)

        # clicked is a QAbstractItemView signal
        self.treeview.clicked.connect(self.activated)
    # end def

    def setCurrentIndex(self,index):
        if index.isValid():
            self.treeview.scrollTo(index)
            self.treeview.setCurrentIndex(index)
        # end if
    # end def

    def addPartNode(self,name,partInst):
        """
        Adds a part to the tree model
        Makes sure it adds to the closest parent assembly if a part is the 
        current selected item
        """
        index = self.treeview.currentIndex()    # this is a QModelIndex
        nodeparent = self.treemodel.nodeFromIndex(index)

        # must make it an assembly that we insert at
        if nodeparent.ntype != AssemblyNode.ntype:                                     
            index = index.parent()              # returns the parent model index
            nodeparent = nodeparent.parent      # go to the parent
        # end if

        #node = PartNode(name, partInst,None, nodeparent)
        node = PartNode(name, partInst,None, None)

        # currently we insert the new node first in the list but 
        # treemodel handles keeping things alphabetical
        if self.treemodel.insertRow(0, index,node):
            # set index to the inserted child
            index = self.treemodel.index(self.treemodel.lastrow, 0, index)
            self.setCurrentIndex(index)
            #self.treeview.edit(index)
            #self.treemodel.reset()
        # end if
    # end def

    def cut(self):
        """
        returns if the treemodel was able to cut something
        """
        index = self.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.cut(index))
        return self.treemodel.hasCutItem()
    # end def

    def paste(self):
        index = self.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.paste(index))
    # end def

    def moveUp(self):
        index = self.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.moveUp(index))
    # end def

    def moveDown(self):
        index = self.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.moveDown(index))
    # end def

    def promote(self):
        index = self.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.promote(index))
    #end def

    def demote(self):
        index = self.win.treeview.currentIndex()
        self.setCurrentIndex(self.treemodel.demote(index))
    #end def

    def hideOrShowNode(self,hide, index):
        """"""
        hideThisOne = hide #and self.treemodel.isChecked(index)
        if index.isValid():
            self.treeview.setRowHidden(index.row(), index.parent(), hideThisOne)
        # end if
        if not hideThisOne:
            for row in range(self.treemodel.rowCount(index)):
                self.hideOrShowNode(hide, self.treemodel.index(row, 0, index))
            # end for
        # end if
    # end def

    def activated(self, index):
        """"""
        node = self.treemodel.nodeFromIndex(index)
        if node.ntype==PartNode.ntype:
            node.object_instance.partselected.emit()
            #self.partselected.emit(node.ntype, node.object_id,node.instance_id)
            
# end class
