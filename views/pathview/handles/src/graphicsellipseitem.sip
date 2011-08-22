// Define the SIP wrapper to the videowidget library.

%Module graphicsellipseitem 0

%Import QtCore/QtCoremod.sip

%Import QtGui/QtGuimod.sip

%If (Qt_4_2_0 -)

class GraphicsEllipseItem : QGraphicsEllipseItem {

%TypeHeaderCode
#include <graphicsellipseitem.h>
%End

public:
    GraphicsEllipseItem (QGraphicsItem  * parent /TransferThis/ = 0);
    virtual ~GraphicsEllipseItem();
    virtual void paint(QPainter *, const QStyleOptionGraphicsItem *, QWidget *widget = 0) = 0;

};

%End
