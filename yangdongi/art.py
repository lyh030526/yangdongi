from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

class PetArt(QWidget):
    """Resolution-independent mascot; redraws only on Qt paint events."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(140, 140)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = min(self.width() / 300, self.height() / 270)
        p.translate((self.width()-300*scale)/2, (self.height()-270*scale)/2)
        p.scale(scale, scale)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#e6d9c5'))
        p.drawEllipse(QRectF(53, 233, 198, 17))
        # Carry handle, soft cat ears, bucket-shaped body.
        p.setPen(QPen(QColor('#8c7562'), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRectF(61, 35, 178, 179), 0, 180*16)
        p.setPen(QPen(QColor('#715747'), 3.5))
        p.setBrush(QColor('#f6bd85'))
        for x in (79, 182):
            path = QPainterPath(QPointF(x, 102))
            path.quadTo(x-12, 44, x+9, 54)
            path.lineTo(x+44, 100)
            p.drawPath(path)
        body = QPainterPath(QPointF(60, 102))
        body.quadTo(150, 81, 240, 102)
        body.lineTo(224, 212)
        body.quadTo(220, 235, 194, 235)
        body.lineTo(105, 235)
        body.quadTo(80, 235, 77, 211)
        body.closeSubpath()
        p.setBrush(QColor('#ffd5a3'))
        p.drawPath(body)
        p.setBrush(QColor('#ffe5be'))
        p.drawRoundedRect(QRectF(53, 91, 194, 30), 14, 14)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor('#eda184'))
        p.drawEllipse(QRectF(91, 169, 28, 14))
        p.drawEllipse(QRectF(182, 169, 28, 14))
        p.setBrush(QColor('#624d41'))
        for x in (118, 176):
            p.drawEllipse(QRectF(x, 148, 8, 12))
        p.setPen(QPen(QColor('#624d41'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        mouth = QPainterPath(QPointF(138, 174))
        mouth.quadTo(150, 188, 162, 174)
        p.drawPath(mouth)
        p.setBrush(QColor('#fff0d7'))
        p.drawEllipse(QRectF(91, 220, 36, 20))
        p.drawEllipse(QRectF(177, 220, 36, 20))
        p.setPen(QPen(QColor('#a4ac87'), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(257, 136, 257, 150)
        p.drawLine(250, 143, 264, 143)
        p.end()
