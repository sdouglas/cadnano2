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
looptool.py
Created by Nick on 2011-05-03.
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
from ui.pathview.handles.loophandle import LoopItem
from abstractpathtool import AbstractPathTool

class LoopTool(AbstractPathTool):
    def __init__(self, controller, parent=None):
        """
        This class inherits from the PathTool class for the majority of
        methods/behaviours.  Essentially it adds merely decorator graphics
        custimazation of behaviour and data structure access particular to
        loop insertion on a mouseclick.

        Its parent should be *always* be a PathHelix.
        """
        super(LoopTool, self).__init__(controller, parent)
        self._loopItem = LoopItem()
        _pen = QPen(styles.bluestroke, 2)
        self.baseWidth = styles.PATH_BASE_WIDTH
        self.hide()
        self.setZValue(styles.ZPATHTOOL)
        self._isTop = True
    # end def

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRect(self._toolRect)
        painter.setPen(self._loopItem.getPen())
        painter.drawPath(self._loopItem.getLoop(self._isTop))
    # end def
    
    def hoverMovePathHelix(self, ph, event, flag=None):
        """
        flag is for the case where an item in the path also needs to
        implement the hover method
        """
        posItem = event.pos()
        if flag != None:
            posScene = event.scenePos()
            posItem = self.parentItem().mapFromScene(posScene)
        if self.helixIndex(posItem)[1] == 1:
            self._isTop = False
        else:
            self._isTop = True
        self.setPos(self.helixPos(posItem))
    # end def

    def mousePressPathHelix(self, ph, event):
        vh = ph.vhelix()
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        indexp = self.helixIndex(posItem)
        mouseDownBase = ph.baseAtLocation(posItem.x(),\
                                                posItem.y())
        print "LoopTool clicked at: (%d, %d) on helix %d" % \
            (indexp[0], indexp[1], self.parentItem().number())
        # create a new LoopHandle by adding through the     parentItem
        if mouseDownBase:
            loopsize = vh.hasLoopAt(*mouseDownBase)
            if loopsize < 0:    # toggle from skip
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],1)
            elif loopsize > 0:    # loop already there
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],0)
            elif vh.hasStrandAt(*mouseDownBase):
                vh.installLoop(mouseDownBase[0],mouseDownBase[1],1)
    # end def
# end class
