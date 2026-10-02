import logging
from pathlib import Path
from PySide6 import QtWidgets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

OUTPUT_PATH = Path("output")
MODS_PATH = Path("mods")

ISO_PATH = OUTPUT_PATH / "iso"
LD_PATH = OUTPUT_PATH / "ld"
GAM_PATH = OUTPUT_PATH / "gam"
PACKED_PATH = OUTPUT_PATH / "packed"
RLE_PATH = OUTPUT_PATH / "rle"
TIM_PATH = OUTPUT_PATH / "tim"
IMG_PATH = OUTPUT_PATH / "img"

XML_NAME = "tomba.xml"
XML_PATH = OUTPUT_PATH / "tomba.xml"
ENTRY_PATH = ISO_PATH / "SCUS_942.36"
SYS_PATH = ISO_PATH / "SYS"


PATTERN_TO_SUFFIX: dict[int, str] = {
    0xD1FF: ".WFM",
    0x60FF: ".RLE.PAK",
    0x62FF: ".RLE.PAK",
    0x5080: ".PAK",
}


def all(pattern: str):
    return "*" + pattern


def get_suffix_from_type(file_type: int):
    return PATTERN_TO_SUFFIX.get(file_type, "")


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


def rglob(path: Path, patterns: list[str]) -> list[Path]:
    """Multi pattern rglob"""
    return [file for pattern in patterns for file in path.rglob(pattern)]
