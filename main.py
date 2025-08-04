import sys
import json
import shutil
from pathlib import Path
from PyQt5.QtWidgets import(
    QApplication,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QMenu,
    QTabWidget,
    QMenuBar,
    QFileDialog,
)
from matrix_controller import MatrixController
from ui.io_tab import IoTab
from ui.preset_tab import PresetTab
from ui.settings_tab import SettingsTab
from ui.dialogs import RenameDialog
from utils import ConnectivityChecker
from config import CONFIG_FILE, NAMES_FILE
from config_manager import ConfigManager

class HdmiMatrixApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager(CONFIG_FILE, NAMES_FILE)
        self.settings = self.config_manager.settings
        self.names = self.config_manager.names
        self.output_mappings = self.config_manager.output_mappings

        self.controller = MatrixController(
            ip_address=self.settings["ip"], port=self.settings["port"]
        )
        self.setWindowTitle("HDMI Matrix Control - by prodYakkai >:3")
        self.selected_input = None
        self.init_ui()
        self.set_theme(self.settings["theme"])
        self.update_button_names()
        self.check_connectivity()

    def set_theme(self, theme_name):
        stylesheet = self.config_manager.get_theme_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        self.settings["theme"] = theme_name
        self.config_manager.save_settings(
            self.settings["ip"],
            self.settings["port"],
            self.settings["confirm_before_switch"],
            self.output_mappings,
            theme=theme_name
        )

    def save_settings(self):
        ip = self.settings_tab.get_ip_address()
        port = self.settings_tab.get_port()
        confirm_before_switch = self.settings_tab.get_confirm_before_switch_state()
        self.config_manager.save_settings(ip, port, confirm_before_switch, self.output_mappings)
        self.settings = self.config_manager.settings # Update local settings reference

        self.controller.ip_address = self.settings["ip"]
        self.controller.port = self.settings["port"]
        self.io_tab.set_ip_address_label(self.settings["ip"])
        print(f"Settings saved: {self.settings['ip']}:{self.settings['port']}")
        self.check_connectivity()

    def save_names(self):
        self.config_manager.save_names()

    def update_button_names(self):
        preset = self.names.get("current_preset", "1")
        input_names = self.names.get("presets", {}).get(preset, {}).get("inputs", {})
        output_names = self.names.get("presets", {}).get(preset, {}).get("outputs", {})
        self.io_tab.update_button_names(input_names, output_names, self.output_mappings)

    

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Menu Bar
        menu_bar = QMenuBar(self)
        main_layout.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")

        save_action = file_menu.addAction("Save I/O Map")
        save_action.triggered.connect(self.save_io_map_to_file)

        load_action = file_menu.addAction("Load I/O Map")
        load_action.triggered.connect(self.load_io_map_from_file)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        self.io_tab = IoTab(self)
        tabs.addTab(self.io_tab, "I/O Routing")
        

        self.preset_tab = PresetTab(self)
        tabs.addTab(self.preset_tab, "Presets")

        self.settings_tab = SettingsTab(self)
        tabs.addTab(self.settings_tab, "Settings")

    def check_connectivity(self):
        self.io_tab.set_connection_status("Status: Checking...", "", False)
        self.connectivity_checker = ConnectivityChecker(self.controller)
        self.connectivity_checker.finished.connect(self.on_connectivity_checked)
        self.connectivity_checker.start()

    def on_connectivity_checked(self, is_connected):
        if is_connected:
            self.io_tab.set_connection_status("Status: Connected", "color: green", False)
        else:
            self.io_tab.set_connection_status("Status: Disconnected", "color: red", True)
            QMessageBox.warning(
                self, "Connection Failed", "Could not connect to the matrix."
            )

    def on_input_selected(self, input_num):
        self.selected_input = input_num
        # Clear previous input highlight
        for i, button in enumerate(self.io_tab.input_buttons):
            if i + 1 == input_num:
                button.setStyleSheet("background-color: #a3be8c")  # Green for selected input
            else:
                button.setStyleSheet("")
        
        # Update output button styles based on the newly selected input
        self._update_output_button_styles()

    def _update_output_button_styles(self, clicked_output_num=None):
        self.io_tab.update_output_button_styles(self.output_mappings, self.selected_input, clicked_output_num)

    def on_output_selected(self, output_num):
        if self.selected_input is None:
            print("Please select an input first.")
            return

        def perform_route():
            command = self.controller.route(self.selected_input, output_num)
            self.io_tab.set_last_command_text(command)
            self.output_mappings[output_num] = self.selected_input
            self.update_button_names()
            self._update_output_button_styles(clicked_output_num=output_num)
            self.save_settings()

        if self.settings["confirm_before_switch"]:
            if (
                output_num in self.output_mappings
                and self.output_mappings[output_num] != self.selected_input
            ):
                current_input = self.output_mappings[output_num]
                reply = QMessageBox.question(
                    self,
                    "Confirm Override",
                    f"Output {output_num} is already connected to Input {current_input}. "
                    f"Do you want to switch it to Input {self.selected_input}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    perform_route()
            else:
                reply = QMessageBox.question(
                    self,
                    "Confirm Switch",
                    f"Are you sure you want to route Input {self.selected_input} to Output {output_num}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    perform_route()
        else: # No confirmation needed
            perform_route()

    def on_input_context_menu(self, pos, input_num):
        context_menu = QMenu(self)
        patch_all_action = context_menu.addAction("Patch to all outputs")
        rename_action = context_menu.addAction("Rename")
        action = context_menu.exec_(self.io_tab.input_buttons[input_num - 1].mapToGlobal(pos))
        if action == patch_all_action:
            self.patch_all_outputs(input_num)
        elif action == rename_action:
            self.rename_input(input_num)

    def on_output_context_menu(self, pos, output_num):
        context_menu = QMenu(self)
        rename_action = context_menu.addAction("Rename")
        trace_action = context_menu.addAction("Trace")
        action = context_menu.exec_(self.io_tab.output_buttons[output_num - 1].mapToGlobal(pos))
        if action == rename_action:
            self.rename_output(output_num)
        elif action == trace_action:
            self.trace_output_to_input(output_num)

    def rename_input(self, input_num):
        preset = self.names["current_preset"]
        current_name = self.names["presets"].get(preset, {}).get("inputs", {}).get(str(input_num), "")
        dialog = RenameDialog(self, current_name, device_type="input")
        if dialog.exec_():
            new_name = dialog.get_name()
            if preset not in self.names["presets"]:
                self.names["presets"][preset] = {"inputs": {}, "outputs": {}}
            self.names["presets"][preset][str(input_num)] = new_name
            self.save_names()
            self.update_button_names()

    def rename_output(self, output_num):
        preset = self.names["current_preset"]
        current_name = self.names["presets"].get(preset, {}).get("outputs", {}).get(str(output_num), "")
        dialog = RenameDialog(self, current_name, device_type="output")
        if dialog.exec_():
            new_name = dialog.get_name()
            if preset not in self.names["presets"]:
                self.names["presets"][preset] = {"inputs": {}, "outputs": {}}
            self.names["presets"][preset]["outputs"][str(output_num)] = new_name
            self.save_names()
            self.update_button_names()

    def patch_all_outputs(self, input_num):
        if self.settings["confirm_before_switch"]:
            reply = QMessageBox.question(
                self,
                "Confirm Patch All",
                f"Are you sure you want to patch Input {input_num} to all outputs?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        self.on_input_selected(input_num)
        command = f"Patching Input {input_num} to all outputs"
        self.controller.route_all(input_num)
        for i in range(16):
            output_num = i + 1
            self.output_mappings[output_num] = input_num
        self.io_tab.set_last_command_text(command)
        self.update_button_names()

    def map_one_to_one(self):
        if self.settings["confirm_before_switch"]:
            reply = QMessageBox.question(
                self,
                "Confirm 1/1 Mapping",
                "Are you sure you want to map all inputs to their corresponding outputs?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        command = "1/1 mapping"
        self.controller.route_1_to_1()
        for i in range(16):
            input_num = i + 1
            output_num = i + 1
            self.output_mappings[output_num] = input_num
        self.io_tab.set_last_command_text(command)
        self.update_button_names()

    def on_preset_selected(self, preset_num):
        if self.preset_tab.is_recall_selected():
            if self.settings["confirm_before_switch"]:
                reply = QMessageBox.question(
                    self,
                    "Confirm Recall",
                    f"Are you sure you want to recall Preset {preset_num}? This will override the current routing.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
            command = self.controller.recall_preset(preset_num)
            self.io_tab.set_last_command_text(command)
            self.names["current_preset"] = str(preset_num)
            self.save_names()
            self.update_button_names()
        elif self.preset_tab.is_store_selected():
            if self.settings["confirm_before_switch"]:
                reply = QMessageBox.question(
                    self,
                    "Confirm Store",
                    f"Are you sure you want to store the current routing to Preset {preset_num}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
            command = self.controller.store_preset(preset_num)
            self.io_tab.set_last_command_text(command)

    def sync_state_to_matrix(self):
        if self.settings["confirm_before_switch"]:
            reply = QMessageBox.question(
                self,
                "Confirm Sync",
                "Are you sure you want to sync the current software state to the matrix? This will send all routing commands.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        self.io_tab.set_last_command_text("Syncing state...")
        for output_num, input_num in self.output_mappings.items():
            command = self.controller.route(input_num, output_num)
            self.io_tab.set_last_command_text(command)
        QMessageBox.information(self, "Sync Complete", "Current state synced to matrix.")

    def trace_output_to_input(self, output_num):
        if output_num in self.output_mappings:
            input_num = self.output_mappings[output_num]
            self.on_input_selected(input_num)
            self.io_tab.parentWidget().setCurrentWidget(self.io_tab) # Switch to I/O Routing tab
        else:
            QMessageBox.information(self, "Trace", f"Output {output_num} is not currently routed to any input.")

    def save_io_map_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save I/O Map", "iomap.json", "JSON Files (*.json)")
        if file_path:
            try:
                # Get current output names for the active preset
                current_preset = self.names["current_preset"]
                output_names_for_preset = self.names["presets"].get(current_preset, {}).get("outputs", {})

                data_to_save = {
                    "mappings": self.output_mappings,
                    "output_names": output_names_for_preset
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, indent=4)
                QMessageBox.information(self, "Save Complete", "I/O map and output names saved successfully.")
                
                if self.settings["confirm_before_switch"]:
                    reply = QMessageBox.question(
                        self,
                        "Sync to Matrix",
                        "Do you want to sync the saved I/O map to the matrix?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        self.sync_state_to_matrix()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save I/O map: {e}")

    def load_io_map_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load I/O Map", "iomap.json", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                
                # Validate loaded data
                if not isinstance(loaded_data, dict) or \
                   "mappings" not in loaded_data or \
                   "output_names" not in loaded_data or \
                   not isinstance(loaded_data["mappings"], dict) or \
                   not isinstance(loaded_data["output_names"], dict):
                    raise ValueError("Invalid I/O map file format.")

                # Load mappings
                self.output_mappings = {int(k): v for k, v in loaded_data["mappings"].items()}

                # Load output names for the current preset
                current_preset = self.names["current_preset"]
                if current_preset not in self.names["presets"]:
                    self.names["presets"][current_preset] = {"inputs": {}, "outputs": {}}
                self.names["presets"][current_preset]["outputs"] = loaded_data["output_names"]
                
                self.save_names() # Save the updated names to names.json

                self.update_button_names()
                self._update_output_button_styles()
                QMessageBox.information(self, "Load Complete", "I/O map and output names loaded successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load I/O map: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = HdmiMatrixApp()
    ex.show()
    sys.exit(app.exec_())