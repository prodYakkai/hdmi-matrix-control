from PyQt5.QtCore import QThread, pyqtSignal


class ConnectivityChecker(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        is_connected = self.controller.check_connection()
        self.finished.emit(is_connected)
