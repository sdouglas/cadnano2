#!/usr/bin/env python
# encoding: utf-8

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

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt


class BranchNode(object):
    """
    
    """
    def __init__(self, name, parent=None):
        """
        
        """
        super(BranchNode,self).__init__()    
        self.name = name
        self.parent = parent
        self.children = []
    # end def
# end class
        
class LeafNode(object):
    """
    
    """
    def __init__(self, parent=None):
        """
        
        """
        super(LeafNode,self).__init__()    
        self.parent = parent
    # end def
    
# end class

class TreeModel(QAbstractItemModel):
    """
    """
    def __init__():
        super(QAbstractItemModel,self).__init__(parent)    
        self.columns = 0
        self.headers = []
        self.root = BranchNode()
        self.cutNode = 0
        
    def flags(self, index):
        """
        """
        theFlags = QAbstractItemModel.flags(index)
        if index.isValid():
            theFlags |= Qt.ItemIsSelectable | \
             Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        # end if
        return theFlags
            
    # end def
    
    
    def rowCount(self, parent):
        """
        parent: QModelIndex
        """
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)


    def columnCount(self, parent):
        return self.columns
    
    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root
    
    def index(self, row, column, parent):
        """
        """
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))
    
    # end def
    
    
    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)
        
    # end def
    
    def headerData(self,section,orientation,role):
        """
        """
        if orientation == Qt.Horizontal and \
            role == Qt.DisplayRole:
            if section == NAME:
                return "Task/Subtask/..."
            elif section == TODAY:
                return "Time (Today)"
            elif section == TOTAL:
                return "Tme (Total)"
        # end if
        return QVariant()
    # end def
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
           role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return QVariant(self.headers[section])
        return QVariant()
    # end def
    
    #def setHeaderData(self, index, value, roleorientation, f):
        
    # end def

    def data(self, index, role):

    # end def
    
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, BranchNode):
            return QVariant(node.toString()) \
                if index.column() == 0 else QVariant(QString(""))
        return QVariant(node.field(index.column()))
    # end def
    
    def setData(self, index, value, role):
        if not index.isValid() or index.column() != NAME:
            return False
        node = self.nodeFromIndex(index)
        if node:
            if role == Qt.EditRole:
                node.setName(value.toString())
            # end if
            elif role == Qt.CheckStateRole:
                node.setDone(value.toBool())
            # end elif
            else:
                return False
            # end else
            self.dataChanged.emit(index,index)
            return true
        # end if
        return False
    # end def
                
    def insertRows(self,row,count, parent):
        if not self.root:
            self.root = BranchNode()
        if parent.isValid():
            parentNode = self.nodeFromIndex(parent)
        else:
            parentNode = self.root
        # end else
        self.beginInsertRows(parent,row, row + count - 1)
        for i in range(count):
            node = Branch()
            parentNode.insertChild(row,node)
        # end for
        self.endInsertRows()
        return True
    # end def
    
    def removeRows(self, row, count, parent):
        if not self.root:
            return False
        # end if
        if parent.isValid():
            node = self.nodeFromIndex(parent)
        # end if
        else:
            node = self.root
        # end else
        self.beginRemoveRows(parent,row, row + count - 1)
        for i in range(count):
            del node.takeChild(row)
        # end for
        self.endRemoveRows()
        return True
    # end def
    
    def isChecked(self, index):
        if not index.isValid():
            return False
        # end if
        return self.data(index,Qt.CheckStateRole).toInt() == Qt.Checked
    # end def
    
    def hasCutItem(self):
        
    # end def
    
    def moveItem(self,parent, oldRow, newRow):
        assert 0 <= oldRow and oldRow < parent.childCount() and \
                0 <= newRow and newRow < parent.childCount():
        parent.swapChildren(oldRow,newRow)
        oldIndex = self.createIndex(oldRow, 0, parent.childAt(oldRow))
        newIndex = self.createIndex(newRow, 0, parent.childAt(newRow))
    # end def
    
    def moveUp(self, index):
        if not index.isValid() or index.row() <= 0:
            return idex
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent()
        assert parent
        return self.moveItem(parent,index.row(), index.row() -1)
    # end def
    
    def moveDown(self, index):
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent()
        newRow = index.row() + 1
        if not parent or parent.childCount() <= newRow
            return index
        # end if
        return self.moveItem(parent, index.row(), newRow)
    # end def
    
    def cut(self, index):
        if not index.isValid():
            return index
        del self.cutNode
        self.cutNode = self.nodeFromIndex(index)
        assert cutNode
        parent = cutNode.parent()
        assert parent
        row = parent.rowOfChild(cutNode)
        assert row == index.row()
        self.beginRemoveRows(index.parent(), row, row)
        child  = parent.takeChild(row)
        self.endRemoveRows()
        assert child = self.cutNode
        child = 0
        if row > 0:
            row -= 1
            return self.createIndex(row,0,parent.childAt(row))
        # end if
        grandParent = parent.parent()
        assert grandParent
        return self.createIndex(grandParent.rowOfChild(parent), 0, parent)
        
    # end def
    
    def paste(self, index):
        if not index.isValid() or not self.cutNode:
            return index
        sibling = self.nodeFromIndex(index)
        assert sibling
        parent = sibling.parent()
        assert parent
        row = parent.rowOfChild(sibling) + 1
        beginInsertRows(index.parent(), row, row)
        parent.insertChild(row, self.cutNode)
        child = self.cutNode
        self.cutNode = 0
        endInsertRows()
        return self.createIndex(row,0,child)
    # end def
    
    def promote(self, index):
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent()
        assert parent
        if parent == self.root:
            return index # Already top level item
        row = parent.rowOfChild(node)
        child = parent.takeChild(row)
        assert child == node
        row = grandParent.rowOfChild(parent)+1
        grandParent.insertChild(row,child)
        newIndex = self.createIndex(row,0,child)
        self.dataChanged.emit(newIndex,newIndex)
        return newIndex
    # end def
    
    def demote (self,index):
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent()
        assert parent
        row = parent.rowOfChild(node)
        if row == 0:
            return index # No preceding sibling to move this under
        child = parent.takeChild(row)
        assert child == node
        sibling = parent.childAr(row-1)
        assert sibling
        sibling.addChild(child)
        newIndex = self.createIndex(sibling.childCount()-1,0,child)
        self.dataChanged.emit(newIndex,newIndex)
        return newIndex
    # end def
    
    def clear(self):
        del self.root
        self.root = 0
        del cutNode
        cutNode = 0
        self.reset()
    # end def
    
    def setCurrentIndex(index):
        if index.isValid():
            self.treeView.scrollTo(index)
            self.treeView.setCurrentIndex(index)
        # end if
    # end def
    
    