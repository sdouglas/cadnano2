# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/latticetype.ui'
#
# Created: Wed Jul 20 13:30:24 2011
#      by: PyQt4 UI code generator snapshot-4.8.3-fbc8b1362812
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LatticeType(object):
    def setupUi(self, LatticeType):
        LatticeType.setObjectName(_fromUtf8("LatticeType"))
        LatticeType.resize(213, 92)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LatticeType.sizePolicy().hasHeightForWidth())
        LatticeType.setSizePolicy(sizePolicy)
        LatticeType.setSizeGripEnabled(False)
        self.widget = QtGui.QWidget(LatticeType)
        self.widget.setGeometry(QtCore.QRect(10, 10, 191, 64))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LatticeType)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LatticeType.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LatticeType.reject)
        QtCore.QMetaObject.connectSlotsByName(LatticeType)

    def retranslateUi(self, LatticeType):
        LatticeType.setWindowTitle(QtGui.QApplication.translate("LatticeType", "Import", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LatticeType", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Is this a square-lattice design?</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

