import logging
from pathlib import Path
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


def bcd_to_int(bcd_byte: int) -> int:
    """Converts BCD byte into integer"""
    high_nibble = bcd_byte >> 4
    low_nibble = bcd_byte & 0x0F

    return (high_nibble * 10) + low_nibble


def read_int(data: bytes, offset: int, size: int) -> int:
    return int.from_bytes(data[offset : offset + size], byteorder="little")


def to_basepath(oldpath: Path, basepath: Path) -> Path:
    newpath = basepath / oldpath.parent.name
    newpath.mkdir(parents=True, exist_ok=True)
    return newpath / oldpath.name
