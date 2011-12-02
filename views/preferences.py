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
from ui.dialogs.ui_preferences import Ui_Preferences
from views import styles
import util
util.qtWrapImport('QtCore', globals(), ['QObject', 'QSettings'])
util.qtWrapImport('QtGui', globals(), ['QDialog', 'QDialogButtonBox'])

class Preferences():
    """docstring for Preferences"""
    def __init__(self):
        self.qs = QSettings()
        self.dialog = QDialog()
        self.uiPrefs = Ui_Preferences()
        self.uiPrefs.setupUi(self.dialog)
        self.readPreferences()
        self.uiPrefs.honeycombRowsSpinBox.valueChanged.connect(self.setHoneycombRows)
        self.uiPrefs.honeycombColsSpinBox.valueChanged.connect(self.setHoneycombCols)
        self.uiPrefs.honeycombStepsSpinBox.valueChanged.connect(self.setHoneycombSteps)
        self.uiPrefs.squareRowsSpinBox.valueChanged.connect(self.setSquareRows)
        self.uiPrefs.squareColsSpinBox.valueChanged.connect(self.setSquareCols)
        self.uiPrefs.squareStepsSpinBox.valueChanged.connect(self.setSquareSteps)
        self.uiPrefs.autoScafComboBox.currentIndexChanged.connect(self.setAutoScaf)
        self.uiPrefs.defaultToolComboBox.currentIndexChanged.connect(self.setStartupTool)
        self.uiPrefs.zoomSpeedSlider.valueChanged.connect(self.setZoomSpeed)
        # self.uiPrefs.helixAddCheckBox.toggled.connect(self.setZoomToFitOnHelixAddition)
        self.uiPrefs.buttonBox.clicked.connect(self.handleButtonClick)

    def showDialog(self):
        self.dialog.exec_()
        # self.dialog.show()  # launch prefs in mode-less dialog

    def handleButtonClick(self, button):
        """
        Restores defaults. Other buttons are ignored because connections
        are already set up in qt designer.
        """
        if self.uiPrefs.buttonBox.buttonRole(button) == QDialogButtonBox.ResetRole:
            self.restoreDefaults()

    def readPreferences(self):
        self.qs.beginGroup("Preferences")
        self.honeycombRows = self.qs.value("honeycombRows", styles.HONEYCOMB_PART_MAXROWS).toInt()[0]
        self.honeycombCols = self.qs.value("honeycombCols", styles.HONEYCOMB_PART_MAXCOLS).toInt()[0]
        self.honeycombSteps = self.qs.value("honeycombSteps", styles.HONEYCOMB_PART_MAXSTEPS).toInt()[0]
        self.squareRows = self.qs.value("squareRows", styles.SQUARE_PART_MAXROWS).toInt()[0]
        self.squareCols = self.qs.value("squareCols", styles.SQUARE_PART_MAXCOLS).toInt()[0]
        self.squareSteps = self.qs.value("squareSteps", styles.SQUARE_PART_MAXSTEPS).toInt()[0]
        self.autoScafIndex = self.qs.value("autoScaf", styles.PREF_AUTOSCAF_INDEX).toInt()[0]
        self.startupToolIndex = self.qs.value("startupTool", styles.PREF_STARTUP_TOOL_INDEX).toInt()[0]
        self.zoomSpeed = self.qs.value("zoomSpeed", styles.PREF_ZOOM_SPEED).toInt()[0]
        self.zoomOnHelixAdd = self.qs.value("zoomOnHelixAdd", styles.PREF_ZOOM_AFTER_HELIX_ADD).toBool()
        self.qs.endGroup()
        self.uiPrefs.honeycombRowsSpinBox.setProperty("value", self.honeycombRows)
        self.uiPrefs.honeycombColsSpinBox.setProperty("value", self.honeycombCols)
        self.uiPrefs.honeycombStepsSpinBox.setProperty("value", self.honeycombSteps)
        self.uiPrefs.squareRowsSpinBox.setProperty("value", self.squareRows)
        self.uiPrefs.squareColsSpinBox.setProperty("value", self.squareCols)
        self.uiPrefs.squareStepsSpinBox.setProperty("value", self.squareSteps)
        self.uiPrefs.autoScafComboBox.setCurrentIndex(self.autoScafIndex)
        self.uiPrefs.defaultToolComboBox.setCurrentIndex(self.startupToolIndex)
        self.uiPrefs.zoomSpeedSlider.setProperty("value", self.zoomSpeed)
        # self.uiPrefs.helixAddCheckBox.setChecked(self.zoomOnHelixAdd)

    def restoreDefaults(self):
        self.uiPrefs.honeycombRowsSpinBox.setProperty("value", styles.HONEYCOMB_PART_MAXROWS)
        self.uiPrefs.honeycombColsSpinBox.setProperty("value", styles.HONEYCOMB_PART_MAXCOLS)
        self.uiPrefs.honeycombStepsSpinBox.setProperty("value", styles.HONEYCOMB_PART_MAXSTEPS)
        self.uiPrefs.squareRowsSpinBox.setProperty("value", styles.SQUARE_PART_MAXROWS)
        self.uiPrefs.squareColsSpinBox.setProperty("value", styles.SQUARE_PART_MAXCOLS)
        self.uiPrefs.squareStepsSpinBox.setProperty("value", styles.SQUARE_PART_MAXSTEPS)
        self.uiPrefs.autoScafComboBox.setCurrentIndex(styles.PREF_AUTOSCAF_INDEX)
        self.uiPrefs.defaultToolComboBox.setCurrentIndex(styles.PREF_STARTUP_TOOL_INDEX)
        self.uiPrefs.zoomSpeedSlider.setProperty("value", styles.PREF_ZOOM_SPEED)
        # self.uiPrefs.helixAddCheckBox.setChecked(styles.PREF_ZOOM_AFTER_HELIX_ADD)

    def setHoneycombRows(self, rows):
        self.honeycombRows = rows
        self.qs.beginGroup("Preferences")
        self.qs.setValue("honeycombRows", self.honeycombRows)
        self.qs.endGroup()

    def setHoneycombCols(self, cols):
        self.honeycombCols = cols
        self.qs.beginGroup("Preferences")
        self.qs.setValue("honeycombCols", self.honeycombCols)
        self.qs.endGroup()

    def setHoneycombSteps(self, steps):
        self.honeycombSteps = steps
        self.qs.beginGroup("Preferences")
        self.qs.setValue("honeycombSteps", self.honeycombSteps)
        self.qs.endGroup()

    def setSquareRows(self, rows):
        self.squareRows = rows
        self.qs.beginGroup("Preferences")
        self.qs.setValue("squareRows", self.squareRows)
        self.qs.endGroup()

    def setSquareCols(self, cols):
        self.squareCols = cols
        self.qs.beginGroup("Preferences")
        self.qs.setValue("squareCols", self.squareCols)
        self.qs.endGroup()

    def setSquareSteps(self, steps):
        self.squareSteps = steps
        self.qs.beginGroup("Preferences")
        self.qs.setValue("squareSteps", self.squareSteps)
        self.qs.endGroup()

    def setAutoScaf(self, index):
        self.autoScafIndex = index
        self.qs.beginGroup("Preferences")
        self.qs.setValue("autoScaf", self.autoScafIndex)
        self.qs.endGroup()

    def setStartupTool(self, index):
        self.startupToolIndex = index
        self.qs.beginGroup("Preferences")
        self.qs.setValue("startupTool", self.startupToolIndex)
        self.qs.endGroup()

    def setZoomSpeed(self, speed):
        self.zoomSpeed = speed
        self.qs.beginGroup("Preferences")
        self.qs.setValue("zoomSpeed", self.zoomSpeed)
        self.qs.endGroup()

    # def setZoomToFitOnHelixAddition(self, checked):
    #     self.zoomOnHelixAdd = checked
    #     self.qs.beginGroup("Preferences")
    #     self.qs.setValue("zoomOnHelixAdd", self.zoomOnHelixAdd)
    #     self.qs.endGroup()

    def getAutoScafType(self):
        return ['Mid-seam', 'Raster'][self.autoScafIndex]

    def getStartupToolName(self):
        return ['Select', 'Pencil', 'Paint', 'AddSeq'][self.startupToolIndex]

