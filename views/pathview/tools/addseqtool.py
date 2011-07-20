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

from abstractpathtool import AbstractPathTool
import util
util.qtWrapImport('QtGui', globals(), ['QPen', 'QColor', 'QDialog'])
util.qtWrapImport('QtCore', globals(), ['Qt', 'QPointF', 'QObject', 'QString', \
                                        'QSignalMapper', 'pyqtSignal', 'pyqtSlot'])
from model.enum import StrandType
from data.dnasequences import sequences
from ui.dialogs.ui_addseq import Ui_AddSeqDialog

class AddSeqTool(AbstractPathTool):
    def __init__(self, controller, parent=None):
        AbstractPathTool.__init__(self, controller, parent)
        self.initDialog()

    def initDialog(self):
        print "initDia"
        self.dialog = QDialog()
        asDlg = Ui_AddSeqDialog()
        asDlg.setupUi(self.dialog)
        self.buttons = [asDlg.m13mp18Button,
                        asDlg.p7308Button,
                        asDlg.p7560Button,
                        asDlg.p7704Button,
                        asDlg.p8064Button,
                        asDlg.p8634Button]
        self.signalMapper = QSignalMapper(self)
        for num, button in enumerate(self.buttons):
            print button, num, button.objectName()
            self.signalMapper.setMapping(button, num)
            button.clicked.connect(self.signalMapper.map)
        self.signalMapper.mapped.connect(self.userChoseStandardSeq)
        # self.handleButtonClick.connect(self.userChoseSeq)

    def mousePressPathHelix(self, pathHelix, event):
        strandType, idx = self.baseAtPoint(pathHelix, event.pos())
        self.vh = pathHelix.vhelix()
        self.strandType = strandType
        self.idx = idx
        result = self.dialog.exec_()
        print "result", result
        # self.dialog.open(self, SLOT("userChoseSeq(QString)"))
    
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
        if vh.hasLoopOrSkipAt(strandType, baseIdx) > 0:
            loopBases = vh.hasLoopOrSkipAt(strandType, baseIdx)
            compLoopBases = vh.hasLoopOrSkipAt(oppositeStrand, baseIdx)
            if loopBases != compLoopBases and strandType == StrandType.Staple:
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

    @pyqtSlot(str)
    def userChoseStandardSeq(self, optionChosen):
        print "slot userChoseSeq", optionChosen
        optionChosen = str(self.buttons[optionChosen].text())
        print "lookup", optionChosen
        seqToUse = ""
        knownSeqNamedByChosenOption = sequences.get(optionChosen, None)
        print knownSeqNamedByChosenOption
        sequenceAfterExtractionOfBasePairChars = util.strToDna(optionChosen)
        if knownSeqNamedByChosenOption:
            seqToUse = knownSeqNamedByChosenOption
        elif len(sequenceAfterExtractionOfBasePairChars)==len(optionChosen):
            seqToUse = sequenceAfterExtractionOfBasePairChars
        vh, strandType, idx = self.vh, self.strandType, self.idx
        vh.applySequenceAt(strandType, idx, seqToUse)

    @pyqtSlot(str)
    def userChoseSeq(self, optionChosen):
        print "slot userChoseSeq", optionChosen
        optionChosen = str(optionChosen)
        seqToUse = ""
        knownSeqNamedByChosenOption = sequences.get(optionChosen, None)
        sequenceAfterExtractionOfBasePairChars = util.strToDna(optionChosen)
        if knownSeqNamedByChosenOption:
            seqToUse = knownSeqNamedByChosenOption
        elif len(sequenceAfterExtractionOfBasePairChars)==len(optionChosen):
            seqToUse = sequenceAfterExtractionOfBasePairChars
        vh, strandType, idx = self.vh, self.strandType, self.idx
        vh.applySequenceAt(strandType, idx, seqToUse)

