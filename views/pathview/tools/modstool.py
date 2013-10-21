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
import sys
from abstractpathtool import AbstractPathTool
from data.sequencemods import mods
from ui.dialogs.ui_mods import Ui_ModsDialog
import util
util.qtWrapImport('QtCore', globals(), ['QSignalMapper', 'QString'])
util.qtWrapImport('QtGui', globals(), ['QBrush','QColor', 'QDialog', 'QPushButton', 'QDialogButtonBox'])

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class ModsTool(AbstractPathTool):
    """
    docstring for ModsTool
    """
    def __init__(self, controller):
        super(ModsTool, self).__init__(controller)
        self.dialog = QDialog()
        self.initDialog()
        self.current_strand = None
        self.current_idx = None

    def __repr__(self):
        return "modsTool"  # first letter should be lowercase

    def initDialog(self):
        """
        """
        uiDlg = Ui_ModsDialog()
        uiDlg.setupUi(self.dialog)

        uiDlg.createButtonBox = QDialogButtonBox(self.dialog)
        uiDlg.createButtonBox.setCenterButtons(True)
        uiDlg.customButtonBox.setObjectName(_fromUtf8("customButtonBox"))
        uiDlg.dialogGridLayout.addWidget(uiDlg.createButtonBox, 2, 0, 1, 1)
        
        saveButton = QPushButton("Save", uiDlg.createButtonBox)
        uiDlg.createButtonBox.addButton(saveButton, QDialogButtonBox.ActionRole)
        saveButton.released.connect(self.saveModChecker)

        deleteButton = QPushButton("Delete", uiDlg.createButtonBox)
        uiDlg.createButtonBox.addButton(deleteButton, QDialogButtonBox.ActionRole)
        deleteButton.released.connect(self.deleteModChecker)

        deleteInstButton = QPushButton("Delete Instance", uiDlg.createButtonBox)
        uiDlg.createButtonBox.addButton(deleteInstButton, QDialogButtonBox.ActionRole)
        deleteInstButton.released.connect(self.deleteInstModChecker)

        combobox = uiDlg.nameComboBox
        self.uiDlg = uiDlg
        combobox.addItem("New", "new")
        for mid, item in mods.iteritems():
            combobox.addItem(item['name'], mid)
        # end for
        combobox.currentIndexChanged.connect(self.displayCurrent)
        self.displayCurrent()

    def saveModChecker(self):#, button):
        # if button.text() == "Create":
        print "save clicked"
        part = self.current_strand.part()
        item, mid = self.getCurrentItem()

        if mid == "new":
            item, mid = part.createMod(item)
            combobox.addItem(item['name'], mid)
        else:
            part.modifyMod(item, mid)
        return 
    # end def

    def deleteModChecker(self):#, button):
        # if button.text() == "Create":
        part = self.current_strand.part()
        item, mid = self.getCurrentItem() 
        if mid != "new":
            part.destroyMod(mid)
    # end def

    def deleteInstModChecker(self):#, button):
        # if button.text() == "Create":
        part = self.current_strand.part()
        item, mid = self.getCurrentItem() 
        if mid != "new":
            part.destroyMod(mid)
    # end def

    def getCurrentItem(self):
        combobox = self.uiDlg.nameComboBox
        qvmid = combobox.itemData(combobox.currentIndex())
        mid = str(qvmid.toString())
        return mods.get(mid), mid
    # end def

    def displayCurrent(self):
        item, mid = self.getCurrentItem()
        if mid != 'new':
            uiDlg = self.uiDlg
            uiDlg.colorLineEdit.setText(item['color'])
            uiDlg.sequence5LineEdit.setText(item['seq5p'])
            uiDlg.sequence3LineEdit.setText(item['seq3p'])
            uiDlg.sequenceInternalLineEdit.setText(item['seqInt'])
            uiDlg.noteTextEdit.setText(item['note']) # notes
    # end def

    def saveCurrent(self):
        item, mid = self.getCurrentItem()
        uiDlg = self.uiDlg
        item['name'] = uiDlg.nameComboBox.text()
        item['color'] = str(uiDlg.colorLineEdit.text())
        item['seq5p'] = uiDlg.sequence5LineEdit.text()
        item['seq3p'] = uiDlg.sequence3LineEdit.text()
        item['seqInt'] = uiDlg.sequenceInternalLineEdit.text()
        item['note'] = uiDlg.noteTextEdit.text() # notes
    # end def

    def applyMod(self, strand, idx):
        self.current_strand = strand
        self.current_idx = idx
        self.dialog.show()
        mid = strand.part().getModID(strand, idx)
        if mid:
            combobox = self.uiDlg.nameComboBox
            mod = strand.part().getMod(mid)
            # print mod, mid
            idx = combobox.findText(mod['name'])
            combobox.setCurrentIndex(idx)
        self.dialog.setFocus()
        if self.dialog.exec_():  # apply the sequence if accept was clicked
            item, mid = self.getCurrentItem()
            strand.addMods(mid, item, idx)

