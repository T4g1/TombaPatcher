import os
import sys
import logging

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QSettings

from ui.main_window import Ui_MainWindow
from ui.clut_widget import CLUTView, ClutUpdate
from ui.skin_preview import SkinPreview

from common import GuiLogger, logger
from patcher import PatchWorker, PatchCommand
from game_parser.vram import to_16bit_color, Pixel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.settings = QSettings("Tomba Club", "Tomba Patcher")
        self.default_dir = str(
            self.settings.value("last_path", os.path.expanduser("~"))
        )

        self.clut_view = CLUTView(self.ui)
        self.skin_preview = SkinPreview(self.ui)

        skin_tab_layout = self.ui.skin_tab.layout()
        assert skin_tab_layout is not None

        skin_tab_layout.addWidget(self.clut_view)
        skin_tab_layout.addWidget(self.skin_preview)

        self.clut_view.clut_updated.connect(self.skin_preview.on_clut_update)
        self.clut_view.clut_updated.connect(self.on_player_clut_updated)

        self.ui.game_path_input.setText(self.default_dir)

        self.ui.game_path_browse.clicked.connect(self.browse_file)
        self.ui.patch_button.clicked.connect(self.start_patch_process)

        log_handler = GuiLogger(self.ui.log)
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.DEBUG)

        self.worker = None
        self.patches = []

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            self.default_dir,
            "All Files (*);;Bin Files (*.bin);;ISO Files (*.iso)",
        )

        if file_path:
            self.ui.game_path_input.setText(file_path)

    def add_patch_command(self, command: PatchCommand):
        """Replace existing command or add a new one"""
        for i in range(len(self.patches)):
            if self.patches[i] == command:
                self.patches[i] = command
                return

        self.patches.append(command)

    def on_player_clut_updated(self, update: ClutUpdate):
        address = (0x0200 * update.position) + 0x02

        clut = bytes()
        for color in update.clut:
            value = to_16bit_color(
                Pixel(color.red(), color.green(), color.blue(), color.alpha())
            )
            clut += value.to_bytes(2, byteorder="little")

        self.add_patch_command(PatchCommand("CLUT*.GAM", address, clut))

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

        self.worker = PatchWorker(target_path, self.patches)

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
