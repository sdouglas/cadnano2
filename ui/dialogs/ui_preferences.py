# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogs/preferences.ui'
#
# Created: Tue Jul 19 13:57:52 2011
#      by: PyQt4 UI code generator snapshot-4.8.3-fbc8b1362812
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
        Preferences.resize(330, 120)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Preferences.sizePolicy().hasHeightForWidth())
        Preferences.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Preferences)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.defaulttoolComboBox = QtGui.QComboBox(Preferences)
        self.defaulttoolComboBox.setObjectName(_fromUtf8("defaulttoolComboBox"))
        self.defaulttoolComboBox.addItem(_fromUtf8(""))
        self.defaulttoolComboBox.addItem(_fromUtf8(""))
        self.defaulttoolComboBox.addItem(_fromUtf8(""))
        self.defaulttoolComboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.defaulttoolComboBox, 0, 3, 1, 1)
        self.zoomSpeedLabel = QtGui.QLabel(Preferences)
        self.zoomSpeedLabel.setObjectName(_fromUtf8("zoomSpeedLabel"))
        self.gridLayout.addWidget(self.zoomSpeedLabel, 1, 0, 1, 1)
        self.zoomSpeedSlider = QtGui.QSlider(Preferences)
        self.zoomSpeedSlider.setMaximum(100)
        self.zoomSpeedSlider.setProperty(_fromUtf8("value"), 50)
        self.zoomSpeedSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSpeedSlider.setInvertedAppearance(False)
        self.zoomSpeedSlider.setInvertedControls(False)
        self.zoomSpeedSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.zoomSpeedSlider.setTickInterval(0)
        self.zoomSpeedSlider.setObjectName(_fromUtf8("zoomSpeedSlider"))
        self.gridLayout.addWidget(self.zoomSpeedSlider, 1, 1, 1, 3)
        self.label = QtGui.QLabel(Preferences)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setInputMethodHints(QtCore.Qt.ImhNone)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.RestoreDefaults|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 4)

        self.retranslateUi(Preferences)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Preferences.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Preferences.reject)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(0, QtGui.QApplication.translate("Preferences", "Select Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(1, QtGui.QApplication.translate("Preferences", "Pencil Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(2, QtGui.QApplication.translate("Preferences", "Paint", None, QtGui.QApplication.UnicodeUTF8))
        self.defaulttoolComboBox.setItemText(3, QtGui.QApplication.translate("Preferences", "Add Seq", None, QtGui.QApplication.UnicodeUTF8))
        self.zoomSpeedLabel.setText(QtGui.QApplication.translate("Preferences", "Zoom speed", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Preferences", "Default Tool at Startup", None, QtGui.QApplication.UnicodeUTF8))

