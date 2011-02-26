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

"""
cadnanomaya
Created by Nick Conway on 2011-02-03.
modified from cadnano.py
"""
from PyQt4 import QtCore
from PyQt4 import QtGui
import pymel.core as pc


class caDNAno(QtCore.QObject):
    sharedApp = None  # This class is a singleton.
    def __init__(self):
        super(caDNAno, self).__init__()
        assert(not caDNAno.sharedApp)
        self.configMaya()
        caDNAno.sharedApp = self
        self.app = QtGui.qApp
        #self.setWindowIcon(QIcon('ui/images/cadnano2-app-icon.png'))
        self.undoGroup = QtGui.QUndoGroup()
        #self.setApplicationName(QString("caDNAno"))
        self.documentControllers = set() # Open documents
        self.newDocument()
        

    def newDocument(self):
        from ui.mayacontroller import DocumentController 
        DocumentController() # DocumentController is responsible for adding
                             # itself to app.documentControllers
                             
    def configMaya(self):
        
        # delete all objects in the scene
        pc.general.select(all=True)
        selectedObjects = pc.ls(sl=True)
        pc.general.delete(selectedObjects)
        
        pc.language.scriptJob( killAll=True)
        # set up the panel shading
        # mypanel = pc.windows.getPanel(underPointer=True)
        # 
        # if mypanel == None or mypanel.name() == "":
        #     mypanel = pc.windows.getPanel(withFocus=True)  
        # #end if
        # print "setting up panel: %s\n" % mypanel.name()
        # if pc.windows.modelEditor(mypanel.name(), query=True, exists=True):
        #     pc.windows.modelEditor(mypanel.name(), edit=True, displayAppearance='smoothShaded',smoothWireframe=False)
        # end if
        #print pc.windows.paneLayout(paneUnderPointer=True,query=True)
        #[u'modelPanel4', u'modelPanel2', u'modelPanel3', u'modelPanel1']
        # panels = pc.windows.paneLayout('viewPanes',query=True, childArray=True)
        panels = [u'modelPanel4', u'modelPanel2', u'modelPanel3', u'modelPanel1']
        print panels
        for current in panels:
            if current != "":
                # renderName=ogsRenderer is Viewport 2.0
                pc.windows.modelEditor(current, edit=True, \
                                    displayAppearance='smoothShaded', \
                                    wireframeOnShaded=False, \
                                    smoothWireframe=False, \
                                    rendererName=u'ogsRenderer') #rendererName=u'base_OpenGL_Renderer'
                #print pc.windows.modelEditor(current, query=True, rendererList=True)
                print "setting up panel: %s\n" % current
            # end if
        # end for
        # finish setting up panels
        
    # end def

# Convenience. No reason to feel guilty using it - caDNAno is a singleton.
def app():
    return caDNAno.sharedApp