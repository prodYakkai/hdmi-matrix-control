# Gemini Project Documentation

This document provides a comprehensive overview of the HDMI Matrix Control application for future AI agents. It details the project structure, the purpose and logic of each file, and the overall architecture of the application.

## Project Overview

The HDMI Matrix Control application is a Python-based graphical user interface (GUI) for controlling an HDMI matrix switcher. The application is built using PyQt5 and is designed to be cross-platform.

### Core Features

*   **I/O Routing:** Allows users to route any input to any output.
*   **Presets:** Save and recall up to 32 routing presets.
*   **Custom Naming:** Rename inputs and outputs for easier identification.
*   **Settings:** Configure the IP address and port of the HDMI matrix, toggle dark theme, and set confirm before switch.
*   **Connectivity Check:** Automatically checks for a connection to the matrix and provides feedback to the user.
*   **Save/Load I/O Map:** Save and load the current input/output routing configuration, including custom output names.

## Project Structure

```
hdmi-matrix-ctrl/
├── config.py
├── main.py
├── matrix_controller.py
├── HDMI_Matrix_Control.spec
├── styles/
│   └── dark_theme.qss
├── ui/
│   ├── dialogs.py
│   ├── io_tab.py
│   ├── preset_tab.py
│   └── settings_tab.py
└── utils.py
```

### File Descriptions

*   **`main.py`**: The main entry point of the application. It contains the `HdmiMatrixApp` class, which is the main window of the application. This class is responsible for initializing the UI, handling events, and managing the overall state of the application.

*   **`matrix_controller.py`**: This file contains the `MatrixController` class, which is responsible for all communication with the HDMI matrix. It handles the construction and sending of UDP packets to control the matrix.

*   **`config.py`**: This module is responsible for managing the application's configuration. It determines the appropriate user-specific directory for storing configuration files and provides the paths to these files. It also handles the creation of the configuration directory if it doesn't exist.

*   **`utils.py`**: This file contains utility classes used by the application. Currently, it contains the `ConnectivityChecker` class, which is a `QThread` that checks for a connection to the matrix in the background to avoid freezing the UI.

*   **`HDMI_Matrix_Control.spec`**: This is the PyInstaller spec file used to bundle the application into a standalone executable.

*   **`styles/`**: This directory contains QSS (Qt Style Sheets) files for styling the application.

    *   **`dark_theme.qss`**: Defines the dark theme styles for the application.

*   **`ui/`**: This directory contains all the UI-related files.

    *   **`io_tab.py`**: This file contains the `IoTab` class, which is the UI for the "I/O Routing" tab. It contains the input and output buttons, as well as the status bar.

    *   **`preset_tab.py`**: This file contains the `PresetTab` class, which is the UI for the "Presets" tab. It contains the preset buttons and the "Recall/Store" radio buttons.

    *   **`settings_tab.py`**: This file contains the `SettingsTab` class, which is the UI for the "Settings" tab. It contains the input fields for the IP address and port, as well as the "Save Settings" button.

    *   **`dialogs.py`**: This file contains the `RenameDialog` class, which is a custom dialog that allows users to rename inputs and outputs.

### Data Storage

*   **`config.json`**: This file stores the IP address, port, theme, confirm before switch setting, and output mappings of the HDMI matrix. It is located in the user-specific configuration directory.

*   **`names.json`**: This file stores the custom names for the inputs and outputs, organized by preset. It is also located in the user-specific configuration directory.

## Application Logic

### Main Application (`HdmiMatrixApp`)

The `HdmiMatrixApp` class is the core of the application. It is responsible for:

*   **Initialization:** Loading the settings and names from the configuration files, initializing the `MatrixController`, and setting up the UI.
*   **Event Handling:** Handling button clicks, context menu events, and other user interactions.
*   **State Management:** Keeping track of the currently selected input, the current output mappings, and the current preset.
*   **UI Updates:** Updating the button labels and other UI elements to reflect the current state of the application.

### UI Tabs

The UI is organized into three tabs:

*   **I/O Routing:** This is the main tab for controlling the matrix. It displays the input and output buttons, and allows users to route inputs to outputs.
*   **Presets:** This tab allows users to save and recall routing presets.
*   **Settings:** This tab allows users to configure the IP address and port of the matrix.

Each tab is implemented as a separate class in the `ui/` directory. This makes the code more modular and easier to maintain.

### Connectivity Check

The `ConnectivityChecker` class is a `QThread` that runs in the background to check for a connection to the matrix. This is important because the ping command can take a few seconds to complete, and running it in the main thread would freeze the UI.

The `ConnectivityChecker` emits a `finished` signal when it is done, and the `HdmiMatrixApp` class has a slot that is connected to this signal. This allows the `HdmiMatrixApp` to update the UI with the connection status when the check is complete.

### Renaming

The `RenameDialog` class is a custom dialog that allows users to rename inputs and outputs. It provides a list of predefined names, as well as a text field for entering a custom name.

The custom names are stored in the `names.json` file, organized by preset. This allows users to have different names for the same input or output in different presets.

## Future Development

This application is designed to be extensible. Here are some potential areas for future development:

*   **Querying the Matrix:** The application currently does not have a way to query the matrix for its current state. This means that when a preset is recalled, the UI is not updated to reflect the new routing. Adding this functionality would make the application more robust.
*   **More Advanced Routing:** The application could be extended to support more advanced routing options, such as routing a single input to multiple outputs at once.
*   **Customizable Presets:** The application could be extended to allow users to create and name their own presets.
