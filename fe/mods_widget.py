from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QListWidgetItem,
)

from ui.main_window import Ui_MainWindow

from patcher.mods import ModsManager

from common import (
    MODS_PATH,
)


class ModsManagerWidget(QWidget):
    ui: Ui_MainWindow

    def __init__(self, ui: Ui_MainWindow, parent=None):
        super().__init__(parent)

        self.ui = ui
        self.ui.refresh_mod_list.clicked.connect(self.load_mods)

        self.load_mods()

    def load_mods(self):
        self.ui.mod_list.clear()

        manager = ModsManager(MODS_PATH)
        for mod in manager.mods:
            check_state = Qt.CheckState.Unchecked
            if mod._is_active:
                check_state = Qt.CheckState.Checked

            item = QListWidgetItem(mod._code)
            item.setCheckState(check_state)

            self.ui.mod_list.addItem(item)
