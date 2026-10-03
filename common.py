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

PNG_SUFFIX = ".PNG"


PATTERN_TO_SUFFIX: dict[int, str] = {
    # VRAM Shard
    0x10FF: ".GRPX",
    0x11FF: ".GRPX",
    0x1080: ".GRPX",
    # 3D Models
    0x5080: ".PAK",
    0x50FF: ".PAK",
    0x51FF: ".PAK",
    0x52FF: ".PAK",
    0x53FF: ".PAK",
    0x54FF: ".PAK",
    0x55FF: ".PAK",
    # Tomba! or Red Kokka sprites
    0x6080: ".RLE.PAK",
    0x60FF: ".RLE.PAK",
    0x6280: ".RLE.PAK",
    0x62FF: ".RLE.PAK",
    0x63FF: ".TIM.GAM.PAK",
    # Text/Dialogs
    0xD0FF: ".WFM",
    0xD1FF: ".WFM",  # Events
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


def is_matching(path: Path, matching: list[str]):
    token = to_matching_token(path)
    return len(matching) == 0 or token in matching


def to_matching_token(path: Path):
    return f"{path.parent.name}/{path.name.split(".")[0]}"
