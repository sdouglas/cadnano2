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
json_io.py

Created by Nick Conway on 2011-01-19.

Houses code that parses legacy (cadnano1) files.l
"""

import json
from document import Document
from dnahoneycombpart import DNAHoneycombPart
from virtualhelix import VirtualHelix
from enum import StrandType
from PyQt4.QtGui import QColor


NODETAG = "node"
NAME = "name"
OBJ_ID = "objectid"
INST_ID = "instanceid"
DONE = "done"
CHECKED = "check"
LOCKED = "locked"

VHELIX = "vhelix"
NUM = "num"
COL = "col"
ROW = "row"
SCAFFOLD = "scaffold"
STAPLE = "staple"
INSERTION = "insertion"
DELETION = "deletion"

def doc_from_legacy_dict(obj):
    """
    take a loaded legacy dictionary, returns a loaded Document
    """
    doc = Document()
    part = DNAHoneycombPart()
    doc.addPart(part)
    part.setName(obj["name"])
    #self.addVirtualHelixAt(coord, vh, requestSpecificIdnum=num, noUndo=True)
    numBases = len(obj['vstrands'][0]['scaf'])
    part.setDimensions((60, 32, numBases))
    for helix in obj['vstrands']:
        row = helix['row']
        col = helix['col']
        scaf= helix['scaf']
        vh = VirtualHelix(numBases=len(scaf), idnum=helix['num'])
        part.addVirtualHelixAt((row,col), vh, requestSpecificIdnum=helix['num'], noUndo=True)
    for helix in obj['vstrands']:
        vh = part.getVirtualHelix(helix['num'])
        scaf = helix['scaf']
        stap = helix['stap']
        loops = helix['loop']
        skips = helix['skip']
        assert(len(scaf)==len(stap) and len(stap)==vh.numBases() and\
               len(scaf)==len(loops) and len(loops)==len(skips))
        for i in range(len(scaf)):
            fiveVH, fiveIdx, threeVH, threeIdx = scaf[i]
            threeVH = part.getVirtualHelix(threeVH)
            # Installing an Xover works on the same strand
            # as well (there is nothing inherently different
            # between an Xover and a same-strand linkage
            # in our current model)
            if threeVH==-1 or threeIdx==-1:
                continue
            vh.installXoverFrom3To5(StrandType.Scaffold, i, threeVH, threeIdx, undoStack=False)
        for i in range(len(stap)):
            fiveVH, fiveIdx, threeVH, threeIdx = stap[i]
            threeVH = part.getVirtualHelix(threeVH)
            if threeVH==-1 or threeIdx==-1:
                continue
            vh.installXoverFrom3To5(StrandType.Staple, i, threeVH, threeIdx, undoStack=False)
        for baseIdx, colorNumber in helix['stap_colors']:
            color = QColor((colorNumber>>16)&0xFF, (colorNumber>>8)&0xFF, colorNumber&0xFF)
            vh.applyColorAt(color, StrandType.Staple, baseIdx, undoStack=False)
        for i in range(len(stap)):
            combinedLoopSkipAmount = loops[i] + skips[i]
            if combinedLoopSkipAmount != 0:
                vh.installLoop(StrandType.Scaffold, i, combinedLoopSkipAmount, undoStack=False)
    return doc
