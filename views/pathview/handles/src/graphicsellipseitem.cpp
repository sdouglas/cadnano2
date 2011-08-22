#include "graphicsellipseitem.h"

GraphicsEllipseItem::GraphicsEllipseItem(QGraphicsItem * parent) :  QGraphicsEllipseItem(parent)
{
   
}

virtual void GraphicsEllipseItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
                              QWidget *widget)
{
    Q_D(QGraphicsEllipseItem);
    Q_UNUSED(widget);
    painter->setPen(d->pen);
    painter->setBrush(d->brush);
    if ((d->spanAngle != 0) && (qAbs(d->spanAngle) % (360 * 16) == 0))
        painter->drawEllipse(d->rect);
    else
        painter->drawPie(d->rect, d->startAngle, d->spanAngle);

    // if (option->state & QStyle::State_Selected)
    //     qt_graphicsItem_highlightSelected(this, painter, option);
}
