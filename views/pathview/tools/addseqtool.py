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
selecttool
Created by Shawn Douglas on 2011-06-21.
"""

import re
from abstractpathtool import AbstractPathTool
from model.enum import StrandType
from data.dnasequences import sequences
from ui.dialogs.ui_addseq import Ui_AddSeqDialog
from views import styles
import util

util.qtWrapImport('QtGui', globals(), ['QBrush','QColor', 'QDialog', \
                                       'QDialogButtonBox', 'QFont', 'QPen', \
                                       'QRadioButton', 'QSyntaxHighlighter', \
                                       'QTextCharFormat'])
util.qtWrapImport('QtCore', globals(), ['Qt', 'QObject', 'QPointF', \
                                        'QRegExp', \
                                        'QString', 'QSignalMapper', \
                                        'pyqtSignal', 'pyqtSlot'])
dnapattern = QRegExp("[^ACGTacgt]")


class DNAHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        self.format = QTextCharFormat()
        self.format.setForeground(QBrush(styles.INVALID_DNA_COLOR))
        if styles.UNDERLINE_INVALID_DNA:
            self.format.setFontUnderline(True)
            self.format.setUnderlineColor(styles.INVALID_DNA_COLOR)

    def highlightBlock(self, text):
        index = dnapattern.indexIn(text)
        while index >= 0:
            length = dnapattern.matchedLength()
            self.setFormat(index, length, self.format)
            index = text.indexOf(dnapattern, index + length)
        self.setCurrentBlockState(0)


class AddSeqTool(AbstractPathTool):
    def __init__(self, controller, parent=None):
        AbstractPathTool.__init__(self, controller, parent)
        self.dialog = QDialog()
        self.buttons = []
        self.seqBox = None
        self.chosenStandardSequence = None  # state for tab switching
        self.customSequenceIsValid = False  # state for tab switching
        self.useCustomSequence = False  # for applying sequence
        self.validatedSequenceToApply = None
        self.initDialog()

    def initDialog(self):
        """
        1. Create buttons according to available scaffold sequences and
        add them to the dialog.
        2. Map the clicked signal of those buttons to keep track of what
        sequence gets selected.
        3. Watch the tabWidget change signal to determine whether a
        standard or custom sequence should be applied.
        """
        uiDlg = Ui_AddSeqDialog()
        uiDlg.setupUi(self.dialog)
        self.signalMapper = QSignalMapper(self)
        # set up the radio buttons
        for i, name in enumerate(sorted(sequences.keys())):
            radioButton = QRadioButton(uiDlg.groupBox)
            radioButton.setObjectName(name + "Button")
            radioButton.setText(name)
            self.buttons.append(radioButton)
            uiDlg.verticalLayout.addWidget(radioButton)
            self.signalMapper.setMapping(radioButton, i)
            radioButton.clicked.connect(self.signalMapper.map)
        self.signalMapper.mapped.connect(self.standardSequenceChangedSlot)
        uiDlg.tabWidget.currentChanged.connect(self.tabWidgetChangedSlot)
        # disable apply until valid option or custom sequence is chosen
        self.applyButton = uiDlg.customButtonBox.button(QDialogButtonBox.Apply)
        self.applyButton.setEnabled(False)
        # watch sequence textedit box to validate custom sequences
        self.seqBox = uiDlg.seqTextEdit
        self.seqBox.textChanged.connect(self.validateCustomSequence)
        self.highlighter = DNAHighlighter(self.seqBox)
        # finally, pre-click the M13mp18 radio button
        self.buttons[0].click()

    def tabWidgetChangedSlot(self, index):
        applyEnabled = False
        if index == 1:  # Custom Sequence
            self.validateCustomSequence()
            if self.customSequenceIsValid:
                applyEnabled = True
        else:  # Standard Sequence
            self.useCustomSequence = False
            if self.chosenStandardSequence != None:
                # Overwrite sequence in case custom has been applied
                activeButton = self.buttons[self.chosenStandardSequence]
                sequenceName = str(activeButton.text())
                self.validatedSequenceToApply = sequences.get(sequenceName, None)
                applyEnabled = True
        self.applyButton.setEnabled(applyEnabled)

    def standardSequenceChangedSlot(self, optionChosen):
        """
        Connected to signalMapper to receive a signal whenever user selects
        a different sequence in the standard tab.
        """
        sequenceName = str(self.buttons[optionChosen].text())
        self.validatedSequenceToApply = sequences.get(sequenceName, None)
        self.chosenStandardSequence = optionChosen
        self.applyButton.setEnabled(True)

    def validateCustomSequence(self):
        """
        Called when:
        1. User enters custom sequence (i.e. seqBox emits textChanged signal)
        2. tabWidgetChangedSlot sees the user has switched to custom tab.

        When the sequence is valid, make the applyButton active for clicking.
        Otherwise
        """
        userSequence = self.seqBox.toPlainText()
        if len(userSequence) == 0:
            self.customSequenceIsValid = False
            return  # tabWidgetChangedSlot will disable applyButton
        if dnapattern.indexIn(userSequence) == -1:  # no invalid characters
            self.useCustomSequence = True
            self.customSequenceIsValid = True
            self.applyButton.setEnabled(True)
        else:
            self.customSequenceIsValid = False
            self.applyButton.setEnabled(False)

    def mousePressPathHelix(self, pathHelix, event):
        strandType, idx = self.baseAtPoint(pathHelix, event.pos())
        if self.dialog.exec_():  # apply the sequence if accept was clicked
            if self.useCustomSequence:
                self.validatedSequenceToApply = str(self.seqBox.toPlainText().toUpper())
            vh = pathHelix.vhelix()
            vh.applySequenceAt(strandType, idx, self.validatedSequenceToApply)

    def updateLocation(self, pathHelix, scenePos, *args):
        AbstractPathTool.updateLocation(self, pathHelix, scenePos, *args)
        if pathHelix == None:
            return
        posItem = pathHelix.mapFromScene(scenePos)
        strandType, baseIdx = self.baseAtPoint(pathHelix, posItem)
        vh = pathHelix.vhelix()
        if strandType == StrandType.Scaffold:
            oppositeStrand = StrandType.Staple
        else:
            oppositeStrand = StrandType.Scaffold
        if vh.hasInsertOrSkipAt(strandType, baseIdx) > 0:
            insertBases = vh.hasInsertOrSkipAt(strandType, baseIdx)
            compInsertBases = vh.hasInsertOrSkipAt(oppositeStrand, baseIdx)
            if insertBases != compInsertBases and strandType == StrandType.Staple:
                newLoc = pathHelix.baseLocation(strandType, baseIdx)
                if self.pos() != newLoc:
                    self.setPos(*newLoc)
                if not self.isVisible():
                    self.show()
                return
        if vh.hasEmptyAt(strandType, baseIdx):
            if self.isVisible():
                self.hide()
            return
        fivePBase = pathHelix.vhelix().fivePEndOfSegmentThrough(StrandType.Scaffold, baseIdx)
        if fivePBase == None:
            self.hide()
        else:
            vh, strandType, idx = fivePBase
            phg = pathHelix.pathHelixGroup()
            ph2 = phg.pathHelixForVHelix(vh)
            fivePBaseLoc = QPointF(*ph2.baseLocation(strandType, idx))
            fivePBaseLocSelfCoords = pathHelix.mapFromItem(ph2, fivePBaseLoc)
            self.setPos(fivePBaseLocSelfCoords)
            if not self.isVisible():
                self.show()
