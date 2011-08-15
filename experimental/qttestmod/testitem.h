#ifndef TESTITEM_H
#define TESTITEM_H

#include <QGraphicsLineItem>
#include <qstring.h>
#include <qcolor.h>

QT_BEGIN_NAMESPACE
class QGraphicsPolygonItem;
class QGraphicsLineItem;
class QGraphicsScene;
class QRectF;
class QGraphicsSceneMouseEvent;
class QPainterPath;
class QString;
class QColor;
QT_END_NAMESPACE

//! [0]
class TestItem : public QGraphicsLineItem
{
public:
    enum { Type = UserType + 4 };

    TestItem(const QString &text,
      QGraphicsItem *parent = 0, QGraphicsScene *scene = 0);

    int type() const
        { return Type; }
    QRectF boundingRect() const;
    QPainterPath shape() const;
    void setColor(const QColor &color)
        { myColor = color; }
    QString message() const
        { return myMessage; }

public slots:
    void updatePosition();

protected:
    void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
               QWidget *widget = 0);

private:
	QString myMessage;
    QColor myColor;
    QPolygonF arrowHead;
};
//! [0]

#endif
