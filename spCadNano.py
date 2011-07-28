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

gCadNanoObjectName = "CadNanoWindow"
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
        gCadNanoDock = QDockWidget("CadNano")
        gCadNanoDock.setFeatures(
                                QDockWidget.DockWidgetMovable
                                | QDockWidget.DockWidgetFloatable)
        gCadNanoDock.setAllowedAreas(
                                Qt.LeftDockWidgetArea
                                | Qt.RightDockWidgetArea)
        gCadNanoDock.setWidget(dw)
        mayaWin.addDockWidget(Qt.DockWidgetArea(Qt.LeftDockWidgetArea),
                                gCadNanoDock)
        dw.setSizePolicy(QSizePolicy.MinimumExpanding,
                            QSizePolicy.MinimumExpanding)
    gCadNanoDock.setVisible(True)


def simplifyMayaUI():
    mayaHotKeys.disableAllHotKeys()
    mayaUI.simplifyUI()

    myWindow = cmds.window()
    myForm = cmds.formLayout(parent=myWindow)
    global gCadNanoToolbar
    gCadNanoToolbar = cmds.toolBar(
                                "caDNAnoBox",
                                area='top',
                                allowedArea='top',
                                content=myWindow)

    global gIconPath
    closeCadNanoCmd = 'import maya.cmds;maya.cmds.closeCadNano()'
    myButton = cmds.iconTextButton(
                               label='Quit caDNAno',
                               annotation='Quit caDNAno interface',
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
                         label='caDNAno',
                         annotation='Launch caDNAno interface',
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
    if(gCadNanoDock):
        return gCadNanoDock.widget()
    else:
        import views.documentwindow
        for a in qApp.topLevelWidgets():
            if (isinstance(a, views.documentwindow.DocumentWindow)):
                return a
    return None
