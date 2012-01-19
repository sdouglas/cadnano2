from autostapleconfig import AutostapleConfig
import cadnano, util
import resources
util.qtWrapImport('QtGui', globals(), ['QIcon', 'QPixmap', 'QAction'])

class AutostapleHandler(object):
    def __init__(self, document, window):
        self.doc, self.win = document, window
        icon10 = QIcon()
        icon10.addPixmap(QPixmap(":/pathtools/autostaple"), QIcon.Normal, QIcon.Off)
        self.actionAutoStaple = QAction(window)
        self.actionAutoStaple.setIcon(icon10)
        self.actionAutoStaple.setText('AutoStaple')
        self.actionAutoStaple.setToolTip("Click this button to generate a default set of staples.")
        self.actionAutoStaple.setObjectName("actionAutoStaple")
        self.actionAutoStaple.triggered.connect(self.actionAutostapleSlot)
        self.win.topToolBar.addAction(self.actionAutoStaple)
        self.configDialog = None

    def actionAutostapleSlot(self):
        if self.configDialog == None:
            self.configDialog = AutostapleConfig(self.win, self)
        self.configDialog.show()

def documentWindowWasCreatedSlot(doc, win):
    doc.autostapleHandler = AutostapleHandler(doc, win)

# Initialization
for c in cadnano.app().documentControllers:
    doc, win = c.document(), c.window()
    doc.autostapleHandler = AutostapleHandler(doc, win)
cadnano.app().documentWindowWasCreatedSignal.connect(documentWindowWasCreatedSlot)
