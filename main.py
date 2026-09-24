import os
import sys
import logging

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QSettings

from ui.main_window import Ui_MainWindow

from common import GuiLogger, logger
from patcher import PatchWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.settings = QSettings("Tomba Club", "Tomba Patcher")
        self.default_dir = str(
            self.settings.value("last_path", os.path.expanduser("~"))
        )

        self.ui.game_path_input.setText(self.default_dir)

        self.ui.game_path_browse.clicked.connect(self.browse_file)
        self.ui.patch_button.clicked.connect(self.start_patch_process)

        log_handler = GuiLogger(self.ui.log)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        self.worker = None

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            self.default_dir,
            "All Files (*);;Bin Files (*.bin);;ISO Files (*.iso)",
        )

        if file_path:
            self.ui.game_path_input.setText(file_path)

    def start_patch_process(self):
        if self.worker is not None:
            logger.error("Trying to patch a file while patching is already in progress")
            return

        target_path = self.ui.game_path_input.text()
        self.settings.setValue("last_path", target_path)

        if not target_path or not os.path.exists(target_path):
            QMessageBox.warning(
                self, "Invalid File", "Please select a valid game file first."
            )
            return

        self.ui.game_path_browse.setEnabled(False)
        self.ui.patch_button.setEnabled(False)

        self.worker = PatchWorker(target_path)

        self.worker.status_changed.connect(self.update_status)
        self.worker.finished.connect(self.on_patch_complete)

        self.worker.start()

    def update_status(self, message):
        logger.info(message)
        self.ui.statusbar.showMessage(message)

    def on_patch_complete(self, success, message):
        self.ui.game_path_browse.setEnabled(True)
        self.ui.patch_button.setEnabled(True)
        self.ui.statusbar.showMessage(message)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Failed", message)

        self.worker = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
