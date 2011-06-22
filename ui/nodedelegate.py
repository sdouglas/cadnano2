
# from QtGui import QStyledItemDelegate, QPainter, QModelIndex, QCheckBox, QLabel, QTextDocument
# from QtCore import QObject

import util
# import Qt stuff into the module namespace with PySide, PyQt4 independence
util.qtWrapImport('QtCore', globals(), ['QObject'] )
util.qtWrapImport('QtGui', globals(),  ['QStyledItemDelegate', 'QPainter', \
                                        'QModelIndex', 'QCheckBox', 'QLabel', \
                                        'QTextDocument', 'QWidget'])

class NodeDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        """
        """
        super(QStyledItemDelegate,self).__init__(parent)
        self.checkbox = None #QCheckBox
        self.label = None #QLabel
        self.document = None #QTextDocument 
    #end def
    
    def closeAndCommitEditor(self):
        """"""
    #end def
    def paintWidget(QPainter *painter, const QRect &rect,
                 const QString &cacheKey, QWidget *widget):
        """"""
    #end def
    def paint(QPainter *painter, const QStyleOptionViewItem &option,
                            const QModelIndex &index):
    #end def
    def sizeHint(const QStyleOptionViewItem &option,
                   const QModelIndex &index):
    """returns QSize """
    #end def
    
    def createEditor(QWidget *parent,
                          const QStyleOptionViewItem &option,
                          const QModelIndex &index):
        """returns QWidget *"""
    #end def
    def setEditorData(QWidget *editor,
                       const QModelIndex &index):
        """"""
    #end def
    def setModelData(QWidget *editor, QAbstractItemModel *model,
                      const QModelIndex &index):
        """"""
    #end def
# end class