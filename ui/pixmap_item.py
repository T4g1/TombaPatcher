from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal, QObject, QPointF


class PixmapItem(QObject, QGraphicsPixmapItem):
    mouse_moved = Signal(QPointF)
    mouse_click = Signal(QPointF)

    def __init__(self, parent=None):
        QObject.__init__(self)
        QGraphicsPixmapItem.__init__(self, parent)

        self.setAcceptHoverEvents(True)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverMoveEvent(event)

        self.mouse_moved.emit(event.pos())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        super().mousePressEvent(event)

        if event.button() is Qt.MouseButton.LeftButton:
            self.mouse_click.emit(event.pos())
