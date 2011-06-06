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
penciltool
Created by Nick Conway on 2011-06-04.
"""

from selecttool import SelectTool


class PencilTool(SelectTool):
    """PencilTool allows for creation of new staple or scaffold strands
    by clicking and dragging on empty bases."""
    def __init__(self, controller):
        super(PencilTool, self).__init__(controller)

    def applyTool(self, vHelix, fr, to):
        """
        """
        fr = vHelix.validatedBase(*fr, raiseOnErr=False)
        to = vHelix.validatedBase(*to, raiseOnErr=False)
        if (None, None) in (fr, to):
            return False
        startOnSegment = vHelix.hasStrandAt(*fr)
        startOnBreakpoint = vHelix.hasEndAt(*fr)
        direction = 1 if to[1] >= fr[1] else -1
        useClearMode = startOnSegment
        if startOnBreakpoint:
            is5to3 = vHelix.directionOfStrandIs5to3(fr[0])
            if is5to3 and startOnBreakpoint==3 or\
               not is5to3 and startOnBreakpoint==5:
                inwardDir = -1
            else:
                inwardDir = 1
            useClearMode = direction == inwardDir
        # adj: the base adjacent to fr in the same direction as to
        if useClearMode:
            if to[1]<fr[1]:
                #print "cl< %s-%s"%(fr[1], to[1])
                vHelix.clearStrand(fr[0], fr[1], to[1]+1)
            elif to[1]>fr[1]:
                if vHelix.hasCrossoverAt(fr[0], fr[1]-1):
                    fr = (fr[0], fr[1]+1)
                #print "cl> %s-%s"%(fr[1], to[1])
                vHelix.clearStrand(fr[0], fr[1], to[1])
            else:
                if not vHelix.hasCrossoverAt(fr[0], fr[1]-1):
                    #print "cl= %s-%s"%(fr[1], to[1])
                    vHelix.clearStrand(fr[0], fr[1], to[1])
        else:
            vHelix.connectStrand(fr[0], fr[1], to[1])
