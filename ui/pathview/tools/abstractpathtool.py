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
crossoverhandle.py
Created by Shawn on 2011-05-03.
"""
import ui.styles as styles


class AbstractPathTool(object):
    """
    Abstract base class to be subclassed by all other pathview tools.

    AbstractPathTool is an abstract class for tools that can handle events
    forwarded in the style of util.defineEventForwardingMethodsForClass.
    
    In other words, the activeTool() gets events from various graphics objects
    in the pathview and then makes the corresponding changes to the model.
    
    The displayed content then updates automatically via notifications from
    the model.
    * the activeTool gets events from graphics items and does the work
      (changes the model). Possible future configuration of the activeTool()
      can be done on the instances of various tools kept in the controller,
      like selectTool.
    * graphics items that make up the view sit back and watch the model,
      updating when it changes
    """

    _baseWidth = styles.PATH_BASE_WIDTH

    def __init__(self):
        self._active = False
    # end def

    def setActive(self, bool):
        """
        Called by PathController.setActiveTool when the tool becomes
        active. Used, for example, to show/hide tool-specific ui elements.
        """
        pass
    # end def

    def isActive(self):
        """Returns isActive"""
        return self._active
    # end def

    def mousePointToBaseIndex(self, point):
        x = int(point.x() / self._baseWidth)
        y = int(point.y() / self._baseWidth)
        return (x, y)
    # end def
# end class
