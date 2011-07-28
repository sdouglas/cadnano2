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

import maya.cmds as cmds
import maya.mel as mel

hiddenElements = []
elementsToHide = ["toolBar", "dockControl"]

mainMenuBarVisible = None


def simplifyUI():
    global hiddenElements
    global elementsToHide
    for i in cmds.lsUI(ctl=True):
        for e in elementsToHide:
            if i.find(e) != -1 and cmds.control(i, q=True, visible=True):
                hiddenElements.append(i)
                #print "hiding... " + i
                cmds.control(i, e=True, visible=False)
                break

    global mainMenuBarVisible
    mainMenuBarVisible = cmds.optionVar(q="mainWindowMenubarVis")
    mel.eval("setMainMenubarVisible 0;")
    #mel.eval("toggleModelEditorBarsInAllPanels 0;")


def restoreUI():
    global hiddenElements
    for e in hiddenElements:
        #print "restoring... " + e
        cmds.control(e, e=True, visible=True)
    hiddenElements = []

    global mainMenuBarVisible
    mel.eval("setMainMenubarVisible " + str(mainMenuBarVisible) + ";")
    #mel.eval("toggleModelEditorBarsInAllPanels 1;")
