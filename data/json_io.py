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
"""

import json



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

def save(my_assembly,filename):
    """
    save a json file, decides between current filetype
    
    Parameters
    ----------
    my_assembly: assembly to save
    filename: filename of json file

    See Also
    --------

    Examples
    -------- 
    """
    pass
#end def

def load(filename, mymodel):
    """
    load a json file, decides between current filetype and legacy caDNAno 1.0 filetype
    
    Parameters
    ----------
    filename: filename of json file

    See Also
    --------

    Examples
    -------- 
    """
    with open(filename,'r') as myfile:
        objects = json.load(myfile)
    try:
        if objects['fileType'] == 'caDNAno2.0':
            return parse_current(objects,mymodel) 
    except:
        return parse_legacy(objects,mymodel)
#end def

def parse_legacy(obj,mymodel):
    """
    take a loaded legacy dictionary, decides between current filetype and legacy caDNAno 1.0 filetype
    
    Parameters
    ----------
    obj: dictionary object generated from a JSON file 

    See Also
    --------

    Examples
    -------- 
    """
    from assembly import Assembly
    from part import Part
    
    my_assembly = Assembly()
    
    my_part = Part(my_assembly.createPartID())
    
    
    vhelixlist = obj["vstrands"] # should rename to 
    name = obj["name"] # placeholder, not really used
    
    # create dictionaries (keyed by vstrand #) of
    # row/col, scaf array, stap array
    vhToRowCol = {}
    vhToScaf = {}
    vhToStap = {}
    vhNums = []
    
    for helix in vhelixlist: # strand should be helix
        num = helix["num"] # helix number
        vhNums.append(num) # keep track of a list of helix numbers
        row = helix["row"] # slice row for this helix
        col = helix["col"] # slice column
        scaf = helix["scaf"] # array of scaffold points
        stap = helix["stap"] # array of staple pointers
        vhToRowCol[num] = [row,col]
        vhToScaf[num] = scaf
        vhToStap[num] = stap
    
    # extract scaffold 5' breakpoints
    scafBreaks = []
    for vh in vhNums:
        scaf = vhToScaf[vh]
        for i in range(len(scaf)):
            base = scaf[i]
            if (base[1] == -1) & (base[3] != -1):
                scafBreaks.append([vh, i])
    
    # extract staple 5' breakpoints
    stapBreaks = []
    for vh in vhNums:
        stap = vhToStap[vh]
        for i in range(len(stap)):
            base = stap[i]
            if (base[1] == -1) & (base[3] != -1):
                stapBreaks.append([vh, i])
    
    
    # extract scaffold paths, starting at 5' breakpoints
    scafPaths = []
    for scafBreak in scafBreaks:
        path = []
        [curr_vh, curr_base] = scafBreak
        [next_vh, next_base] = vhToScaf[curr_vh][curr_base][2:4]
        while next_base != -1:
            [row, col] = vsToRowCol[curr_vs]
            [x, y, z] = getScafCoord(row,col,curr_base)
            path.append([curr_vs,curr_base,[x, y, z]])
            # append midpoint for crossover
            if (curr_vs != next_vs) & (curr_base == next_base):
                (x1,y1,z1) = getScafCoord(row,col,curr_base)
                [nextrow, nextcol] = vsToRowCol[next_vs]
                (x2,y2,z2) = getScafCoord(nextrow,nextcol,next_base)
                midxyz = [(x1+x2)/2,(y1+y2)/2,(z1+z2)/2]
                path.append([curr_vs,curr_base,midxyz])
            [curr_vs, curr_base] = [next_vs, next_base]
            [next_vs, next_base] = vsToScaf[curr_vs][curr_base][2:4]
        [row, col] = vsToRowCol[curr_vs]
        [x, y, z] = getScafCoord(row,col,curr_base)
        path.append([curr_vs,curr_base,[x, y, z]])
        scafPaths.append(path)
    
    
    # extract staple paths, starting at 5' breakpoints
    stapPaths = []
    for stapBreak in stapBreaks:
        path = []
        [curr_vs, curr_base] = stapBreak
        [next_vs, next_base] = vsToStap[curr_vs][curr_base][2:4]
        while next_base != -1:
            [row, col] = vsToRowCol[curr_vs]
            [x, y, z] = getStapCoord(row,col,curr_base)
            path.append([curr_vs,curr_base, [x, y, z]])
            # append midpoint for crossover
            if (curr_vs != next_vs) & (curr_base == next_base):
                (x1,y1,z1) = getStapCoord(row,col,curr_base)
                [nextrow, nextcol] = vsToRowCol[next_vs]
                (x2,y2,z2) = getStapCoord(nextrow,nextcol,next_base)
                midxyz = [(x1+x2)/2,(y1+y2)/2,(z1+z2)/2]
                path.append([curr_vs,curr_base,midxyz])
            [curr_vs, curr_base] = [next_vs, next_base]
            [next_vs, next_base] = vsToStap[curr_vs][curr_base][2:4]
        [row, col] = vsToRowCol[curr_vs]
        [x, y, z] = getStapCoord(row,col,curr_base)
        path.append([curr_vs,curr_base, [x, y, z]])
        stapPaths.append(path)
    
    my_part.VHelix = vhelixlist
    my_assembly.addPart(my_part)
    return my_parts, my_assembly
# end def
