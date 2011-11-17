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

from os.path import basename
from model.enum import StrandType

def legacy_dict_from_doc(document, fname, helixOrderList):
    part = document.selectedPart()
    numBases = part.maxBaseIdx()+1

    # iterate through virtualhelix list
    vhList = []
    for row, col in helixOrderList:
        vh = part.virtualHelixAtCoord((row, col))
        # insertions and skips
        insertionDict = part.insertions()[(row, col)]
        insts = [0 for i in range(numBases)]
        skips = [0 for i in range(numBases)]
        for idx, insertion in insertionDict.iteritems():
            if insertion.isSkip():
                skips[idx] = insertion.length()
            else:
                insts[idx] = insertion.length()
        # colors
        stapColors = []
        stapStrandSet = vh.stapleStrandSet()
        for strand in stapStrandSet:
            if strand.connection5p() == None:
                c = str(strand.oligo().color())[1:]  # drop the hash
                stapColors.append([strand.idx5Prime(), int(c, 16)])

        vhDict = {"row":row,
                  "col":col,
                  "num":vh.number(),
                  "scaf":vh.getLegacyStrandSetArray(StrandType.Scaffold),
                  "stap":vh.getLegacyStrandSetArray(StrandType.Staple),
                  "loop":insts,
                  "skip":skips,
                  "scafLoop":[],
                  "stapLoop":[],
                  "stap_colors":stapColors}
        vhList.append(vhDict)
    bname = basename(str(fname))
    obj = {"name":bname , "vstrands":vhList}
    return obj