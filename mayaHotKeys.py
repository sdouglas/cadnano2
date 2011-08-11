###############################################################################
#
# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###############################################################################


import maya.cmds as cmds
import string

commandWhiteList = [
                "NameComPop_hotBox",
                "TranslateToolWithSnapMarkingMenuNameCommand",
                "RotateToolWithSnapMarkingMenuNameCommand",
                "ScaleToolWithSnapMarkingMenuNameCommand",
                "NameComUndo",
                "NameComRedo"]
disabledHotKeys = []


class HotKey():
    key = ""
    alt = ""
    ctl = ""
    cmd = ""
    name = ""
    rname = ""

    def __init__(self, key, name, rname, alt=False, ctl=False, cmd=False):
        self.key = key
        self.name = name
        self.rname = rname
        self.alt = alt
        self.ctl = ctl
        self.cmd = cmd


def saveHotKey(key):
    global disabledHotKeys
    for alt in range(0, 2):
        for ctl in range(0, 2):
            for cmd in range(0, 2):
                name = cmds.hotkey(
                                key, q=True, n=True,
                                alt=alt, ctl=ctl, cmd=cmd)
                rname = cmds.hotkey(
                                key, q=True, rn=True,
                                alt=alt, ctl=ctl, cmd=cmd)
                if(name != None or rname != None):
                    if name == None:
                        name = ""
                    if rname == None:
                        rname = ""
                    disabledHotKeys.append(
                                HotKey(key, name, rname, alt, ctl, cmd))


def disableHotKey(key):
    saveHotKey(key)
    for alt in range(0, 2):
        for ctl in range(0, 2):
            for cmd in range(0, 2):
                name = cmds.hotkey(
                                key, q=True, n=True,
                                alt=alt, ctl=ctl, cmd=cmd)
                rname = cmds.hotkey(
                                key, q=True, rn=True,
                                alt=alt, ctl=ctl, cmd=cmd)
                if(commandWhiteList.count(name) == 0):
                    cmds.hotkey(
                            k=key, n="", rn="",
                            alt=alt, ctl=ctl, cmd=cmd)


def disableAllHotKeys():
    newChars = string.printable
    for char in newChars:
        disableHotKey(char)

    otherHotKeys = [
                "Up", "Down", "Right", "Left",
                "Home", "End",
                "Page_Up", "Page_Down",
                "Insert", "Return"]
                #"Space" is alread covered in string.printable
    for key in otherHotKeys:
        disableHotKey(key)

    for key in range(1, 13):
        disableHotKey("F" + str(key))


def restoreAllHotKeys():
    global disabledHotKeys
    for hotkey in disabledHotKeys:
        cmds.hotkey(
                k=hotkey.key,
                n=hotkey.name,
                rn=hotkey.rname,
                alt=hotkey.alt,
                ctl=hotkey.ctl,
                cmd=hotkey.cmd)
    disabledHotKeys = []
