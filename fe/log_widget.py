import datetime
import logging
from pathlib import Path

from PySide6.QtWidgets import QWidget

from ui.main_window import Ui_MainWindow

from common import GuiLogger


class LogWidget(QWidget):
    ui: Ui_MainWindow

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(parent)

        self.ui = ui

        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = log_dir / f"patcher_{timestamp}.log"

        root_logger = logging.getLogger()

        log_handler = GuiLogger(self.ui.log)
        root_logger.addHandler(log_handler)
        root_logger.setLevel(logging.DEBUG)

        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        root_logger.addHandler(file_handler)
