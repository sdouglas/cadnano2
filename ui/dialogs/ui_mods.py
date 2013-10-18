# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\dialogs\mods.ui'
#
# Created: Fri Oct 18 16:09:26 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ModsDialog(object):
    def setupUi(self, ModsDialog):
        ModsDialog.setObjectName(_fromUtf8("ModsDialog"))
        ModsDialog.resize(500, 500)
        ModsDialog.setModal(True)
        self.dialogGridLayout = QtGui.QGridLayout(ModsDialog)
        self.dialogGridLayout.setObjectName(_fromUtf8("dialogGridLayout"))
        self.customButtonBox = QtGui.QDialogButtonBox(ModsDialog)
        self.customButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel)
        self.customButtonBox.setCenterButtons(True)
        self.customButtonBox.setObjectName(_fromUtf8("customButtonBox"))
        self.dialogGridLayout.addWidget(self.customButtonBox, 1, 0, 1, 1)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.nameLabel = QtGui.QLabel(ModsDialog)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.nameLabel)
        self.nameComboBox = QtGui.QComboBox(ModsDialog)
        self.nameComboBox.setEditable(True)
        self.nameComboBox.setObjectName(_fromUtf8("nameComboBox"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.nameComboBox)
        self.colorLabel = QtGui.QLabel(ModsDialog)
        self.colorLabel.setObjectName(_fromUtf8("colorLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.colorLabel)
        self.colorLineEdit = QtGui.QLineEdit(ModsDialog)
        self.colorLineEdit.setObjectName(_fromUtf8("colorLineEdit"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.colorLineEdit)
        self.sequence5Label = QtGui.QLabel(ModsDialog)
        self.sequence5Label.setObjectName(_fromUtf8("sequence5Label"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.sequence5Label)
        self.sequence5LineEdit = QtGui.QLineEdit(ModsDialog)
        self.sequence5LineEdit.setObjectName(_fromUtf8("sequence5LineEdit"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.sequence5LineEdit)
        self.sequence3Label = QtGui.QLabel(ModsDialog)
        self.sequence3Label.setObjectName(_fromUtf8("sequence3Label"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.sequence3Label)
        self.sequence3LineEdit = QtGui.QLineEdit(ModsDialog)
        self.sequence3LineEdit.setObjectName(_fromUtf8("sequence3LineEdit"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.sequence3LineEdit)
        self.sequenceInternalLabel = QtGui.QLabel(ModsDialog)
        self.sequenceInternalLabel.setObjectName(_fromUtf8("sequenceInternalLabel"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.LabelRole, self.sequenceInternalLabel)
        self.sequenceInternalLineEdit = QtGui.QLineEdit(ModsDialog)
        self.sequenceInternalLineEdit.setObjectName(_fromUtf8("sequenceInternalLineEdit"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.FieldRole, self.sequenceInternalLineEdit)
        self.notesLabel = QtGui.QLabel(ModsDialog)
        self.notesLabel.setObjectName(_fromUtf8("notesLabel"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.LabelRole, self.notesLabel)
        self.textEdit = QtGui.QTextEdit(ModsDialog)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.FieldRole, self.textEdit)
        self.dialogGridLayout.addLayout(self.formLayout_2, 0, 0, 1, 1)

        self.retranslateUi(ModsDialog)
        QtCore.QObject.connect(self.customButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ModsDialog.reject)
        QtCore.QObject.connect(self.customButtonBox, QtCore.SIGNAL(_fromUtf8("clicked(QAbstractButton*)")), ModsDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ModsDialog)

    def retranslateUi(self, ModsDialog):
        ModsDialog.setWindowTitle(_translate("ModsDialog", "Choose a sequence", None))
        self.nameLabel.setText(_translate("ModsDialog", "Name", None))
        self.colorLabel.setText(_translate("ModsDialog", "color", None))
        self.sequence5Label.setText(_translate("ModsDialog", "sequence 5\'", None))
        self.sequence3Label.setText(_translate("ModsDialog", "sequence 3\'", None))
        self.sequenceInternalLabel.setText(_translate("ModsDialog", "sequence internal", None))
        self.notesLabel.setText(_translate("ModsDialog", "Notes", None))

