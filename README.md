# SUNSTAR Modbus RTU Dual Controller Application

## Overview

This application provides a comprehensive Graphical User Interface (GUI) for configuring and monitoring a dual-channel controller via Modbus RTU protocol. It allows users to establish communication with the controller, view real-time monitoring data for two independent output groups (A and B), adjust various writable parameters, and visualize controller behavior through dynamic charts.

## Features

*   **Modbus RTU Communication:** Connects to controllers via serial COM ports with configurable baud rates and slave IDs.
*   **Real-time Monitoring:** Displays live output current, input command, and status for both Output A and Output B.
*   **Multi-language Support:** Supports both English and Traditional Chinese interfaces.
*   **Organized Parameter Management:** Writable parameters are categorized into Common, Output A, Output B, and PID parameters, accessible via a tabbed interface.
*   **Dynamic Control Mode Chart:** Visualizes the controller's output characteristics based on input selection settings, dynamically switching between "Dual Output Dual Slope", "Dual Output Single Slope", and "Single Output" modes.
*   **Parameter Persistence:** Save and load parameter configurations locally for easy recall and deployment.
*   **Batch Write Operations:** Apply multiple parameter changes to the controller in a single batch, with special handling for factory reset commands.
*   **Input Validation:** Ensures parameter values are within valid ranges and formats before writing to the controller.

## Requirements

To run this application from source, you need:

*   Python 3.x
*   `pyserial` library
*   `modbus_tk` library

## Installation

### From Executable (Windows)

A pre-built executable (`dual_controller_app.exe`) is available in the `dist/` directory or via GitHub Releases. No installation is required; simply run the executable.

### From Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Sunstar22611900/daul_controller_app.git
    cd daul_controller_app
    ```

2.  **Install dependencies:**
    ```bash
    pip install pyserial modbus_tk
    ```

## Usage

1.  **Run the application:**
    ```bash
    python dual_controller_app.py
    ```

2.  **Modbus Communication Setup:**
    *   Select the correct **COM Port** from the dropdown.
    *   Choose the appropriate **Baud Rate**.
    *   Enter the **Device Address (Slave ID)** (1-247).
    *   Click "Refresh Ports" if your COM port doesn't appear.
    *   Click "Connect" to establish Modbus communication.

3.  **Real-time Monitoring:**
    *   Once connected, the "Real-time Monitoring" section will display live data for Output A and Output B.

4.  **Writable Parameters:**
    *   Navigate through the tabs (Common, Output A, Output B, PID Parameters) to adjust various settings.
    *   Enter desired values in the input fields.
    *   Use "SAVE locally" to save current parameters to a JSON file.
    *   Use "LOAD locally" to load previously saved parameters.
    *   Click "APPLY to Controller" to write all configured parameters to the device.

5.  **Controller Mode Chart:**
    *   The "Controller Mode Chart" section visually represents the output characteristics based on the configured parameters. This chart updates dynamically as parameters are changed.

## Building the Executable (Optional)

You can build a standalone Windows executable using PyInstaller.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Generate the `.spec` file:**
    ```bash
    pyinstaller --noconsole --onefile dual_controller_app.py
    ```

3.  **Modify the `.spec` file:**
    Open `dual_controller_app.spec` in a text editor. Ensure the `datas` and `icon` sections are correctly configured to include necessary assets like icons and the `forest-light` theme. An example configuration for `datas` and `icon` within the `Analysis` and `EXE` objects respectively:

    ```python
    # ... inside Analysis object
    datas=[
        ('icon', 'icon'),
        ('forest-light.tcl', '.'),
        ('forest-light', 'forest-light'),
    ],
    # ...

    # ... inside EXE object
    icon='icon/002.ico'
    # ...
    ```

4.  **Build the executable:**
    ```bash
    pyinstaller dual_controller_app.spec -y
    ```
    The executable will be generated in the `dist/` directory.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details.
