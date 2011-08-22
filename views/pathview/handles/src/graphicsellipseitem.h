
#ifndef ELLIPSEITEM_H
#define ELLIPSEITEM_H


// QT_MODULE(Gui)

#include <QtGui/qgraphicsitem.h>
#include <QtGui/qgraphicswidget.h>
#include <QtGui/qstyleoptiongraphicsitem.h>
#include <QtGui/qpainter.h>


class GraphicsEllipseItem : public QGraphicsEllipseItem {
    // This is needed by the Qt Meta-Object Compiler.
    Q_OBJECT
    
    public:
        GraphicsEllipseItem (QGraphicsItem *parent = 0);
        virtual ~GraphicsEllipseItem ();
        virtual void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget = 0) = 0; 
    
#endif