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
documentwindow.py
"""

import ui.mainwindow.ui_mainwindow as ui_mainwindow
import controllers.pathcontroller as pathcontroller
import controllers.slicecontroller as slicecontroller
from cadnano import app
from views.pathview.colorpanel import ColorPanel
from tests.testrecorder import TestRecorder

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['pyqtSignal', 'Qt', 'QFileInfo', \
                                        'QPoint', 'QSettings', 'QSize', \
                                        'QString'])
util.qtWrapImport('QtGui', globals(), [ 'QGraphicsItem', 'QMainWindow', \
                                        'QGraphicsScene', 'QGraphicsView', \
                                        'QApplication', 'QAction', 'QWidget'])
util.qtWrapImport('QtOpenGL', globals(), [ 'QGLWidget', 'QGLFormat', 'QGL'])

class SceneRoot(QGraphicsItem):
    def __init__(self, rectsource=None):
        super(SceneRoot, self).__init__()
        # this sets the rect of itself to the QGraphicsScene bounding volume
        self.rect = rectsource.sceneRect()

    def paint(self, painter, option, widget):
        pass

    def boundingRect(self):
        return self.rect


class DocumentWindow(QMainWindow, ui_mainwindow.Ui_MainWindow):
    """docstring for DocumentWindow"""
    def __init__(self, parent=None, docCtrlr=None):
        super(DocumentWindow, self).__init__(parent)
        self.controller = docCtrlr
        self.setupUi(self)
        self.settings = QSettings()
        self.readSettings()
        # Slice setup
        self.slicescene = QGraphicsScene(parent=self.sliceGraphicsView)
        self.sliceroot = SceneRoot(rectsource=self.slicescene)
        self.slicescene.addItem(self.sliceroot)
        assert self.sliceroot.scene() == self.slicescene
        self.sliceGraphicsView.setScene(self.slicescene)
        self.sliceGraphicsView.sceneRootItem = self.sliceroot
        self.sliceController = slicecontroller.SliceController(self)
        # Path setup
        self.pathscene = QGraphicsScene(parent=self.pathGraphicsView)
        self.pathroot = SceneRoot(rectsource=self.pathscene)
        self.pathscene.addItem(self.pathroot)
        assert self.pathroot.scene() == self.pathscene

        # Uncomment the following block for  explicit pathview GL rendering
        # self.pathGraphicsView.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        # self.pathGraphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # self.pathGraphicsView.setAutoFillBackground ( True )
        # self.pathscene.setBackgroundBrush(Qt.white)
        # self.pathscene.setItemIndexMethod(QGraphicsScene.NoIndex)

        self.pathGraphicsView.setScene(self.pathscene)
        self.pathGraphicsView.sceneRootItem = self.pathroot
        self.pathGraphicsView.setScaleFitFactor(0.9)

        self.pathToolbar = ColorPanel()
        self.pathGraphicsView.toolbar = self.pathToolbar
        self.pathscene.addItem(self.pathToolbar)
        self.pathController = pathcontroller.PathController(self)
        self.sliceController.pathController = self.pathController
        self.pathController.sliceController = self.sliceController

        # Test recording
        if app().testRecordMode:
            rec = TestRecorder()
            self.sliceController.testRecorder = rec
            self.pathController.testRecorder = rec
            self.pathController.activeToolChanged.connect(rec.activePathToolChangedSlot)

        # Edit menu setup
        self.actionUndo = docCtrlr.undoStack().createUndoAction(self)
        self.actionRedo = docCtrlr.undoStack().createRedoAction(self)
        self.actionUndo.setText(QApplication.translate("MainWindow", "Undo", None, QApplication.UnicodeUTF8))
        self.actionUndo.setShortcut(QApplication.translate("MainWindow", "Ctrl+Z", None, QApplication.UnicodeUTF8))
        self.actionRedo.setText(QApplication.translate("MainWindow", "Redo", None, QApplication.UnicodeUTF8))
        self.actionRedo.setShortcut(QApplication.translate("MainWindow", "Ctrl+Shift+Z", None, QApplication.UnicodeUTF8))
        self.sep = QAction(self)
        self.sep.setSeparator(True)
        self.menuEdit.insertAction(self.actionCut, self.sep)
        self.menuEdit.insertAction(self.sep, self.actionRedo)
        self.menuEdit.insertAction(self.actionRedo, self.actionUndo)
        self.splitter.setSizes([400,400])  # balance splitter size

    def undoStack(self):
        return self.controller.undoStack()

    def focusInEvent(self):
        app().undoGroup.setActiveStack(self.controller.undoStack())

    def readSettings(self):
        self.settings.beginGroup("MainWindow");
        self.resize(self.settings.value("size", QSize(1100, 800)).toSize())
        self.move(self.settings.value("pos", QPoint(200, 200)).toPoint())
        self.settings.endGroup()

    def moveEvent(self, event):
        """Reimplemented to save state on move."""
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("pos", self.pos())
        self.settings.endGroup()

    def resizeEvent(self, event):
        """Reimplemented to save state on resize."""
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", self.size())
        self.settings.endGroup()
        QWidget.resizeEvent(self, event)
