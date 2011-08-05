 #*******************************************************************
 # (C) Copyright 2010 by Autodesk, Inc. All Rights Reserved. By using
 # this code,  you  are  agreeing  to the terms and conditions of the
 # License  Agreement  included  in  the documentation for this code.
 # AUTODESK  MAKES  NO  WARRANTIES,  EXPRESS  OR  IMPLIED,  AS TO THE
 # CORRECTNESS OF THIS CODE OR ANY DERIVATIVE WORKS WHICH INCORPORATE
 # IT.  AUTODESK PROVIDES THE CODE ON AN 'AS-IS' BASIS AND EXPLICITLY
 # DISCLAIMS  ANY  LIABILITY,  INCLUDING CONSEQUENTIAL AND INCIDENTAL
 # DAMAGES  FOR ERRORS, OMISSIONS, AND  OTHER  PROBLEMS IN THE  CODE.
 #
 # Use, duplication,  or disclosure by the U.S. Government is subject
 # to  restrictions  set forth  in FAR 52.227-19 (Commercial Computer
 # Software Restricted Rights) as well as DFAR 252.227-7013(c)(1)(ii)
 # (Rights  in Technical Data and Computer Software),  as applicable.
 #*******************************************************************


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
