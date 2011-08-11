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

import os
import sys
import maya
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
import sip

sys.path.insert(0, os.environ['CADNANO_PATH'])

import mayaHotKeys
import mayaUI
import util

util.qtWrapImport('QtGui', globals(), ['qApp', 'QDockWidget', 'QSizePolicy'])
util.qtWrapImport('QtCore', globals(), ['Qt', 'QObject'])

kPluginName = "spCadNano"
gCadNanoButton = None
gCadNanoToolbar = None
fMayaExitingCB = None
gCadNanoApp = None
gCadNanoObjectName = "CADnanoWindow"
gCadNanoDock = None
gIconPath = (
        os.environ['CADNANO_PATH'] +
        "/ui/mainwindow/images/cadnano2-app-icon_shelf.png")


# command
class openCadNano(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, argList):
        openCN()

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(openCadNano())

class closeCadNano(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, argList):
        closeCN()

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(closeCadNano())

def onExitingMaya(clientData):
    closeCN()
    cmds.SavePreferences()

def onHideEvent():
    closeCN()

# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand("openCadNano", openCadNano.creator)
        mplugin.registerCommand("closeCadNano", closeCadNano.creator)
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginName)
        raise
    addUIButton()
    global fMayaExitingCB
    fMayaExitingCB = OpenMaya.MSceneMessage.addCallback(
                                OpenMaya.MSceneMessage.kMayaExiting,
                                onExitingMaya)


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    closeCN()
    removeUIButton()
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand("openCadNano")
        mplugin.deregisterCommand("closeCadNano")
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginName)
        raise
    global fMayaExitingCB
    if (fMayaExitingCB != None):
        OpenMaya.MSceneMessage.removeCallback(fMayaExitingCB)

def openCN():
    global gCadNanoDock
    global gCadNanoApp
    simplifyMayaUI()

    dw = getDocumentWindow()
    if gCadNanoApp:
        for x in gCadNanoApp.documentControllers:
            if x.win:
                x.win.setVisible(True)
    else:
        # begin program
        from cadnano import app as getAppInstance
        gCadNanoApp = getAppInstance(sys.argv)
        gCadNanoApp.initGui()
        if __name__ == '__main__':
            gCadNanoApp.exec_()
        #execfile( os.environ['CADNANO_PATH'] + '/mayamain.py')
        dw = getDocumentWindow()
        global gCadNanoObjectName
        dw.setObjectName(gCadNanoObjectName)

    if gCadNanoDock == None:
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        mayaWin = sip.wrapinstance(long(ptr), QObject)
        gCadNanoDock = QDockWidget("CADnano")
        gCadNanoDock.setFeatures(
                                QDockWidget.DockWidgetMovable
                                | QDockWidget.DockWidgetFloatable)
        gCadNanoDock.setAllowedAreas(
                                Qt.LeftDockWidgetArea
                                | Qt.RightDockWidgetArea)
        gCadNanoDock.setWidget(dw)
        mayaWin.addDockWidget(Qt.DockWidgetArea(Qt.LeftDockWidgetArea),
                                gCadNanoDock)
        # dw.setSizePolicy(QSizePolicy.MinimumExpanding,
        #                     QSizePolicy.MinimumExpanding)
        gCadNanoDock.changeEvent = changed
        mayaWin.changeEvent = changed
    gCadNanoDock.setVisible(True)

    pluginPath = os.path.join(os.environ['CADNANO_PATH'],  "views", "solidview", "helixManip.py") 
    if not cmds.pluginInfo( pluginPath, query=True, loaded=True ):
            cmds.loadPlugin( pluginPath )        
            cmds.spHelixManipCtxCmd("spHelixContext1")
            cmds.setToolTo("spHelixContext1")

def changed(self, event):
    print str(event.type())
    if (event.type() == QEvent.ActivationChange or
        event.type() == QEvent.WindowActivate or
        event.type() == QEvent.ApplicationActivate):
            print self.win.windowTitle()
            app().activeDocument = self

def simplifyMayaUI():
    mayaHotKeys.disableAllHotKeys()
    mayaUI.simplifyUI()

    myWindow = cmds.window()
    myForm = cmds.formLayout(parent=myWindow)
    global gCadNanoToolbar
    gCadNanoToolbar = cmds.toolBar(
                                "CADnanoBox",
                                area='top',
                                allowedArea='top',
                                content=myWindow)
    global gIconPath
    closeCadNanoCmd = 'import maya.cmds;maya.cmds.closeCadNano()'
    myButton = cmds.iconTextButton(
                               label='Quit CADnano',
                               annotation='Quit CADnano interface',
                               image1=gIconPath,
                               parent=myForm,
                               command=closeCadNanoCmd)
    cmds.formLayout(
                myForm,
                edit=True,
                attachForm=[(myButton, 'right', 10)])

def restoreMayaUI():
    mayaHotKeys.restoreAllHotKeys()
    mayaUI.restoreUI()
    if cmds.toolBar(gCadNanoToolbar, exists=True):
        cmds.deleteUI(gCadNanoToolbar)

def closeCN():
    global gCadNanoDock
    global gCadNanoApp
    gCadNanoDock.setVisible(False)
    for x in gCadNanoApp.documentControllers:
        if x.win:
            x.win.setVisible(False)
    restoreMayaUI()

def addUIButton():
    global gCadNanoButton
    global gIconPath
    mayaMainToolbar = (
            'MayaWindow|toolBar1|MainStatusLineLayout|formLayout5|formLayout8')
    if cmds.formLayout(mayaMainToolbar, ex=True):
        cmds.setParent(mayaMainToolbar)
        gCadNanoButton = cmds.iconTextButton(
                         label='CADnano',
                         annotation='Launch CADnano interface',
                         image1=gIconPath,
                         parent=mayaMainToolbar,
                         command='import maya.cmds; maya.cmds.openCadNano()')
        cmds.formLayout(
                    mayaMainToolbar,
                    edit=True,
                    attachForm=[(gCadNanoButton, 'right', 10)])

def removeUIButton():
    global gCadNanoButton
    cmds.deleteUI(gCadNanoButton)

def getDocumentWindow():
    global gCadNanoDock
    global gCadNanoApp
    if gCadNanoDock:
        return gCadNanoDock.widget()
    elif gCadNanoApp:
        for x in gCadNanoApp.documentControllers:
            if x.win:
                return x.win
    return None
