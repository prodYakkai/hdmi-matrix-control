from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
)


class RenameDialog(QDialog):
    def __init__(self, parent=None, current_name="", device_type=""):
        super().__init__(parent)
        self.setWindowTitle(f"Rename {device_type.capitalize()}")
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        
        INPUT_NAMES = [
            "Computer", "Laptop", "Camera", "Game Console", "PTZ",  "Server", 
            "Telepresence", "ATEM M/E", "Multiview"
        ]
        OUTPUT_NAMES = [
            "Projector", "TV", "Monitor", "LED Wall", "Conference Room",
            "Auditorium", "Classroom", "Recorder", "Broadcast", "Overflow",
            "Telepresence Return", 
        ]

        if device_type == "input":
            self.list_widget.addItems(INPUT_NAMES)
        elif device_type == "output":
            self.list_widget.addItems(OUTPUT_NAMES)
        
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        self.name_input = QLineEdit(current_name)
        layout.addWidget(self.name_input)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

    def on_item_clicked(self, item):
        self.name_input.setText(item.text())

    def get_name(self):
        return self.name_input.text()
