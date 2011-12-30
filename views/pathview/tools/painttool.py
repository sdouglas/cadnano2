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
import sys
from abstractpathtool import AbstractPathTool
import util
util.qtWrapImport('QtCore', globals(), [])
util.qtWrapImport('QtGui', globals(), [])


class PaintTool(AbstractPathTool):
    """
    Handles visibility and color cycling for the paint tool.
    """
    def __init__(self, controller):
        super(PaintTool, self).__init__(controller)
        self._isMacrod = False

    def __repr__(self):
        return "paintTool"  # first letter should be lowercase

    def setActive(self, willBeActive):
        """Show the ColorPicker widget when active, hide when inactive."""
        if willBeActive:
            self._window.pathColorPanel.show()
        else:
            self._window.pathColorPanel.hide()
            self._window.pathColorPanel.prevColor()

    def widgetClicked(self):
        """Cycle through colors on 'p' keypress"""
        self._window.pathColorPanel.nextColor()
        
    def customMouseRelease(self, event):
        if self._isMacrod:
            self._isMacrod = False
            self._window.undoStack().endMacro()
    # end def
    
    def isMacrod(self):
        return self._isMacrod
    # end def
    
    def setMacrod(self):
        self._isMacrod = True
        self._window.undoStack().beginMacro("Group Paint")
        self._window.pathGraphicsView.addToPressList(self)
    # end def
