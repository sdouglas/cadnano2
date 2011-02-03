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
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QByteArray, QString, QStringList, QVariant
from PyQt4.QtCore import QXmlStreamReader, QXmlStreamWriter


NODETAG = "node"
NAMETAG = "NAMETAG"
OBJ_ID = "objectid"
INST_ID = "instanceid"

KEY, NODE = range(2)

NAME,HIDDEN,LOCKED = range(3)

class Node(object):
    """
    """
    ntype =""
    def __init__(self, name="", obj_inst=None,node_attribute=None, parent=None):
        """
        We could do this one of two ways, straight add children, or,
        keep children sorted when they get added.  Keeping them sorted
        complicates the undo process
        """
        super(Node,self).__init__()    
        self.parent = parent
        self.children = []
        
        self.name = name
                
        if self.parent != None:
            self.parent.addChild(self)
        #end if
        
        self.object_instance = obj_inst
        self.node_attr = node_attribute
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
        ind = bisect.bisect_right(self.children, (child.orderKey(), child) )
        self.children.insert(ind, (child.orderKey(), child) )
        return ind
    # end def
    
    # def insertChild(self, row, child):
    #     """
    #     """
    #     child.parent = self
    #     self.children.insert(row, ('a', child))
    # # end def

    def addChild(self,child):
        """
        """
        self.insertChild(child)
        # child.parent = self
        # self.children.append(child.child)
    # end def
    
    def swapChildren(self,oldRow, newRow):
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
        if len(self.children) == 0:
            return False
        # end if
        #print "am I a child node?"
        return isinstance(self.children[0][NODE], Node)
    # end def

# end class
        
class TreeModel(QAbstractItemModel):
    """
    """
    def __init__(self,parent=None):
        """
        """
        super(QAbstractItemModel,self).__init__(parent)    
        self.headers = []
        self.root = Node()
        self.cutNode = 0
        self.lastrow = 0    # row of last single row insertion
        self.maxCompression  = 9
        self.mime_type = QString("application/cadnano.xml.node.z") 
        
        # must set this in order for anything to work!
        self.COLUMNCOUNT = 3
        self.columns = self.COLUMNCOUNT
        
        self.filename = ""
    # end def

    def flags(self, index):
        """QAbstractItemModel required"""
        theFlags = QAbstractItemModel.flags(self,index)
        if index.isValid():
            theFlags |= Qt.ItemIsSelectable | Qt.ItemIsEnabled 
        if index.column() == NAME:
            theFlags |= Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        # end if
        return theFlags
            
    # end def

    def rowCount(self, parentindex=None):
        """
        QAbstractItemModel required
        parentindex: QModelIndex
        """
        
        try:
            node = self.nodeFromIndex(parentindex)
            if node is None or not node.hasKids():
                return 0
            # end if
            return len(node)
        except:
            return 0
    # end def

    def columnCount(self, parent):
        """
        QAbstractItemModel required
        """
        return self.columns
    # end def
    
    def nodeFromIndex(self, index):
        """
        """
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root
    # end def
    
    def index(self, row, column, parentindex):
        """QAbstractItemModel required"""
        assert self.root
        node = self.nodeFromIndex(parentindex)
        assert node is not None
        return self.createIndex(row, column, node.childAtRow(row))
    
    # end def

    def parent(self, index):
        """"""
        node = self.nodeFromIndex(index)
        if node is None:
            return QModelIndex()
        # end if
        parentnode = node.parent
        if parentnode is None:
            return QModelIndex()
        # end if
        grandparentnode = parentnode.parent
        if grandparentnode is None:
            return QModelIndex()
        # end if
        row = grandparentnode.rowOfChild(parentnode)
        assert row != -1
        return self.createIndex(row, 0, parentnode)    
    # end def
    
    def headerData(self, section, orientation, role):
        """QAbstractItemModel required"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            #print "header confirmed"
            return QVariant(self.headers[section])
        return QVariant()
    # end def

    def data(self, index, role):
        """QAbstractItemModel required"""
        # if role == Qt.DecorationRole:
        #     node = self.nodeFromIndex(index)
        #     if node is None:
        #         return QVariant()
        #     else:
        #         return QVariant(node.toString())
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop|Qt.AlignLeft))
        if role != Qt.DisplayRole:
            return QVariant()
        node = self.nodeFromIndex(index)
        assert node is not None
        if index.column() == NAME:
            #print "yes!"
            return QVariant(node.toString())
        else:
            #print "no!"
            QVariant(QString("poo"))
    # end def

    def setData(self, index, value, role):
        """QAbstractItemModel required"""
        #print "setting data...."
        if not index.isValid() or index.column() != NAME:
            return False
        # end if
        node = self.nodeFromIndex(index)
        #print "setting %s" % node.name
        if node != None:
            if role == Qt.EditRole:
                temp = value.toString()
                if temp != "":
                    node.name = value.toString()
                # end if
                # print "new name: %s" % node.name
            # end if
            # elif role == Qt.CheckStateRole:
            #     node.setDone(value.toBool())
            # # end elif
            else:
                #print "not an edit role"
                return False
            # end else
            #print "setdata: Data Changed!"
            self.dataChanged.emit(index,index)
            return True
        # end if
        return False
    # end def

    def insertRow(self, row, parentindex,node=None):
        """"""
        if parentindex.isValid():
            parentnode = self.nodeFromIndex(parentindex)
        # end if
        else:
            return False
        # end else
        self.beginInsertRows(parentindex,row, row)
        # TODO Fix this !!!!!
        if node == None:
            return False
        # end if
        print "inserted %s" % node.name
        if node.parent == None:
            #parentnode.insertChild(row,node)
            self.lastrow = parentnode.insertChild(node)
        # end if
        self.endInsertRows()
        return True
    # end def

    def insertRows(self, row, count, parentindex,node=None):
        """
        Need to understand insertRows better
        the type of node going in must be obvious
        """
        print "insertRows called for some reason"
        if not self.root == None:   # if there is no root node, we must create one
            if node == None:
                self.root = Node()
            else:
                self.root = node
        # end if
        if parentindex.isValid():
            parentnode = self.nodeFromIndex(parentindex)
        # end if
        else:
            parentnode = self.root
        # end else
        self.beginInsertRows(parentindex,row, row + count - 1)
        # TODO Fix this !!!!!
        for i in range(count):
            node = Node()
            #parentnode.insertChild(row,node)
            parentnode.insertChild(node)
        # end for
        self.endInsertRows()
        return True
    # end def
    
    def removeRows(self, row, count, parent):
        """QAbstractItemModel required"""
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
    
    # def clear(self):
    #     """
    #     """
    #     del self.root
    #     self.root = 0
    #     del cutNode
    #     cutNode = 0
    #     #self.reset()
    # # end def
    
    def mimeData(indices):
        """QAbstractItemModel drag and drop required"""
        assert indices.count()
        if indices.count() != 1:
            return 0
        node = nodeFromIndex(indices.at(0))
        if node:
            mime_data = QMimeData()
            xml_data = QByteArray()
            writer =  QXmlStreamWriter(xml_data)
            self.writeNodeAndChildren(writer,node)
            mime_data.setData(self.mime_type,QByteArray.qCompress(xml_data, self.maxCompression))
            return mime_data
        # end if
        return 0
    # end def
    
    def dropMimeData(mime_data, action, row, column, parent):
        """QAbstractItemModel drag and drop required"""
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
            self.readNode(reader, node)
            self.endInsertRows()
            return True
        # end if
        return False
    # end def
    
    def mimeTypes():
        """QAbstractItemModel drag and drop required"""
        return QStringList(self.mime_type)
    # end def
    
    def supportedDragActions(self):
        """QAbstractItemModel drag and drop required"""
        return Qt.MoveAction# | Qt.CopyAction
    # end def
        
    def supportedDropActions(self):
        """QAbstractItemModel drag and drop required"""
        return Qt.MoveAction# | Qt.CopyAction
    # end def
    
    def writeNodeAndChildren(writer, node):
        """
        This needs to be written for all types of tags
        
        self.name = name
        self.ntype = "part" # the type of node i.e. Assembly, Part, etc
        self.object_id = 'something'
        self.checked = True
        self.locked = False 
        self.done = False
        """
        if node != self.root:            
            writer.writeStartElement(NODETAG)
            writer.writeAttribute(NAMETAG, node.name)
            writer.writeAttribute(NTYPE, node.ntype)
            #writer.writeAttribute(OBJ_ID, node.object_id)
            #writer.writeAttribute(INST_ID, node.instance_id)
        # end if
        for child in node.children:
            self.writeNodeAndChildren(writer, child[NODE])
        # end for
        if node != self.root:
            writer.writeEndElement() 
        # end if
    # end def
    
    def readNode(reader, node):
        """
        readNode requires some knowledge of all the types of nodes to properly create the node
        """
        while not reader.atEnd():
            reader.readNext()
            if reader.isStartElement():
                if reader.name() == NODETAG:
                    name = reader.attributes().value(NAMETAG).toString()
                    ntype = reader.attributes().value(NTYPE).toString() 
                    #id_obj = reader.attributes().value(OBJ_ID)
                    #id_inst = reader.attributes().value(INST_ID)
                    #generateNode(name,ntype, id_obj,id_inst)
                # end if
            # end if
            elif reader.isEndElement():
                if reader.name() == NODETAG:
                    assert node
                    node = node.parent
                    assert node
                # end if
            # end elif
        # end while
    # end def
    
    #def generateNode(name, ntype, id_obj,id_inst):
    #    pass
    # end def

    # def load(self):
    #     """
    #     """
    #     clear()
    #     self.root = Node()
    #     reader = QXmlStreamReader(soome)
    #     readNode(reader, self.root)    
    #     if reader.hasError():
    #         pass
    # # end def

# end class

