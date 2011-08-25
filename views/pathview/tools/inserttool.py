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
inserttool.py
Created by Nick on 2011-05-03.
"""
from exceptions import AttributeError, NotImplementedError
from model.enum import HandleOrient, StrandType
from views import styles
# from views.pathview.pathhelix import PathHelix
from views.pathview.pathhelixgraphicsitem import PathHelix
from abstractpathtool import AbstractPathTool
from views.pathview.handles import loopgraphicsitem
from controllers.insertiontooloperation import InsertionToolOperation
import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QPointF', 'QRectF', 'Qt'])
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QBrush', 'QFont',
                                        'QGraphicsSimpleTextItem', 'QPen',\
                                        'QPainterPath'])

class InsertTool(AbstractPathTool):
    baseWidth = styles.PATH_BASE_WIDTH
    _boundingRect = loopgraphicsitem.loopPathUpBR
    _boundingRect = _boundingRect.united(loopgraphicsitem.loopPathDownBR)
    
    def __init__(self, controller, parent=None):
        """
        This class inherits from the PathTool class for the majority of
        methods/behaviours.  Essentially it adds merely decorator graphics
        custimazation of behaviour and data structure access particular to
        insert addition on a mouseclick.

        Its parent should be *always* be a PathHelix.
        """
        AbstractPathTool.__init__(self, controller, parent)
        self.setZValue(styles.ZPATHTOOL)
        self._vBase = None
        self._loopPath = None
    # end def

    def vBase(self):
        return self._vBase
    def setVBase(self, newVBase, pathHelix):
        oldVBase = self._vBase
        if oldVBase != None and newVBase == None:
            self.hide()
        if newVBase != None:
            if self.parentItem() != pathHelix:
                self.setParentItem(pathHelix)
            self.setPos(pathHelix.pointForVBase(newVBase))
            if pathHelix.vBaseIsTop(newVBase):
                self._loopPath = loopgraphicsitem.loopPathUp
            else:
                self._loopPath = loopgraphicsitem.loopPathDown
            strand = newVBase.strand()
            self._loopPen = strand.color() if strand else styles.scafstroke
            if not self.isVisible():
                self.show()
        self._vBase = newVBase

    def paint(self, painter, option, widget=None):
        if self._vBase == None: return
        painter.setPen(self._pen)  # Red square
        painter.setBrush(self._brush)
        painter.drawRect(self._toolRect)
        painter.setPen(self._loopPen)
        painter.drawPath(self._loopPath)

    def boundingRect(self):
        return self._boundingRect

    def hoverMovePathHelix(self, pathHelix, event):
        self.setVBase(pathHelix.vBaseAtPoint(event.pos()), pathHelix)

    def mousePressPathHelix(self, pathHelix, event):
        vb = pathHelix.vBaseAtPoint(event.pos())
        if vb != None:
            InsertionToolOperation(vb, vb.undoStack())
# end class
