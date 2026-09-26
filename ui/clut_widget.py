from dataclasses import dataclass

from PySide6.QtWidgets import QColorDialog
from PySide6.QtCore import Signal, QPointF
from PySide6.QtGui import QColor

from ui.main_window import Ui_MainWindow
from ui.image import ImageView

ZOOM_LEVEL = 15


@dataclass
class ClutUpdate:
    position: int
    clut: list[QColor]


@dataclass
class ColorPicked:
    x: int
    y: int
    color: QColor


class CLUTView(ImageView):
    clut_updated = Signal(ClutUpdate)
    color_picked = Signal(ColorPicked)

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(ui, "assets/player_clut.png", parent=parent)

        self.pixmap_item.mouse_click.connect(self.on_mouse_click)
        self.color_picked.connect(self.on_color_picked)

    def on_mouse_click(self, position: QPointF):
        x = int(position.x())
        y = int(position.y())

        initial = self.get_pixel(x, y)
        self.open_color_picker(x, y, initial)

    def on_color_picked(self, picked: ColorPicked):
        self.set_pixel(picked.x, picked.y, picked.color)
        self.refresh()

        clut = self.get_clut(picked.y)
        self.clut_updated.emit(ClutUpdate(picked.y, clut))

    def get_clut(self, index: int) -> list[QColor]:
        """Creates an array from the clut at the given position"""
        clut = []
        for x in range(self.image.width()):
            clut.append(self.get_pixel(x, index))
        return clut

    def open_color_picker(self, x: int, y: int, initial: QColor):
        color = QColorDialog.getColor(
            initial=initial, parent=self, title="Select Color"
        )

        if color.isValid():
            self.color_picked.emit(ColorPicked(x, y, color))
