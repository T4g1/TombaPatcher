from PySide6.QtGui import QColor

from ui.main_window import Ui_MainWindow
from ui.clut_widget import ClutUpdate
from ui.image import ImageView

ZOOM_LEVEL = 15
BOTTOM_THRESHOLD = 22

DEFAULT_CLUT = [
    QColor.fromRgbF(0.015686, 0.015686, 0.015686, 1.000000),
    QColor.fromRgbF(0.188235, 0.047059, 0.031373, 1.000000),
    QColor.fromRgbF(0.250980, 0.125490, 0.078431, 1.000000),
    QColor.fromRgbF(0.486275, 0.188235, 0.109804, 1.000000),
    QColor.fromRgbF(0.627451, 0.235294, 0.141176, 1.000000),
    QColor.fromRgbF(0.721569, 0.345098, 0.156863, 1.000000),
    QColor.fromRgbF(0.862745, 0.533333, 0.203922, 1.000000),
    QColor.fromRgbF(0.956863, 0.768627, 0.439216, 1.000000),
    QColor.fromRgbF(0.015686, 0.109804, 0.000000, 1.000000),
    QColor.fromRgbF(0.015686, 0.188235, 0.000000, 1.000000),
    QColor.fromRgbF(0.047059, 0.250980, 0.000000, 1.000000),
    QColor.fromRgbF(0.094118, 0.392157, 0.000000, 1.000000),
    QColor.fromRgbF(0.125490, 0.674510, 0.000000, 1.000000),
    QColor.fromRgbF(0.674510, 0.674510, 0.674510, 1.000000),
    QColor.fromRgbF(0.956863, 0.956863, 0.956863, 1.000000),
]


class SkinPreview(ImageView):
    top_clut: list[QColor] = DEFAULT_CLUT
    bottom_clut: list[QColor] = DEFAULT_CLUT

    indexed_data: list[list[int]] = []

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(ui, "assets/player_preview.png", parent=parent)

        self.init_indexed_data()

    def is_top(self, y: int) -> bool:
        return y > BOTTOM_THRESHOLD

    def get_clut(self, y: int) -> list[QColor]:
        if self.is_top(y):
            return self.top_clut
        else:
            return self.bottom_clut

    def set_clut(self, clut: list[QColor], is_top: bool = True):
        """Set the clut to preview"""
        if is_top:
            self.top_clut = clut
        else:
            self.bottom_clut = clut

        if not self.indexed_data:
            self.init_indexed_data()

        self.build_preview()

    def get_clut_color(self, y: int, index: int) -> QColor:
        return self.get_clut(y)[index]

    def get_clut_index(self, y: int, color: QColor) -> int:
        """Returns the index of the given color
        -1 if no color matches
        """
        clut = self.get_clut(y)

        for index in range(len(clut)):
            if color == clut[index]:
                return index

        return -1

    def init_indexed_data(self):
        """Initialize the indexed image data from the given CLUT"""
        width = self.image.width()
        height = self.image.height()

        for x in range(width):
            self.indexed_data.append([])

            for y in range(height):
                color = self.get_pixel(x, y)
                clut_index = self.get_clut_index(y, color)
                self.indexed_data[x].append(clut_index)

    def build_preview(self):
        """Build preview from the indexed data and the clut"""
        width = self.image.width()
        height = self.image.height()

        for x in range(width):
            for y in range(height):
                index = self.indexed_data[x][y]
                if index < 0:
                    color = QColor.fromRgbF(0.0, 0.0, 0.0, 0.0)
                else:
                    color = self.get_clut_color(y, index)

                self.set_pixel(x, y, color)

        self.refresh()

    def on_clut_update(self, update: ClutUpdate):
        if update.position == 8:
            self.set_clut(update.clut, is_top=False)
            self.set_clut(update.clut, is_top=True)
        else:
            self.set_clut(update.clut, is_top=update.position % 2 == 1)
