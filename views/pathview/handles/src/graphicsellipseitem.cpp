#include "graphicsellipseitem.h"

GraphicsEllipseItem::GraphicsEllipseItem(QGraphicsItem * parent) :  QGraphicsEllipseItem(parent)
{
   
}

void GraphicsEllipseItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
                              QWidget *widget)
{
    Q_UNUSED(widget); Q_UNUSED(option);
    painter->setPen(pen());
    painter->setBrush(brush());
    if ((spanAngle() != 0) && (qAbs(spanAngle()) % (360 * 16) == 0))
        painter->drawEllipse(rect());
    else
        painter->drawPie(rect(), startAngle(), spanAngle());

    // if (option->state & QStyle::State_Selected)
    //     qt_graphicsItem_highlightSelected(this, painter, option);
}
