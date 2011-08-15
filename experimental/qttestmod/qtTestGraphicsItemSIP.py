#!/usr/bin/env python




import math

from PyQt4.QtCore import QRectF, Qt, QPointF, QLineF
from PyQt4.QtGui import QGraphicsItem, QGraphicsRectItem, \
                        QGraphicsView, QGraphicsScene, QApplication, \
                        QBrush, QPen, QPainterPath, QStyleOptionGraphicsItem,\
                        QPainter
import random
from timeit import Timer
import testitem

aRAND = random.Random()
maxH = 20
maxW = 20
maxX = 600
maxY = 600

class GraphWidget(QGraphicsView):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.timerId = 0

        scene = QGraphicsScene(self)
        scene.setItemIndexMethod(QGraphicsScene.BspTreeIndex)
        scene.setSceneRect(0, 0, maxX, maxY)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        self.itemtest = testitem.TestItem("something", None, scene)
        self.itemtest.setLine(QLineF(10, 10, 300, 300))
        
        self.scale(0.8, 0.8)
        self.setMinimumSize(maxX, maxY)
        self.setWindowTitle("Colliding test")


    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)
        
    def mousePressEvent(self, event):
        print self.itemtest.message()
    # end def

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    
    widget = GraphWidget()
    widget.show()
    
    sys.exit(app.exec_())
