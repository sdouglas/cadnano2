#include "graphicsellipseitem.h"

void GraphicsEllipseItem::paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
                              QWidget *widget)
{
    Q_D(QGraphicsPathItem);
    Q_UNUSED(widget);
    painter->setPen(d->pen);
    painter->setBrush(d->brush);
    painter->drawPath(d->path);

    // if (option->state & QStyle::State_Selected)
    //     qt_graphicsItem_highlightSelected(this, painter, option);
}
