from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QImage

from ui.main_window import Ui_MainWindow
from ui.pixmap_item import PixmapItem

DEFAULT_ZOOM_LEVEL = 15


class ImageView(QGraphicsView):
    ui: Ui_MainWindow

    image: QImage
    pixmap: QPixmap
    pixmap_item: PixmapItem

    def __init__(
        self,
        ui: Ui_MainWindow,
        image_path: str,
        zoom_level: int = DEFAULT_ZOOM_LEVEL,
        parent=None,
    ):
        super().__init__(parent)

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self.pixmap = QPixmap(image_path)
        assert not self.pixmap.isNull()

        self.image = self.pixmap.toImage()

        self.pixmap_item = PixmapItem(self.pixmap)
        self.pixmap_item.setTransformationMode(Qt.TransformationMode.FastTransformation)
        self.pixmap_item.setScale(zoom_level)
        scene.addItem(self.pixmap_item)

        scaled_width = self.pixmap.width() * zoom_level
        scaled_height = self.pixmap.height() * zoom_level

        scene.setSceneRect(0, 0, scaled_width, scaled_height)
        self.setFixedSize(scaled_width, scaled_height)

        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def refresh(self):
        """Refresh the image displayed"""
        self.pixmap = QPixmap.fromImage(self.image)
        self.pixmap_item.setPixmap(self.pixmap)

    def get_pixel(self, x: int, y: int) -> QColor:
        return self.image.pixelColor(x, y)

    def set_pixel(self, x: int, y: int, color: QColor):
        """Set the color of a particular pixel at given coordinates"""
        self.image.setPixelColor(x, y, color)
