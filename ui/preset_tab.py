from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QRadioButton,
)


class PresetTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.recall_radio = None
        self.store_radio = None
        self.init_ui()

    def init_ui(self):
        preset_layout = QVBoxLayout(self)

        preset_mode_layout = QHBoxLayout()
        preset_layout.addLayout(preset_mode_layout)

        self.recall_radio = QRadioButton("Recall")
        self.recall_radio.setChecked(True)
        preset_mode_layout.addWidget(self.recall_radio)

        self.store_radio = QRadioButton("Store")
        preset_mode_layout.addWidget(self.store_radio)

        preset_grid = QGridLayout()
        preset_layout.addLayout(preset_grid)

        for i in range(32):
            button = QPushButton(f"Preset {i + 1}")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumSize(100, 50)
            button.clicked.connect(lambda _, num=i: self.parent.on_preset_selected(num + 1))
            preset_grid.addWidget(button, i // 8, i % 8)

    def is_recall_selected(self):
        return self.recall_radio.isChecked()

    def is_store_selected(self):
        return self.store_radio.isChecked()
