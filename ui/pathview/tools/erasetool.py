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
erasetool.py

Created by Nick on 2011-05-18
"""

from exceptions import AttributeError, NotImplementedError
from PyQt4.QtCore import QPointF, QRectF, Qt
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QPen
import ui.styles as styles
from abstractpathtool import AbstractPathTool


class EraseTool(AbstractPathTool):
    _pen = QPen(styles.redstroke, 2)
    _pen.setCapStyle(Qt.RoundCap)
    _pen.setJoinStyle(Qt.RoundJoin)
    _brush = QBrush(styles.erasefill)

    def __init__(self, controller, parent=None):
        """
        This class inherits from the PathTool class for the majority of
        methods/behaviours.  Essentially it adds merely decorator graphics
        custimazation of behaviour and data structure access particular to
        loop insertion on a mouseclick.

        Its parent should be *always* be a PathHelix.
        """
        super(EraseTool, self).__init__(controller, parent)
        self.hide()
        self.setZValue(styles.ZPATHTOOL)

    def mousePressPathHelix(self, pathHelix, event):
        posScene = event.scenePos()
        posItem = self.parentItem().mapFromScene(posScene)
        strandType, idx = self.baseAtPoint(pathHelix, posItem)
        vh = self.parentItem().vhelix()
        rightBreakIdx = leftBreakIdx = idx
        while leftBreakIdx>1:
            if vh.hasCrossoverAt(strandType, leftBreakIdx-1):
                break
            if vh.hasEndAt(strandType, leftBreakIdx-1):
                break
            leftBreakIdx -= 1
        while rightBreakIdx<vh.numBases():
            if vh.hasCrossoverAt(strandType, rightBreakIdx+1):
                break
            if vh.hasEndAt(strandType, rightBreakIdx) and\
               rightBreakIdx != idx:
                break
            rightBreakIdx += 1
        vh.clearStrand(strandType, leftBreakIdx, rightBreakIdx)