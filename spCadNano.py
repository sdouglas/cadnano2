import os, sys
import maya
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

#need to find this value or make it relative
gPathToScript = "C:\\git\\cadnano2\\"
lib_path = os.path.abspath( gPathToScript )
sys.path.insert(0, lib_path)

import util
util.qtWrapImport('QtGui', globals(), [ 'qApp' ])

kPluginName = "spCadNano"
gCadNanoButton = None
gCadNanoToolbar = None
fMayaExitingCB = None

# command
class openCadNano(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
	def doIt(self, argList):
		openCN()
	@staticmethod
	def creator():
		return OpenMayaMPx.asMPxPtr( openCadNano() )

class closeCadNano(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
	def doIt(self, argList):
		closeCN()
	@staticmethod
	def creator():
		return OpenMayaMPx.asMPxPtr( closeCadNano() )

def onExitingMaya(clientData):
	closeCN()
	cmds.SavePreferences();

# Initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerCommand( "openCadNano", openCadNano.creator )
		mplugin.registerCommand( "closeCadNano", closeCadNano.creator )
	except:
		sys.stderr.write( "Failed to register command: %s\n" %kPluginName )
		raise
	addUIButton()
	global fMayaExitingCB
	fMayaExitingCB = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kMayaExiting, onExitingMaya)

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	closeCN()
	removeUIButton()

	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand( "openCadNano" )
		mplugin.deregisterCommand( "closeCadNano" )
	except:
		sys.stderr.write( "Failed to unregister command: %s\n" %kPluginName )
		raise
	
	global fMayaExitingCB
	if (fMayaExitingCB != None):
		OpenMaya.MSceneMessage.removeCallback(fMayaExitingCB)

def openCN():
	simplifyMayaUI();
	dw = getDocumentWindow()
	
	if (dw):
		dw.setVisible(True)
	else :
		execfile( gPathToScript + 'mayamain.py')

def simplifyMayaUI():
	cmds.HideUIElements()
	mel.eval("setMainMenubarVisible 0;")
	
	myWindow = cmds.window()
	myForm = cmds.formLayout( parent = myWindow )
	global gCadNanoToolbar
	global gPathToScript;
	gCadNanoToolbar = cmds.toolBar( area = 'top', allowedArea = 'top', content = myWindow )

	myButton = cmds.iconTextButton(	label = 'Quit CadNano',
									image1 = gPathToScript + 'ui/mainwindow/images/cadnano2-app-icon_shelf.png',
									parent = myForm,
									command = 'import maya.cmds; maya.cmds.closeCadNano()' )
	cmds.formLayout( myForm, edit = True, attachForm = [( myButton, 'right', 10 )] )

def restoreMayaUI() :
	cmds.RestoreUIElements();
	mel.eval("setMainMenubarVisible 1;")
	if cmds.toolBar( gCadNanoToolbar, exists=True ):
		cmds.deleteUI(gCadNanoToolbar)

def closeCN():
	dw = getDocumentWindow()
	restoreMayaUI()
	if (dw) :
		dw.setVisible(False)

def addUIButton():
	global gCadNanoButton;
	global gPathToScript;
	cmds.setParent('MayaWindow|toolBar1|MainStatusLineLayout|formLayout5|formLayout8')
	gCadNanoButton = cmds.iconTextButton( 	label = 'caDNAno',
							annotation = 'Launch caDNAno interface',
							image1 = gPathToScript + 'ui/mainwindow/images/cadnano2-app-icon_shelf.png',
							parent = 'MayaWindow|toolBar1|MainStatusLineLayout|formLayout5|formLayout8',
							command = 'import maya.cmds; maya.cmds.openCadNano()' )
	cmds.formLayout(	'MayaWindow|toolBar1|MainStatusLineLayout|formLayout5|formLayout8',
						edit = True,
						attachForm = [(gCadNanoButton, 'right', 10)] )

def removeUIButton():
	global gCadNanoButton;
	cmds.deleteUI(gCadNanoButton)

def getDocumentWindow():
	import views.documentwindow
	for a in qApp.topLevelWidgets():
		if (isinstance(a, views.documentwindow.DocumentWindow)):
			return a
	return None
