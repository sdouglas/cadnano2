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

import bisect
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QByteArray, QString
from PyQt4.QtCore import QXmlStreamReader, QXmlStreamWriter
import data.json_io as json_io



KEY, NODE = range(2)

class Node(object):
    """
    """
    ntype="extra" # the type of node i.e. Assembly, Part, etc
    
    def __init__(self, name, obj_id, inst_id, parent=None):
        """
        We could do this one of two ways, straight add children, or,
        keep children sorted when they get added.  Keeping them sorted
        complicates the undo process
        """
        super(Node,self).__init__()    
        self.parent = parent
        self.children = []
        
        parent.addChild(self)
        
        self.name = name
        self.object_id = obj_id
        self.instance_id = inst_id
    # end def
    
    def orderKey(self):
        """
        """
        return self.name.lower()
    # end def

    def toString(self):
        """
        """
        return self.name
    # end def

    def __str__(self):
        return self.name
    # end def
    
    def __len__(self):
        """
        """
        return len(self.children)
    # end def

    def childAtRow(self, row):
        """
        """
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]
    # end def

    def rowOfChild(self, child):
        """
        """
        for i, kid in enumerate(self.children):
            if kid[NODE] == child:
                return i
            # end if
        # end for
        return -1
    # end def

    def childWithKey(self, key):
        """
        """
        if not self.children:
            return None
        # end if
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        # end if
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        # end if
        return None
    # end def

    def insertChild(self, child):
        """
        """
        child.parent = self
        # insert the child in assuming that self.children is already sorted
        bisect.insort(self.children, (child.orderKey(), child))
    # end def
    
    # def insertChild(self, row, child):
    #     """
    #     """
    #     child.parent = self
    #     self.children.insert(row, child)
    # # end def

    def addChild(child):
        """
        """
        insertChild(self, child)
        # child.parent = self
        # self.children.append(child.child)
    # end def
    
    def swapChildren(oldRow, newRow):
        """
        This is used assuming that order doesn't matter
        """
        tempNew = self.children[newRow]
        self.children[newRow] = self.children[oldRow]
        self.children[oldRow] = tempNew
    # end def

    def takeChild(self, row):
        child = self.children[row][NODE]
        assert child
        child.parent = 0
        return child
    # end def

    def hasKids(self):
        """
        """
        if not self.children:
            return False
        # end if
        return isinstance(self.children[0][NODE], Node)
    # end def

    def writeNodeAndChildren(writer, treemodel):
        """
        This needs to be written for all types of tags
        
        self.name = name
        self.ntype = "part" # the type of node i.e. Assembly, Part, etc
        self.object_id = 'something'
        self.checked = True
        self.locked = False 
        self.done = False
        """
        if self != treemodel.root:            
            writer.writeStartElement(json_io.NODETAG)
            writer.writeAttribute(json_io.NAME, node.name())
            writer.writeAttribute(json_io.NTYPE, node.ntype())
            writer.writeAttribute(json_io.OBJ_ID, node.object_id)
            writer.writeAttribute(json_io.INST_ID, node.instance_id)
        # end if
        for child in self.children:
            child[NODE].writeNodeAndChildren(writer, treemodel)
        # end for
        if self != treemodel.root:
            writer.writeEndElement() 
        # end if
    # end def

    def readNode(reader, treemodel):
        """
        readNode requires some knowledge of all the types of nodes to properly create the node
        """
        while not reader.atEnd():
            reader.readNext()
            if reader.isStartElement():
                if reader.name() == json_io.NODETAG:
                    name = reader.attributes().value(json_io.NAME).toString()
                    ntype = reader.attributes().value(json_io.NTYPE).toString() 
                    id_obj = reader.attributes().value(json_io.OBJ_ID)
                    id_inst = reader.attributes().value(json_io.INST_ID)
                    #if ntype == "part"#PartNode().ntype:
                    #   node = PartNode(name, id_obj, id_inst, self)
                    # end if
                    #elif ntype == AssemblyNode.ntype:
                    #    node = AssemblyNode(name,id_obj, id_inst, self)
                    # end elif
                # end if
            # end if
            elif reader.isEndElement():
                if reader.name() == json_io.NODETAG:
                    assert node
                    node = node.parent
                    assert node
                # end if
            # end elif
        # end while
    # end def
# end class
        
class TreeModel(QAbstractItemModel):
    """
    """
    def __init__(self):
        from data.assembly import AssemblyNode
        from data.part import PartNode
        
        super(QAbstractItemModel,self).__init__()    
        self.columns = 0
        self.headers = []
        self.root = AssemblyNode('ASM_0', 0, 0, None)
        self.cutNode = 0
        self.maxCompression  = 9
        self.mime_type = QString("application/cadnano.xml.node.z") 
        self.COLUMNCOUNT = 3
    # end def

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
        if node is None or not node.hasKids():
            return 0
        # end if
        return len(node)


    def columnCount(self, parent):
        """
        """
        return self.columns
    
    def nodeFromIndex(self, index):
        """
        """
        if index.isValid():
            return index.internalPointer()
        else:
             return self.root
    # end def
    
    def index(self, row, column, parent):
        """
        """
        assert self.root
        node = self.nodeFromIndex(parent)
        assert node is not None
        return self.createIndex(row, column, node.childAtRow(row))
    
    # end def

    def parent(self, index):
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

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
           role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return QVariant(self.headers[section])
        return QVariant()
    # end def

    def data(self, index, role):
        """
        """
        if not self.root or not index.isValid() or \
            index.column() < 0 or index.column() >= self.COLUMNCOUNT:
            return QVariant()
        # end if
        node = self.nodeFromIndex(index)
        assert node is not None
        if node:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                if index.column() == NAME:
                    return QVariant(node.name)
                else:
                    return QVariant(QString(""))
                # end if
            # end if
            if role == Qt.CheckStateRole and index.column() == NAME:
                return QVariant(int(Qt.Checked if item.isDone() else Qt.Unchecked))
            # end if
            if role == Qt.TextAlignmentRole:
                return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
            # end if
            if (role == Qt.DecorationRole) and (index.column() == True):
                pass
            # end if
        # end if
        return QVariant()   # Default return
    # end def

    def setData(self, index, value, role):
        """
        """
        if not index.isValid() or index.column() != NAME:
            return False
        # end if
        node = self.nodeFromIndex(index)
        if node:
            if role == Qt.EditRole:
                node.name = value.toString()
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
                
    def insertRows(self, row, count, parent):
        """
        Need to understand insertRows better
        the type of node going in must be obvious
        """
        if not self.root:   # if there is no root node, we must create one
            self.root = AssemblyNode('ASM_0', self.idbank.issue(), parent=None)
        # end if
        if parent.isValid():
            parentNode = self.nodeFromIndex(parent)
        # end if
        else:
            parentNode = self.root
        # end else
        self.beginInsertRows(parent,row, row + count - 1)
        # TODO Fix this !!!!!
        for i in range(count):
            node = Node()
            parentNode.insertChild(row,node)
        # end for
        self.endInsertRows()
        return True
    # end def
    
    def removeRows(self, row, count, parent):
        """
        """
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
            # del node.takeChild(row)
            # might not work as expected
            c = node.takeChild(row)
            del c
        # end for
        self.endRemoveRows()
        return True
    # end def
    
    def isChecked(self, index):
        """
        """
        if not index.isValid():
            return False
        # end if
        return self.data(index,Qt.CheckStateRole).toInt() == Qt.Checked
    # end def
    
    def hasCutItem(self):
        """
        """
        return self.cutItem
    # end def
    
    def moveItem(self, parent, oldRow, newRow):
        """
        """
        assert (0 <= oldRow) and (oldRow < parent.childCount()) and \
               (0 <= newRow) and (newRow < parent.childCount())
        parent.swapChildren(oldRow,newRow)
        oldIndex = self.createIndex(oldRow, 0, parent.childAt(oldRow))
        newIndex = self.createIndex(newRow, 0, parent.childAt(newRow)) 
    # end def
    
    def moveUp(self, index):
        """
        """
        if not index.isValid() or index.row() <= 0:
            return idex
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent
        assert parent
        return self.moveItem(parent,index.row(), index.row() -1)
    # end def
    
    def moveDown(self, index):
        """
        """
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent
        newRow = index.row() + 1
        if not parent or parent.childCount() <= newRow:
            return index
        # end if
        return self.moveItem(parent, index.row(), newRow)
    # end def
    
    def cut(self, index):
        """
        """
        if not index.isValid():
            return index
        # end if
        del self.cutNode
        self.cutNode = self.nodeFromIndex(index)
        assert cutNode
        parent = cutNode.parent
        assert parent
        row = parent.rowOfChild(cutNode)
        assert row == index.row()
        self.beginRemoveRows(index.parent(), row, row)
        child  = parent.takeChild(row)
        self.endRemoveRows()
        assert child == self.cutNode
        child = 0
        if row > 0:
            row -= 1
            return self.createIndex(row,0,parent.childAt(row))
        # end if
        grandParent = parent.parent
        assert grandParent
        return self.createIndex(grandParent.rowOfChild(parent), 0, parent)
        
    # end def
    
    def paste(self, index):
        """
        """
        if not index.isValid() or not self.cutNode:
            return index
        # end if
        sibling = self.nodeFromIndex(index)
        assert sibling
        parent = sibling.parent
        assert parent
        row = parent.rowOfChild(sibling) + 1
        self.beginInsertRows(index.parent(), row, row)
        parent.insertChild(row, self.cutNode)
        child = self.cutNode
        self.cutNode = 0
        self.endInsertRows()
        return self.createIndex(row,0,child)
    # end def
    
    def promote(self, index):
        """
        """
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent
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
    
    def demote(self, index):
        """
        """
        if not index.isValid():
            return index
        node = self.nodeFromIndex(index)
        assert node
        parent = node.parent
        assert parent
        row = parent.rowOfChild(node)
        if row == 0:
            return index # No preceding sibling to move this under
        # end if
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
        """
        """
        del self.root
        self.root = 0
        del cutNode
        cutNode = 0
        #self.reset()
    # end def
    
    def setCurrentIndex(index):
        """
        """
        if index.isValid():
            self.treeView.scrollTo(index)
            self.treeView.setCurrentIndex(index)
        # end if
    # end def
    
    def mimeData(indices):
        """
        """
        assert indices.count()
        if indices.count() != 1:
            return 0
        node = nodeFromIndex(indices.at(0))
        if node:
            mime_data = QMimeData()
            xml_data = QByteArray()
            writer =  QXmlStreamWriter(xml_data)
            node.writeNodeAndChildren(writer,self)
            mime_data.setData(self.mime_type,QByteArray.qCompress(xml_data, self.maxCompression))
            return mime_data
        # end if
        return 0
    # end def
    
    def dropMimeData(mime_data, action, row, column, parent):
        """
        """
        if action == Qt.IgnoreAction:
            return True
        if action != Qt.MoveAction or column > 0 or \
            not mime_data or not mime_data.hasFormat(self.mime_type):
            return False
        node = nodeFromIndex(parent)
        if node:
            xml_data = QByteArray.qUncompress(mime_data.data(self.mime_type))
            reader = QXmlStreamReader(xml_data)
            if row == -1:
                if parent.isValid():
                    row = parent.row()
                else:
                    row = self.root.childCount()
            # end if
            self.beginInsertRows(parent, row, row)
            node.readTasks(reader, self)
            self.endInsertRows()
            return True
        # end if
        return False
    # end def
    
    def supportedDragActions(self):
        """
        """
        return Qt.MoveAction# | Qt.CopyAction
        
    def supportedDropActions(self):
        """
        """
        return Qt.MoveAction# | Qt.CopyAction
        
    def load(self):
        """
        """
        clear()
        self.root = Node()
        reader = QXmlStreamReader(soome)
        readNode(reader, self.root)    
        if reader.hasError():
            pass
    # end def
# end class

    
    