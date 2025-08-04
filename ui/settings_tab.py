from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QCheckBox,
)
from PyQt5.QtCore import Qt


class SettingsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ip_input = None
        self.port_input = None
        self.confirm_before_switch_checkbox = None
        self.theme_checkbox = None
        self.init_ui()

    def init_ui(self):
        settings_layout = QVBoxLayout(self)
        settings_form_layout = QGridLayout()
        settings_layout.addLayout(settings_form_layout)

        settings_form_layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.ip_input = QLineEdit(self.parent.settings["ip"])
        settings_form_layout.addWidget(self.ip_input, 0, 1)

        settings_form_layout.addWidget(QLabel("Port:"), 1, 0)
        self.port_input = QLineEdit(str(self.parent.settings["port"]))
        settings_form_layout.addWidget(self.port_input, 1, 1)

        # Theme selection
        self.theme_checkbox = QCheckBox("Enable Dark Theme")
        self.theme_checkbox.setChecked(self.parent.settings.get("theme", "light") == "dark")
        self.theme_checkbox.stateChanged.connect(self.toggle_theme)
        settings_layout.addWidget(self.theme_checkbox)

        # Confirm Before Switch checkbox
        self.confirm_before_switch_checkbox = QCheckBox("Confirm Before Switch")
        self.confirm_before_switch_checkbox.setChecked(self.parent.settings.get("confirm_before_switch", True))
        settings_layout.addWidget(self.confirm_before_switch_checkbox)

        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.parent.save_settings)
        settings_layout.addWidget(save_button)

        sync_button = QPushButton("Sync Current State to Matrix")
        sync_button.clicked.connect(self.parent.sync_state_to_matrix)
        settings_layout.addWidget(sync_button)

        settings_layout.addStretch(1)

    def toggle_theme(self, state):
        if state == Qt.Checked:
            self.parent.set_theme("dark")
        else:
            self.parent.set_theme("light")

    def get_ip_address(self):
        return self.ip_input.text()

    def get_port(self):
        return int(self.port_input.text())

    def get_confirm_before_switch_state(self):
        return self.confirm_before_switch_checkbox.isChecked()
