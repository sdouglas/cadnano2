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
util.qtWrapImport('QtCore', globals(), ['QSignalMapper'])
util.qtWrapImport('QtGui', globals(), ['QBrush','QColor', 'QDialog'])


class ModsTool(AbstractPathTool):
    """
    docstring for ModsTool
    """
    def __init__(self, controller):
        super(ModsTool, self).__init__(controller)
        self.dialog = QDialog()
        self.buttons = []
        self.seqBox = None
        self.chosenStandardSequence = None  # state for tab switching
        self.customSequenceIsValid = False  # state for tab switching
        self.useCustomSequence = False  # for applying sequence
        self.validatedSequenceToApply = None
        self.initDialog()

    def __repr__(self):
        return "modsTool"  # first letter should be lowercase

    def initDialog(self):
        """
        1. Create buttons according to available scaffold sequences and
        add them to the dialog.
        2. Map the clicked signal of those buttons to keep track of what
        sequence gets selected.
        3. Watch the tabWidget change signal to determine whether a
        standard or custom sequence should be applied.
        """
        uiDlg = Ui_ModsDialog()
        uiDlg.setupUi(self.dialog)
        self.signalMapper = QSignalMapper(self)
