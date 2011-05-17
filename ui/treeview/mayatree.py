import maya.cmds as cmds
from maya import cmds

window = cmds.window()
layout = cmds.formLayout()
control = cmds.treeView( parent = layout, numberOfButtons = 3, abr = False )
def cool(itemstring, state):
    cmds.treeView( control, e=True,buttonStyle=(itemstring,1,'2StateButton'))
    if state == '1':
        mode = 'buttonDown'
    else:
        mode = 'buttonUp'      
    cmds.treeView( control, e=True,buttonState=(itemstring,1,mode))
    print "%s on %s" % (mode, itemstring)
def great(itemstring,state):
    cmds.treeView( control, e=True,selectItem=(itemstring,state))
    print "great, selected %s" %itemstring
cmds.treeView( control, e=True, pressCommand=(1, cool))
cmds.treeView( control, e=True, selectCommand=great)
cmds.formLayout(layout,e=True, attachForm=(control,'top', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'left', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'bottom', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'right', 2))
cmds.showWindow( window )
cmds.treeView( control, e=True, addItem = ("layer 1", ""))
cmds.treeView( control, e=True, addItem = ("layer 2", ""))
cmds.treeView( control, e=True, addItem = ("layer 3", ""))
cmds.treeView( control, e=True, addItem = ("layer 4", ""))
cmds.treeView( control, e=True, addItem = ("layer 5", ""))
cmds.treeView( control, e=True, addItem = ("layer 6", ""))
cmds.treeView( control, e=True, addItem = ("layer 7", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 8", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 9", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 10", "layer 8"))
cmds.treeView( control, e=True, addItem = ("layer 11", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 12", ""))
cmds.treeView( control, e=True, addItem = ("layer 13", "layer 10"))