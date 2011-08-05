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
