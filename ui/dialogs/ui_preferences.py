# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/preferences.ui'
#
# Created: Mon Aug 15 14:17:41 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName(_fromUtf8("Preferences"))
        Preferences.resize(344, 242)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Preferences.sizePolicy().hasHeightForWidth())
        Preferences.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(Preferences)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_honeycomb = QtGui.QWidget()
        self.tab_honeycomb.setObjectName(_fromUtf8("tab_honeycomb"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_honeycomb)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.dimensionsLabel1 = QtGui.QLabel(self.tab_honeycomb)
        self.dimensionsLabel1.setObjectName(_fromUtf8("dimensionsLabel1"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.dimensionsLabel1)
        self.honeycombGLayout = QtGui.QGridLayout()
        self.honeycombGLayout.setContentsMargins(-1, 3, -1, -1)
        self.honeycombGLayout.setObjectName(_fromUtf8("honeycombGLayout"))
        self.honeycombRowsSpinBox = QtGui.QSpinBox(self.tab_honeycomb)
        self.honeycombRowsSpinBox.setMinimum(6)
        self.honeycombRowsSpinBox.setMaximum(200)
        self.honeycombRowsSpinBox.setProperty(_fromUtf8("value"), 30)
        self.honeycombRowsSpinBox.setObjectName(_fromUtf8("honeycombRowsSpinBox"))
        self.honeycombGLayout.addWidget(self.honeycombRowsSpinBox, 0, 0, 1, 1)
        self.honeycombColsSpinBox = QtGui.QSpinBox(self.tab_honeycomb)
        self.honeycombColsSpinBox.setMinimum(6)
        self.honeycombColsSpinBox.setMaximum(200)
        self.honeycombColsSpinBox.setProperty(_fromUtf8("value"), 32)
        self.honeycombColsSpinBox.setObjectName(_fromUtf8("honeycombColsSpinBox"))
        self.honeycombGLayout.addWidget(self.honeycombColsSpinBox, 0, 1, 1, 1)
        self.hRowsLabel = QtGui.QLabel(self.tab_honeycomb)
        self.hRowsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.hRowsLabel.setObjectName(_fromUtf8("hRowsLabel"))
        self.honeycombGLayout.addWidget(self.hRowsLabel, 1, 0, 1, 1)
        self.hColsLabel = QtGui.QLabel(self.tab_honeycomb)
        self.hColsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.hColsLabel.setObjectName(_fromUtf8("hColsLabel"))
        self.honeycombGLayout.addWidget(self.hColsLabel, 1, 1, 1, 1)
        self.honeycombStepsSpinBox = QtGui.QSpinBox(self.tab_honeycomb)
        self.honeycombStepsSpinBox.setMinimum(2)
        self.honeycombStepsSpinBox.setMaximum(2000)
        self.honeycombStepsSpinBox.setSingleStep(1)
        self.honeycombStepsSpinBox.setProperty(_fromUtf8("value"), 2)
        self.honeycombStepsSpinBox.setObjectName(_fromUtf8("honeycombStepsSpinBox"))
        self.honeycombGLayout.addWidget(self.honeycombStepsSpinBox, 0, 2, 1, 1)
        self.hBasesLabel = QtGui.QLabel(self.tab_honeycomb)
        self.hBasesLabel.setObjectName(_fromUtf8("hBasesLabel"))
        self.honeycombGLayout.addWidget(self.hBasesLabel, 1, 2, 1, 1)
        self.formLayout_3.setLayout(0, QtGui.QFormLayout.FieldRole, self.honeycombGLayout)
        self.verticalLayout_3.addLayout(self.formLayout_3)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/part/honeycomb")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_honeycomb, icon, _fromUtf8(""))
        self.tab_square = QtGui.QWidget()
        self.tab_square.setObjectName(_fromUtf8("tab_square"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_square)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.dimensionsLabel2 = QtGui.QLabel(self.tab_square)
        self.dimensionsLabel2.setObjectName(_fromUtf8("dimensionsLabel2"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.dimensionsLabel2)
        self.squareGLayout = QtGui.QGridLayout()
        self.squareGLayout.setContentsMargins(-1, 3, -1, -1)
        self.squareGLayout.setObjectName(_fromUtf8("squareGLayout"))
        self.squareRowsSpinBox = QtGui.QSpinBox(self.tab_square)
        self.squareRowsSpinBox.setMinimum(6)
        self.squareRowsSpinBox.setMaximum(200)
        self.squareRowsSpinBox.setProperty(_fromUtf8("value"), 30)
        self.squareRowsSpinBox.setObjectName(_fromUtf8("squareRowsSpinBox"))
        self.squareGLayout.addWidget(self.squareRowsSpinBox, 0, 0, 1, 1)
        self.squareColsSpinBox = QtGui.QSpinBox(self.tab_square)
        self.squareColsSpinBox.setMinimum(6)
        self.squareColsSpinBox.setMaximum(200)
        self.squareColsSpinBox.setProperty(_fromUtf8("value"), 30)
        self.squareColsSpinBox.setObjectName(_fromUtf8("squareColsSpinBox"))
        self.squareGLayout.addWidget(self.squareColsSpinBox, 0, 1, 1, 1)
        self.sRowsLabel = QtGui.QLabel(self.tab_square)
        self.sRowsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sRowsLabel.setObjectName(_fromUtf8("sRowsLabel"))
        self.squareGLayout.addWidget(self.sRowsLabel, 1, 0, 1, 1)
        self.sColsLabel = QtGui.QLabel(self.tab_square)
        self.sColsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sColsLabel.setObjectName(_fromUtf8("sColsLabel"))
        self.squareGLayout.addWidget(self.sColsLabel, 1, 1, 1, 1)
        self.squareStepsSpinBox = QtGui.QSpinBox(self.tab_square)
        self.squareStepsSpinBox.setMinimum(2)
        self.squareStepsSpinBox.setMaximum(2000)
        self.squareStepsSpinBox.setObjectName(_fromUtf8("squareStepsSpinBox"))
        self.squareGLayout.addWidget(self.squareStepsSpinBox, 0, 2, 1, 1)
        self.sBasesLabel = QtGui.QLabel(self.tab_square)
        self.sBasesLabel.setObjectName(_fromUtf8("sBasesLabel"))
        self.squareGLayout.addWidget(self.sBasesLabel, 1, 2, 1, 1)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.FieldRole, self.squareGLayout)
        self.verticalLayout_2.addLayout(self.formLayout_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/part/square")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_square, icon1, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.defaulttoolLabel = QtGui.QLabel(Preferences)
        self.defaulttoolLabel.setObjectName(_fromUtf8("defaulttoolLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.defaulttoolLabel)
        self.defaulttoolComboBox = QtGui.QComboBox(Preferences)
        self.defaulttoolComboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.defaulttoolComboBox.setObjectName(_fromUtf8("defaulttoolComboBox"))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/pathtools/select")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.defaulttoolComboBox.addItem(icon2, _fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/pathtools/pencil")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.defaulttoolComboBox.addItem(icon3, _fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/pathtools/paint")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.defaulttoolComboBox.addItem(icon4, _fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/pathtools/addseq")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.defaulttoolComboBox.addItem(icon5, _fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.defaulttoolComboBox)
        self.zoomSpeedLabel = QtGui.QLabel(Preferences)
        self.zoomSpeedLabel.setObjectName(_fromUtf8("zoomSpeedLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.zoomSpeedLabel)
        self.zoomSpeedSlider = QtGui.QSlider(Preferences)
        self.zoomSpeedSlider.setMinimumSize(QtCore.QSize(140, 0))
        self.zoomSpeedSlider.setMinimum(1)
        self.zoomSpeedSlider.setMaximum(100)
        self.zoomSpeedSlider.setSingleStep(1)
        self.zoomSpeedSlider.setProperty(_fromUtf8("value"), 50)
        self.zoomSpeedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSpeedSlider.setInvertedControls(False)
        self.zoomSpeedSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.zoomSpeedSlider.setTickInterval(0)
        self.zoomSpeedSlider.setObjectName(_fromUtf8("zoomSpeedSlider"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.zoomSpeedSlider)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setInputMethodHints(QtCore.Qt.ImhNone)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.RestoreDefaults)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.actionClose = QtGui.QAction(Preferences)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))

        self.retranslateUi(Preferences)
        self.tabWidget.setCurrentIndex(0)
        self.defaulttoolComboBox.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Preferences.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Preferences.reject)
        QtCore.QObject.connect(self.actionClose, QtCore.SIGNAL(_fromUtf8("activated()")), Preferences.close)
        QtCore.QMetaObject.connectSlotsByName(Preferences)
        Preferences.setTabOrder(self.buttonBox, self.tabWidget)
        Preferences.setTabOrder(self.tabWidget, self.honeycombRowsSpinBox)
        Preferences.setTabOrder(self.honeycombRowsSpinBox, self.honeycombColsSpinBox)
        Preferences.setTabOrder(self.honeycombColsSpinBox, self.squareRowsSpinBox)
        Preferences.setTabOrder(self.squareRowsSpinBox, self.squareColsSpinBox)
        Preferences.setTabOrder(self.squareColsSpinBox, self.zoomSpeedSlider)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.dimensionsLabel1.setText(QtGui.QApplication.translate("Preferences", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Default</p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">dimensions</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.hRowsLabel.setText(QtGui.QApplication.translate("Preferences", "rows", None, QtGui.QApplication.UnicodeUTF8))
        self.hColsLabel.setText(QtGui.QApplication.translate("Preferences", "columns", None, QtGui.QApplication.UnicodeUTF8))
        self.hBasesLabel.setText(QtGui.QApplication.translate("Preferences", "bases (x21)", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_honeycomb), QtGui.QApplication.translate("Preferences", "Honeycomb", None, QtGui.QApplication.UnicodeUTF8))
        self.dimensionsLabel2.setText(QtGui.QApplication.translate("Preferences", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Default</p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">dimensions</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.sRowsLabel.setText(QtGui.QApplication.translate("Preferences", "rows", None, QtGui.QApplication.UnicodeUTF8))
        self.sColsLabel.setText(QtGui.QApplication.translate("Preferences", "columns", None, QtGui.QApplication.UnicodeUTF8))
        self.sBasesLabel.setText(QtGui.QApplication.translate("Preferences", "bases (x32)", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_square), QtGui.QApplication.translate("Preferences", "Square", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolLabel.setText(QtGui.QApplication.translate("Preferences", "Default tool at startup:", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(0, QtGui.QApplication.translate("Preferences", "Select Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(1, QtGui.QApplication.translate("Preferences", "Pencil Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(2, QtGui.QApplication.translate("Preferences", "Paint", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(3, QtGui.QApplication.translate("Preferences", "Add Seq", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomSpeedLabel.setText(QtGui.QApplication.translate("Preferences", "Mousewheel zoom speed:", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setText(QtGui.QApplication.translate("Preferences", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setShortcut(QtGui.QApplication.translate("Preferences", "Ctrl+W", None, QtGui.QApplication.UnicodeUTF8))

import dialogicons_rc
