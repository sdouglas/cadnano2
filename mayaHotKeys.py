import maya.cmds as cmds
import string

commandWhiteList = ["NameComPop_hotBox",
                    "TranslateToolWithSnapMarkingMenuNameCommand",
                    "RotateToolWithSnapMarkingMenuNameCommand",
                    "ScaleToolWithSnapMarkingMenuNameCommand",
                    "NameComUndo",
                    "NameComRedo"
                    ]
disabledHotKeys = []

class HotKey():
    key = ""
    alt = ""
    ctl = ""
    cmd = ""
    name = ""
    rname = ""
    
    def __init__(self, key, name, rname, alt = False, ctl = False, cmd = False):
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
                name = cmds.hotkey( key, q = True, n = True, alt=alt, ctl=ctl, cmd=cmd )
                rname = cmds.hotkey( key, q = True, rn = True, alt=alt, ctl=ctl, cmd=cmd )
                if( name != None or rname != None) :
                    if name == None:
                        name = ""
                    if rname == None:
                        rname = ""
                    #print "saving hotkey " + key + " name = " + name + " rname = " + rname + " alt=" + str(alt) + " ctl=" + str(ctl) + " cmd=" + str(cmd)
                    disabledHotKeys.append( HotKey(key, name, rname, alt, ctl, cmd) )

def disableHotKey(key):
    saveHotKey(key)
    for alt in range(0, 2):
        for ctl in range(0, 2):
            for cmd in range(0, 2):
                name = cmds.hotkey( key, q = True, n = True, alt=alt, ctl=ctl, cmd=cmd )
                rname = cmds.hotkey( key, q = True, rn = True, alt=alt, ctl=ctl, cmd=cmd )
                if( commandWhiteList.count(name) == 0 ) :
                    cmds.hotkey( k = key, n = "", rn = "", alt=alt, ctl=ctl, cmd=cmd )

def disableAllHotKeys():
    newChars = string.printable
    for char in newChars:
        disableHotKey(char);

    otherHotKeys = ["Up", "Down", "Right", "Left", "Home", "End", "Page_Up", "Page_Down", "Insert", "Return"] #"Space" is alread covered in string.printable
    for key in otherHotKeys:
        disableHotKey(key)

    for key in range(1, 13):
        disableHotKey("F" + str(key))

def restoreAllHotKeys():
    global disabledHotKeys
    for hotkey in disabledHotKeys:
        #print "restoring hotkey " + hotkey.key + " name = " + hotkey.name + " rname = " + hotkey.rname + " alt=" + str(hotkey.alt) + " ctl=" + str(hotkey.ctl) + " cmd=" + str(hotkey.cmd)
        cmds.hotkey( k = hotkey.key, n = hotkey.name, rn = hotkey.rname, alt=hotkey.alt, ctl=hotkey.ctl, cmd=hotkey.cmd )
    disabledHotKeys = []