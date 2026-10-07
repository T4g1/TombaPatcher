import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QSettings

from ui.main_window import Ui_MainWindow
from ui.clut_widget import CLUTView, ClutUpdate
from ui.skin_preview import SkinPreview

from fe import (
    PatchWorker,
    PatchWorkerMode,
    ModsManagerWidget,
    LogWidget,
    PatchButtonsWidget,
)

from game_parser.image import to_16bit_color, Pixel

from common import logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker = PatchWorker()
        self.patches = []

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

        self.ui.patch_button.clicked.connect(self.on_patch)
        self.ui.extract_button.clicked.connect(self.on_extract)
        self.ui.apply_mods_button.clicked.connect(self.on_apply_mods)
        self.ui.compile_button.clicked.connect(self.on_compile)

        self.log_wdiget = LogWidget(self.ui)
        self.mods_widget = ModsManagerWidget(self.ui)
        self.button_widget = PatchButtonsWidget(self.ui, self.worker, parent=self)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            self.default_dir,
            "All Files (*);;Bin Files (*.bin);;ISO Files (*.iso)",
        )

        if file_path:
            self.ui.game_path_input.setText(file_path)

    def on_player_clut_updated(self, update: ClutUpdate):
        # address = (0x0200 * update.position) + 0x02

        clut = bytes()
        for color in update.clut:
            value = to_16bit_color(
                Pixel(color.red(), color.green(), color.blue(), color.alpha())
            )
            clut += value.to_bytes(2, byteorder="little")

        # self.add_patch_command(PatchCommand("CLUT*.GAM", address, clut))

    def on_patch(self):
        self.start_patch_worker(PatchWorkerMode.ALL)

    def on_extract(self):
        self.start_patch_worker(PatchWorkerMode.EXTRACT)

    def on_apply_mods(self):
        self.start_patch_worker(PatchWorkerMode.PATCH)

    def on_compile(self):
        self.start_patch_worker(PatchWorkerMode.COMPILE)

    def start_patch_worker(self, mode: PatchWorkerMode):
        if self.worker.running:
            logger.error("Trying to patch a file while patching is already in progress")
            return

        self.target_path = self.ui.game_path_input.text()
        self.settings.setValue("last_path", self.target_path)

        if not self.target_path or not os.path.exists(self.target_path):
            QMessageBox.warning(
                self, "Invalid File", "Please select a valid game file first."
            )
            return

        self.worker.set_mode(mode)
        self.worker.set_filepath(self.target_path)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
