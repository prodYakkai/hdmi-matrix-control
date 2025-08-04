from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QGroupBox,
    QSizePolicy,
    QLabel,
)
from PyQt5.QtCore import Qt


class IoTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.input_buttons = []
        self.output_buttons = []
        self.init_ui()

    def init_ui(self):
        io_layout = QVBoxLayout(self)

        # Input Panel
        input_group = QGroupBox("Inputs")
        input_layout = QGridLayout()
        input_group.setLayout(input_layout)
        io_layout.addWidget(input_group)

        for i in range(16):
            button = QPushButton()
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumSize(100, 50)
            button.clicked.connect(lambda _, num=i: self.parent.on_input_selected(num + 1))
            button.setContextMenuPolicy(Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, num=i: self.parent.on_input_context_menu(pos, num + 1)
            )
            self.input_buttons.append(button)
            input_layout.addWidget(button, i // 8, i % 8)

        # Output Panel
        output_group = QGroupBox("Outputs")
        output_layout = QGridLayout()
        output_group.setLayout(output_layout)
        io_layout.addWidget(output_group)

        for i in range(16):
            button = QPushButton()
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumSize(100, 50)
            button.clicked.connect(lambda _, num=i: self.parent.on_output_selected(num + 1))
            button.setContextMenuPolicy(Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, num=i: self.parent.on_output_context_menu(pos, num + 1)
            )
            self.output_buttons.append(button)
            output_layout.addWidget(button, i // 8, i % 8)

        # Status Bar
        status_bar_layout = QHBoxLayout()
        io_layout.addLayout(status_bar_layout)

        one_to_one_button = QPushButton("1/1 Mapped")
        one_to_one_button.clicked.connect(self.parent.map_one_to_one)
        status_bar_layout.addWidget(one_to_one_button)

        status_bar_layout.addStretch(1)

        self.connection_status_label = QLabel("Status: Unknown")
        status_bar_layout.addWidget(self.connection_status_label)

        self.retry_button = QPushButton("Retry")
        self.retry_button.clicked.connect(self.parent.check_connectivity)
        self.retry_button.hide()
        status_bar_layout.addWidget(self.retry_button)

        self.last_command_label = QLabel("Last Command: None")
        status_bar_layout.addWidget(self.last_command_label)

        self.ip_address_label = QLabel(f"IP: {self.parent.settings['ip']}")
        status_bar_layout.addWidget(self.ip_address_label)

    def update_button_names(self, input_names, output_names, output_mappings):
        for i, button in enumerate(self.input_buttons):
            name = input_names.get(str(i + 1))
            if name:
                button.setText(f"{name}\n(Input {i + 1})")
            else:
                button.setText(f"Input {i + 1}")

        for i, button in enumerate(self.output_buttons):
            output_num = i + 1
            name = output_names.get(str(output_num))
            
            base_text = f"{name}\n(Output {output_num})" if name else f"Output {output_num}"

            if output_num in output_mappings:
                input_num_for_output = output_mappings[output_num]
                base_text += f"\n<-- Input {input_num_for_output}"
            
            button.setText(base_text)

    def update_output_button_styles(self, output_mappings, selected_input, clicked_output_num=None):
        for i, button in enumerate(self.output_buttons):
            output_num = i + 1
            if output_num == clicked_output_num:
                button.setStyleSheet("background-color: #ebcb8b;") # Yellow for clicked output
            elif output_mappings.get(output_num) == selected_input:
                button.setStyleSheet("background-color: #88c0d0;") # Light blue for connected outputs
            else:
                button.setStyleSheet("")

    def set_connection_status(self, text, color, show_retry):
        self.connection_status_label.setText(text)
        self.connection_status_label.setStyleSheet(color)
        self.retry_button.setVisible(show_retry)

    def set_last_command_text(self, text):
        self.last_command_label.setText(f"Last Command: {text}")

    def set_ip_address_label(self, ip):
        self.ip_address_label.setText(f"IP: {ip}")