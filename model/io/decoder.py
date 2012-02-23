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

import json
from exceptions import ImportError
from legacydecoder import import_legacy_dict
from ui.dialogs.ui_latticetype import Ui_LatticeType
import util, cadnano
if cadnano.app().isGui():#headless:
    from ui.dialogs.ui_latticetype import Ui_LatticeType
    util.qtWrapImport('QtGui', globals(),  ['QDialog', 'QDialogButtonBox'])


def decode(document, string):
    if cadnano.app().isGui():
        # from ui.dialogs.ui_latticetype import Ui_LatticeType
        # util.qtWrapImport('QtGui', globals(),  ['QDialog', 'QDialogButtonBox'])
        dialog = QDialog()
        dialogLT = Ui_LatticeType()  # reusing this dialog, should rename
        dialogLT.setupUi(dialog)

    # try:  # try to do it fast
    #     try:
    #         import cjson
    #         packageObject = cjson.decode(string)
    #     except:  # fall back to if cjson not available or on decode error
    #         packageObject = json.loads(string)
    # except ValueError:
    #     dialogLT.label.setText("Error decoding JSON object.")
    #     dialogLT.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
    #     dialog.exec_()
    #     return
    packageObject = json.loads(string)

    if packageObject.get('.format', None) != 'caDNAno2':
        import_legacy_dict(document, packageObject)