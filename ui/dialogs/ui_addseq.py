# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/addseq.ui'
#
# Created: Wed Jul 20 17:04:34 2011
#      by: PyQt4 UI code generator snapshot-4.8.3-fbc8b1362812
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AddSeqDialog(object):
    def setupUi(self, AddSeqDialog):
        AddSeqDialog.setObjectName(_fromUtf8("AddSeqDialog"))
        AddSeqDialog.resize(493, 426)
        AddSeqDialog.setModal(True)
        self.dialogGridLayout = QtGui.QGridLayout(AddSeqDialog)
        self.dialogGridLayout.setObjectName(_fromUtf8("dialogGridLayout"))
        self.tabWidget = QtGui.QTabWidget(AddSeqDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabStandard = QtGui.QWidget()
        self.tabStandard.setObjectName(_fromUtf8("tabStandard"))
        self.standardTabGridLayout = QtGui.QGridLayout(self.tabStandard)
        self.standardTabGridLayout.setObjectName(_fromUtf8("standardTabGridLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.standardTabGridLayout.addItem(spacerItem, 3, 2, 1, 1)
        self.p8634Button = QtGui.QPushButton(self.tabStandard)
        self.p8634Button.setObjectName(_fromUtf8("p8634Button"))
        self.standardTabGridLayout.addWidget(self.p8634Button, 5, 1, 1, 1)
        self.p8064Button = QtGui.QPushButton(self.tabStandard)
        self.p8064Button.setObjectName(_fromUtf8("p8064Button"))
        self.standardTabGridLayout.addWidget(self.p8064Button, 4, 1, 1, 1)
        self.p7704Button = QtGui.QPushButton(self.tabStandard)
        self.p7704Button.setObjectName(_fromUtf8("p7704Button"))
        self.standardTabGridLayout.addWidget(self.p7704Button, 3, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.standardTabGridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.p7560Button = QtGui.QPushButton(self.tabStandard)
        self.p7560Button.setMinimumSize(QtCore.QSize(110, 0))
        self.p7560Button.setObjectName(_fromUtf8("p7560Button"))
        self.standardTabGridLayout.addWidget(self.p7560Button, 2, 1, 1, 1)
        self.p7308Button = QtGui.QPushButton(self.tabStandard)
        self.p7308Button.setMinimumSize(QtCore.QSize(110, 0))
        self.p7308Button.setObjectName(_fromUtf8("p7308Button"))
        self.standardTabGridLayout.addWidget(self.p7308Button, 1, 1, 1, 1)
        self.m13mp18Button = QtGui.QPushButton(self.tabStandard)
        self.m13mp18Button.setMinimumSize(QtCore.QSize(110, 0))
        self.m13mp18Button.setDefault(True)
        self.m13mp18Button.setObjectName(_fromUtf8("m13mp18Button"))
        self.standardTabGridLayout.addWidget(self.m13mp18Button, 0, 1, 1, 1)
        self.standardButtonBox = QtGui.QDialogButtonBox(self.tabStandard)
        self.standardButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.standardButtonBox.setObjectName(_fromUtf8("standardButtonBox"))
        self.standardTabGridLayout.addWidget(self.standardButtonBox, 6, 2, 1, 1)
        self.tabWidget.addTab(self.tabStandard, _fromUtf8(""))
        self.tabCustom = QtGui.QWidget()
        self.tabCustom.setObjectName(_fromUtf8("tabCustom"))
        self.customTabGridLayout = QtGui.QGridLayout(self.tabCustom)
        self.customTabGridLayout.setObjectName(_fromUtf8("customTabGridLayout"))
        self.customButtonBox = QtGui.QDialogButtonBox(self.tabCustom)
        self.customButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel)
        self.customButtonBox.setObjectName(_fromUtf8("customButtonBox"))
        self.customTabGridLayout.addWidget(self.customButtonBox, 1, 0, 1, 1)
        self.sequencePlainTextEdit = QtGui.QPlainTextEdit(self.tabCustom)
        self.sequencePlainTextEdit.setTabChangesFocus(True)
        self.sequencePlainTextEdit.setBackgroundVisible(False)
        self.sequencePlainTextEdit.setObjectName(_fromUtf8("sequencePlainTextEdit"))
        self.customTabGridLayout.addWidget(self.sequencePlainTextEdit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabCustom, _fromUtf8(""))
        self.dialogGridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(AddSeqDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.standardButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddSeqDialog.reject)
        QtCore.QObject.connect(self.customButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddSeqDialog.reject)
        QtCore.QObject.connect(self.customButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.m13mp18Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.p7308Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.p7560Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.p7704Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.p8064Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QObject.connect(self.p8634Button, QtCore.SIGNAL(_fromUtf8("clicked()")), AddSeqDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AddSeqDialog)
        AddSeqDialog.setTabOrder(self.m13mp18Button, self.p7308Button)
        AddSeqDialog.setTabOrder(self.p7308Button, self.p7560Button)
        AddSeqDialog.setTabOrder(self.p7560Button, self.p7704Button)
        AddSeqDialog.setTabOrder(self.p7704Button, self.p8064Button)
        AddSeqDialog.setTabOrder(self.p8064Button, self.p8634Button)
        AddSeqDialog.setTabOrder(self.p8634Button, self.sequencePlainTextEdit)
        AddSeqDialog.setTabOrder(self.sequencePlainTextEdit, self.customButtonBox)
        AddSeqDialog.setTabOrder(self.customButtonBox, self.tabWidget)

    def retranslateUi(self, AddSeqDialog):
        AddSeqDialog.setWindowTitle(QtGui.QApplication.translate("AddSeqDialog", "Choose a sequence", None, QtGui.QApplication.UnicodeUTF8))
        self.p8634Button.setText(QtGui.QApplication.translate("AddSeqDialog", "p8634", None, QtGui.QApplication.UnicodeUTF8))
        self.p8064Button.setText(QtGui.QApplication.translate("AddSeqDialog", "p8064", None, QtGui.QApplication.UnicodeUTF8))
        self.p7704Button.setText(QtGui.QApplication.translate("AddSeqDialog", "p7704", None, QtGui.QApplication.UnicodeUTF8))
        self.p7560Button.setText(QtGui.QApplication.translate("AddSeqDialog", "p7560", None, QtGui.QApplication.UnicodeUTF8))
        self.p7308Button.setText(QtGui.QApplication.translate("AddSeqDialog", "p7308", None, QtGui.QApplication.UnicodeUTF8))
        self.m13mp18Button.setText(QtGui.QApplication.translate("AddSeqDialog", "M13mp18", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStandard), QtGui.QApplication.translate("AddSeqDialog", "Standard", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCustom), QtGui.QApplication.translate("AddSeqDialog", "Custom", None, QtGui.QApplication.UnicodeUTF8))

