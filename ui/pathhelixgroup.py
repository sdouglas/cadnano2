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
pathhelixgroup.py

Created by Shawn on 2011-01-27.
"""

from PyQt4.QtCore import QRectF, QPointF, QEvent, pyqtSlot, QObject
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem#, QGraphicsObject
from .pathhelix import PathHelix
import styles

class PhgObject(QObject):
    """ A placeholder class until QGraphicsObject is available to allow signaling """
    scaffoldChange = pyqtSignal(int)
    def __init__(self):
        super(PhgObject, self).__init__()
# end class

class PathHelixGroup(QGraphicsItem):    # change to QGraphicsObject for Qt 4.6
    """docstring for PathHelixGroup"""
    def __init__(self, dnaPartInst, type="honeycomb", controller=None,\
                 scene=None, parent=None):
        super(PathHelixGroup, self).__init__()
        
        self.dnaPartInst = dnaPartInst
        self.pathController = controller
        self.scene = scene
        self.crossSectionType = self.dnaPartInst.part().getCrossSectionType()

        if self.crossSectionType == "honeycomb":
            # set honeycomb parameters
            self.rect = QRectF(0, 0, 200, 200)
            self.pathCanvasWidth = 42 # FIX: set from config file
        else:
            # set square parameters
            pass
            
        # set up signals    
        self.qObject = PhgObject()
        self.scaffoldChange = self.qObject.scaffoldChange
    # end def

    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect

    @pyqtSlot('QPointF',int)
    def handleNewHelix(self, pos, number):
        """
        Retrieve reference to new VirtualHelix vh based on number relayed
        by the signal event. Next, create a new PathHelix associated 
        with vh and draw it on the screen.
        """
        part = self.dnaPartInst.part()
        vh = part.getVirtualHelix(number)
        x = 0
        y = part.getVirtualHelixCount() * 50
        ph = PathHelix(vh, QPointF(x, y), self)
        ph.setParentItem(self)
