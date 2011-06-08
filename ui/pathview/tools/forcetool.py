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
forcetool.py

Created by Nick on 2011-05-18
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush, QFont
from PyQt4.QtGui import QGraphicsItem, QGraphicsSimpleTextItem
from PyQt4.QtGui import QPainterPath
from PyQt4.QtGui import QPen
from model.enum import HandleOrient
import ui.styles as styles
from ui.pathview.pathhelix import PathHelix
from ui.pathview.pathhelixgroup import PathHelixGroup
from abstractpathtool import AbstractPathTool

class ForceTool(AbstractPathTool):
    def __init__(self, parent=None, rightClickOnly=False):
        super(ForceTool, self).__init__(parent)
        self.hide()
        self.setZValue(styles.ZPATHTOOL)
        self.base1 = None
        self.rightClickOnly = rightClickOnly
    
    def paint(self, painter, option, widget=None):
        pass

    def baseFromLocation(self, phg, posScene):
        pathHelix = phg.pathHelixAtScenePos(posScene)
        if pathHelix:
            posItem = pathHelix.mapFromScene(posScene)
            strandType, idx = pathHelix.baseAtLocation(posItem.x(), posItem.y())
            vh = pathHelix.vhelix()
            base2 = (vh, strandType, idx)
        else:
            base2 = None
        return base2
         
    def mousePressPathHelix(self, pathHelix, event):
        # Drags that are active on mouse press must end
        self.updateDrag(pathHelix, event, mustEnd=True, canStart=True)
    
    def mouseMovePathHelix(self, pathHelix, event):
        self.updateDrag(pathHelix, event)

    def mouseReleasePathHelix(self, pathHelix, event):
        self.updateDrag(pathHelix, event, canEnd=True)
        
    def hoverMovePathHelix(self, pathHelix, event):
        self.updateDrag(pathHelix, event)

    def hoverMovePathHelixGroup(self, phg, event):
        self.updateDrag(phg, event)

    def updateDrag(self, ph, event, canStart=False, canEnd=False, mustEnd=False):
        scenePos = ph.mapToScene(QPointF(event.pos()))
        if isinstance(ph, PathHelix):
            phg = ph.pathHelixGroup()
        elif isinstance(ph, PathHelixGroup):
            phg = ph
        else:
            assert(False)
        destBase = self.baseFromLocation(phg, scenePos)

        didEnd = False
        if self.base1==None and canStart:  # Start drag
            assert(destBase)
            self.base1 = destBase
            vh = destBase[0]
            vh.setSandboxed(True)
        elif not self.base1:
            return
        elif canEnd and not destBase==self.base1 or\
             mustEnd:  # End drag
            didEnd = True
            vh = self.base1[0]
            vh.setSandboxed(False)
        else:  # In the middle of a drag
            vh = self.base1[0]
            sandboxUndoStack = vh.undoStack()
            # Ensure sandboxing worked or we get mad popping of the
            # document undo stack
            assert(sandboxUndoStack != vh.part().undoStack())
            sandboxUndoStack.undo()

        destBase = self.baseFromLocation(phg, scenePos)
        if destBase==None:
            vh, strandType, idx = self.base1
            if didEnd:
                vh.setFloatingXover(None)
            else:
                vh.setFloatingXover(strandType, idx, scenePos)
        else:
            vh1, strand1, idx1 = self.base1
            vh2, strand2, idx2 = destBase
            vh1.setFloatingXover(None)
            vh1.installXoverFrom3To5(strand1, idx1, vh2, idx2)
        
        if didEnd:
            self.base1 = None
