# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/about.ui'
#
# Created: Tue Nov 29 17:53:16 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName(_fromUtf8("About"))
        About.resize(474, 304)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(About.sizePolicy().hasHeightForWidth())
        About.setSizePolicy(sizePolicy)
        About.setWindowTitle(QtGui.QApplication.translate("About", "About cadnano", None, QtGui.QApplication.UnicodeUTF8))
        About.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(About)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(About)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(440, 270))
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.appname = QtGui.QLabel(self.frame)
        self.appname.setGeometry(QtCore.QRect(0, 10, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.appname.setFont(font)
        self.appname.setText(QtGui.QApplication.translate("About", "cadnano", None, QtGui.QApplication.UnicodeUTF8))
        self.appname.setObjectName(_fromUtf8("appname"))
        self.version = QtGui.QLabel(self.frame)
        self.version.setGeometry(QtCore.QRect(0, 40, 101, 16))
        self.version.setText(QtGui.QApplication.translate("About", "version 2.0.8", None, QtGui.QApplication.UnicodeUTF8))
        self.version.setObjectName(_fromUtf8("version"))
        self.info = QtGui.QLabel(self.frame)
        self.info.setGeometry(QtCore.QRect(0, 90, 411, 161))
        self.info.setText(QtGui.QApplication.translate("About", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright © 2009–2011 <a href=\"http://cadnano.org/\"><span style=\" text-decoration: underline; color:#0000ff;\">cadnano.org</span></a>.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">cadnano</span> is free and open-source. The <a href=\"https://github.com/sdouglas/cadnano2/\"><span style=\" text-decoration: underline; color:#0000ff;\">source code</span></a> is available under the <a href=\"http://cadnano.org/license\"><span style=\" text-decoration: underline; color:#0000ff;\">MIT license</span></a>.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The development has been supported by <a href=\"http://wyss.harvard.edu/\"><span style=\" text-decoration: underline; color:#0000ff;\">Wyss Institute at Harvard University</span></a> and the <a href=\"http://www.dana-farber.org/\"><span style=\" text-decoration: underline; color:#0000ff;\">Dana-Farber Cancer Institute</span></a>, and the laboratories of <a href=\"http://research4.dfci.harvard.edu/shih/\"><span style=\" text-decoration: underline; color:#0000ff;\">William Shih</span></a> and <a href=\"http://arep.med.harvard.edu/\"><span style=\" text-decoration: underline; color:#0000ff;\">George Church</span></a>.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Send <a href=\"http://cadnano.org/feedback\"><span style=\" text-decoration: underline; color:#0000ff;\">feedback</span></a> or <a href=\"http://cadnano.org/join\"><span style=\" text-decoration: underline; color:#0000ff;\">join</span></a> our team.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setTextFormat(QtCore.Qt.RichText)
        self.info.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.info.setWordWrap(True)
        self.info.setObjectName(_fromUtf8("info"))
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        pass

import dialogicons_rc
