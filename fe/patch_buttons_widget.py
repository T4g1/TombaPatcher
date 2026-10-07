from PySide6.QtWidgets import QWidget, QMessageBox

from ui.main_window import Ui_MainWindow

from fe import PatchWorker

from common import logger


class PatchButtonsWidget(QWidget):
    ui: Ui_MainWindow
    patch_worker: PatchWorker

    def __init__(self, ui: Ui_MainWindow, patch_worker: PatchWorker, parent=None):
        super().__init__(parent)

        self.ui = ui
        self.patch_worker = patch_worker

        self.ui.advanced_button.clicked.connect(self.toggle_advanced)

        self.patch_worker.status_changed.connect(self.on_process_running)
        self.patch_worker.finished.connect(self.on_process_finished)

        self.ui.extract_button.hide()
        self.ui.apply_mods_button.hide()
        self.ui.compile_button.hide()

    def toggle_advanced(self):
        advanced_shown = self.ui.extract_button.isVisible()

        if advanced_shown:
            self.ui.extract_button.hide()
            self.ui.apply_mods_button.hide()
            self.ui.compile_button.hide()

        else:
            self.ui.extract_button.show()
            self.ui.apply_mods_button.show()
            self.ui.compile_button.show()

    def on_process_running(self, message: str):
        self.ui.game_path_browse.setEnabled(False)
        self.ui.patch_button.setEnabled(False)
        self.ui.extract_button.setEnabled(False)
        self.ui.apply_mods_button.setEnabled(False)
        self.ui.compile_button.setEnabled(False)

        self.ui.statusbar.showMessage(message)

        logger.info(message)

    def on_process_finished(self, success: bool, message: str):
        self.ui.game_path_browse.setEnabled(True)
        self.ui.patch_button.setEnabled(True)
        self.ui.extract_button.setEnabled(True)
        self.ui.apply_mods_button.setEnabled(True)
        self.ui.compile_button.setEnabled(True)

        self.ui.statusbar.showMessage(message)

        logger.info(message)

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Failed", message)
