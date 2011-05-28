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
"""
precrossoverhandle.py
Created by Nick on 2011-05-03.
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPolygonF
from PyQt4.QtGui import QPen, QUndoCommand
from model.enum import StrandType, Parity, BreakType, HandleOrient
import ui.styles as styles


# construct paths for breakpoint handles
def hashMarkGen(path, p1, p2, p3):
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
# end

# create hash marks QPainterPaths only once
_ppRect = QRectF(0, 0, styles.PATH_BASE_WIDTH, styles.PATH_BASE_WIDTH)
_pathCenter = QPointF(styles.PATH_BASE_WIDTH / 2,\
                          styles.PATH_BASE_WIDTH / 2)
_pathUCenter = QPointF(styles.PATH_BASE_WIDTH / 2, 0)
_pathDCenter = QPointF(styles.PATH_BASE_WIDTH / 2, styles.PATH_BASE_WIDTH)
_ppathLU = QPainterPath()
hashMarkGen(_ppathLU, _ppRect.bottomLeft(), _pathDCenter, _pathCenter)
_ppathRU = QPainterPath()
hashMarkGen(_ppathRU, _ppRect.bottomRight(), _pathDCenter, _pathCenter)
_ppathRD = QPainterPath()
hashMarkGen(_ppathRD, _ppRect.topRight(), _pathUCenter, _pathCenter)
_ppathLD = QPainterPath()
hashMarkGen(_ppathLD, _ppRect.topLeft(), _pathUCenter, _pathCenter)


class PreXoverHandleGroup(QGraphicsItem):
    def __init__(self, parent=None):
        """
        Merely initialize a PreXoverHandle buffer
        sets the group's parent to preferably a PathHelixGroup sets each
        PreXoverHandle's parent in the buffer initially to the group
        """
        super(PreXoverHandleGroup, self).__init__(parent)
        self.parent = parent
        self.rect = QRectF(0, 0, 0, 0)
        self.handlesA = []
        self.handlesB = []
        # print parent, "coool", self.parentItem()
        for i in range(128):
            self.handlesA.append(PreXoverHandle(parent=self))
            self.handlesB.append(PreXoverHandle(parent=self))
            # point the two to each other
            self.handlesA[i].setPartner(self.handlesB[i])
            self.handlesB[i].setPartner(self.handlesA[i])
        # end for
        self.activeCount = 0
    # end def
    
    def parentItem(self):
        return self.parent

    def __str__(self):
        return "I am a PXoHG!"

    def boundingRect(self):
        return self.rect
    # end def

    def paint(self, painter, option, widget=None):
        pass
    # end def

    def updateActiveHelix(self, vhelix):
        """
        Collects the locations of each type of PreCrossover from the
        recently activated VirtualHelix vhelix. Each self._index corresponds
        to a pair of PreXoverHandle that must be updated and displayed.
        """
        scafL = vhelix.getLeftScafPreCrossoverIndexList()
        scafR = vhelix.getRightScafPreCrossoverIndexList()
        stapL = vhelix.getLeftStapPreCrossoverIndexList()
        stapR = vhelix.getRightStapPreCrossoverIndexList()
        count = sum([len(scafL), len(scafR), len(stapL), len(stapR)])

        # Process Scaffold PreXoverHandles
        strandtype = StrandType.Scaffold
        ph1 = self.parentItem().getPathHelix(vhelix)
        i = 0
        for [neighbor, index] in scafL:
            if vhelix.evenParity():
                orient1 = HandleOrient.LeftUp
                orient2 = HandleOrient.LeftDown
            else:
                orient1 = HandleOrient.LeftDown
                orient2 = HandleOrient.LeftUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handlesA[i].configure(strandtype, orient1, index, ph1)
            self.handlesB[i].configure(strandtype, orient2, index, ph2)
            self.handlesA[i].setLabel()
            self.handlesB[i].setLabel()
            i += 1
        for [neighbor, index] in scafR:
            if vhelix.evenParity():
                orient1 = HandleOrient.RightUp
                orient2 = HandleOrient.RightDown
            else:
                orient1 = HandleOrient.RightDown
                orient2 = HandleOrient.RightUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handlesA[i].configure(strandtype, orient1, index, ph1)
            self.handlesB[i].configure(strandtype, orient2, index, ph2)
            self.handlesA[i].setLabel()
            self.handlesB[i].setLabel()
            i += 1
        # Process Staple PreXoverHandles
        strandtype = StrandType.Staple
        for [neighbor, index] in stapL:
            if vhelix.evenParity():
                orient1 = HandleOrient.LeftUp
                orient2 = HandleOrient.LeftDown
            else:
                orient1 = HandleOrient.LeftDown
                orient2 = HandleOrient.LeftUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handlesA[i].configure(strandtype, orient1, index, ph1)
            self.handlesB[i].configure(strandtype, orient2, index, ph2)
            self.handlesA[i].setLabel()
            self.handlesB[i].setLabel()
            i += 1
        for [neighbor, index] in stapR:
            if vhelix.evenParity():
                orient1 = HandleOrient.RightUp
                orient2 = HandleOrient.RightDown
            else:
                orient1 = HandleOrient.RightDown
                orient2 = HandleOrient.RightUp
            ph2 = self.parentItem().getPathHelix(neighbor)
            self.handlesA[i].configure(strandtype, orient1, index, ph1)
            self.handlesB[i].configure(strandtype, orient2, index, ph2)
            self.handlesA[i].setLabel()
            self.handlesB[i].setLabel()
            i += 1

        # hide extra precrossoverhandles as necessary
        if self.activeCount > count:
            for i in range(count, self.activeCount):
                self.handlesA[i].hide()
                self.handlesB[i].hide()
            # end for
        # end if
        self.activeCount = count
    # end def
# end class


class PreXoverHandle(QGraphicsItem):
    """
    PreXoverHandle responds to mouse input and serves as an interface
    for adding scaffold crossovers
    """
    pen = QPen(styles.pchstroke, styles.PATH_STRAND_STROKE_WIDTH)
    pen.setCapStyle(Qt.FlatCap)  # or Qt.RoundCap
    pen.setJoinStyle(Qt.RoundJoin)
    baseWidth = styles.PATH_BASE_WIDTH
    _myfont = QFont("Times", 10, QFont.Bold)

    def __init__(self, parent=None):
        """
        Set up a hidden label and boundingbox for PreXoverHandle. Parent
        should always be a PreXoverHandleGroup, whose own parent is a
        PathHelixGroup.
        """
        super(PreXoverHandle, self).__init__(parent)
        self.setParentItem(parent)
        self.rect = QRectF(0, 0, styles.PATH_BASE_WIDTH,\
                                 styles.PATH_BASE_WIDTH)
        self.painterpath = _ppathLD
        self.phg = parent.parentItem()  # this should be a PathHelixGroup
        pathController = parent.parentItem().controller()
        self.undoStack = pathController.mainWindow.undoStack
        self._strandType = None
        self._index = None
        self._orientation = None
        self.partner = None  # partner PreXoverHandle in the pair
        self.setZValue(styles.ZPREXOVERHANDLE)
        self._label = QGraphicsSimpleTextItem("", parent=self)
        self._label.setPos(0, 0)
        self._label.setFont(self._myfont)
        self._label.hide()
        self.hide()
    # end def

    def setPartner(self, pch):
        """
        create a pointer towards it's complementary PreXoverHandle
        """
        self.partner = pch
    # end def

    def pathHelix(self):
        return self.parentItem()
    # end def

    def index(self):
        return self._index
    # end def

    def orientation(self):
        return self._orientation
    # end def

    def setLabel(self):
        self._label.setText("%d" % (self.partner.pathHelix().number()))
        if self._orientation == HandleOrient.RightDown:
            self.rightDrawConfig()
            self.downDrawConfig()
            self.painterpath = _ppathRD
        elif self._orientation == HandleOrient.LeftDown:
            self.leftDrawConfig()
            self.downDrawConfig()
            self.painterpath = _ppathLD
        elif self._orientation == HandleOrient.LeftUp:
            self.leftDrawConfig()
            self.upDrawConfig()
            self.painterpath = _ppathLU
        elif self._orientation == HandleOrient.RightUp:
            self.rightDrawConfig()
            self.upDrawConfig()
            self.painterpath = _ppathRU
        else:
            raise AttributeError("PCH orientation not recognized")
        self._label.show()
        self.show()
    # end def

    def configure(self, strandtype, orientation, index, parent):
        """
        Sets the parent of the PreXoverHandle to its PathHelix, so upon
        reordering of that PathHelix, the PreXoverHandle will redraw
        correctly.
        """
        self.setParentItem(parent)
        self._strandType = strandtype
        self._orientation = orientation
        self._index = index
    # end def

    def rightDrawConfig(self):
        # self.setX(self.baseWidth * self._index)
        self.setPos(self.baseWidth * self._index, self.y())
        offset = -self._label.boundingRect().width() / 2 + self.baseWidth / 2
        # self._label.setX(offset)
        self._label.setPos(offset, self._label.y())
    # end def

    def leftDrawConfig(self):
        # self.setX(self.baseWidth * self._index)
        self.setPos(self.baseWidth * self._index, self.y())
        offset = self._label.boundingRect().width() / 2
        # self._label.setX(self.baseWidth / 2 - offset)
        self._label.setPos(self.baseWidth/2 - offset, self._label.y())
    # end def

    def upDrawConfig(self):
        # self.setY(-1.25 * self.baseWidth)
        # self._label.setY(-0.10 * self.baseWidth)
        self.setPos(self.x(), -1.25*self.baseWidth)
        self._label.setPos(self._label.x(), -0.10*self.baseWidth)
    #end def

    def downDrawConfig(self):
        # self.setY(2.25 * self.baseWidth)
        # self._label.setY(0.48 * self.baseWidth)
        self.setPos(self.x(), 2.25 * self.baseWidth)
        self._label.setPos(self._label.x(), 0.48 * self.baseWidth)
    #end def

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen)
        painter.drawPath(self.painterpath)
    # end def

    def mousePressEvent(self, event):
        """
        This handles installing crossovers
        """
        if event.button() != Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self, event)
        # end else
        else:
            self.installCrossover()
        # end else
    # end def

    def installCrossover(self):
        """Install a crossover: determine which is the upstream (3') base,
        create the corresponding XoverHandlePair, and then push
        the InstallXoverCommand to the undostack, which updates the model
        and causes the ui refresh."""
        # Determine upstream base
        if self._orientation in [HandleOrient.LeftUp,\
                                 HandleOrient.RightDown]:  # 3-prime clicked
            fromHelix = self.pathHelix().vhelix()
            fromIndex = self.index()
            toHelix = self.partner.pathHelix().vhelix()
            toIndex = self.partner.index()
        else:  # 5-prime clicked
            toHelix = self.pathHelix().vhelix()
            toIndex = self.index()
            fromHelix = self.partner.pathHelix().vhelix()
            fromIndex = self.partner.index()
        # Create XoverHandlePair and store references
        fromHelix.installXoverTo(StrandType.Scaffold, \
                                        fromIndex, toHelix, toIndex)
    # end def
# end class
