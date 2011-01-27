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
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from PyQt4.QtCore import QRectF, QPointF, QObject, QEvent
from PyQt4.QtCore import QObject, pyqtSlot
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QGraphicsItem, QGraphicsObject

# import pathhelix
import styles

class PathHelixGroup(QGraphicsObject):
    """docstring for PathHelixGroup"""
    def __init__(self, type="honeycomb", controller=None, parent=None):
        super(PathHelixGroup, self).__init__()
        self.pathController = controller

        if type == "honeycomb":
            # set honeycomb parameters
            pass
        else:
            # set square parameters
            pass
        
    def paint(self, painter, option, widget=None):
        pass

    def boundingRect(self):
        return self.rect


    