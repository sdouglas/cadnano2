// Define the SIP wrapper to the testitem library.

%Module testitem 0

%Import QtCore/QtCoremod.sip

%Import QtGui/QtGuimod.sip

%If (Qt_4_2_0 -)

class TestItem : QGraphicsLineItem {

%TypeHeaderCode
#include <testitem.h>
%End

public:
    TestItem(const QString &text, QGraphicsItem *parent /TransferThis/ = 0, QGraphicsScene *scene  /TransferThis/ = 0);
    int type() const;
    QRectF boundingRect() const;
    QPainterPath shape() const;
    void setColor(const QColor &color);
    QString message() const;
    
protected:
    void paint(QPainter *painter, const QStyleOptionGraphicsItem *option,
               QWidget *widget /TransferThis/ = 0);

};

%End