import logging
from PySide6 import QtWidgets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class GuiLogger(logging.Handler):
    """Interface between python logging and QT"""

    display: QtWidgets.QTextEdit

    def __init__(self, display: QtWidgets.QTextEdit):
        super().__init__()

        self.display = display

    def emit(self, record):
        self.display.textCursor().insertText(f"{self.format(record)}\n")
