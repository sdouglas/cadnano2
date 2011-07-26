import maya.cmds as cmds
import maya.mel as mel

hiddenElements = []
elementsToHide = ["toolBar", "dockControl"]

mainMenuBarVisible = None

def simplifyUI():
    global hiddenElements
    global elementsToHide
    for i in cmds.lsUI( ctl = True):
        for e in elementsToHide:
            if i.find(e) != -1 and cmds.control( i, q=True, visible=True):
                hiddenElements.append(i)
                #print "hiding... " + i
                cmds.control( i, e=True, visible=False)
                break

    global mainMenuBarVisible
    mainMenuBarVisible = cmds.optionVar( q = "mainWindowMenubarVis")
    mel.eval("setMainMenubarVisible 0;")
    #mel.eval("toggleModelEditorBarsInAllPanels 0;")

def restoreUI() :
    global hiddenElements
    for e in hiddenElements:
        #print "restoring... " + e
        cmds.control( e, e=True, visible=True)
    hiddenElements = []
    
    global mainMenuBarVisible
    mel.eval("setMainMenubarVisible " + str(mainMenuBarVisible) + ";")
    #mel.eval("toggleModelEditorBarsInAllPanels 1;")