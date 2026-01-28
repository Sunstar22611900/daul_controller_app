[English](README_EN.md) | [繁體中文](README.md)

# SUNSTAR Modbus RTU Controller Monitor Software (V3.0)

## Introduction
Designed for the SUNSTAR SY-DPCA series dual proportional coil controllers, this software provides an intuitive graphical interface for users to easily read and write various controller parameters via the Modbus RTU communication protocol (RS-485 interface).

<img width="960" height="800" alt="image" src="https://github.com/user-attachments/assets/e53f0ded-9a5d-49bf-a510-c48e78e50ead" />

## Features
*   **Dual Mode Support:** Supports switching between SY-DPCA-*-2 (Dual Controller) and SY-DPCA-*-1 (Single Controller) models.
*   **Quick Setup Wizard:** Guided steps to help users quickly complete basic configuration.
*   **Real-time Monitoring:** Simultaneously monitor output current, input signals, and fault status for two channels.
*   **Parameter Adjustment:** Provides complete parameter writing functions, including max/min current, ramp time, PWM frequency, dither parameters, and PID settings.
*   **Chart Analysis:** Provides real-time data charts to visualize and adjust output curve characteristics.
*   **Batch Operations:** Supports local saving, reading, and one-click writing of parameters to the controller.
*   **Multi-language Interface:** Supports switching between Traditional Chinese and English.
*   **Auto PID (BETA):** Adds automatic PID setting function in dual controller mode, but it is still a BETA version and is not recommended for use.

## Installation and Usage
This is a portable version; simply unzip and use.

1.  Enter the `SUNSTAR_dual_controller_app` folder.
2.  Find and run `SUNSTAR_dual_controller_app_V3.0.exe`.
    *   **Note:** To speed up launch times, the program is distributed as a folder. Please ensure the integrity of the entire folder and do not move the `.exe` file individually.

### Troubleshooting: SmartScreen Warning
When running for the first time on Windows, a blue **Windows SmartScreen** warning window may appear, stating "Windows protected your PC".
This is because this program is an internal development tool and does not have an expensive Microsoft digital signature. This is normal behavior.

**How to bypass the warning:**
1.  Click **"More info"** in the warning window.
2.  Click the **"Run anyway"** button.
3.  This warning will not appear again when running on the same computer.

## System Requirements
*   Windows 10 / 11 Operating System
*   USB to RS-485 Converter (requires appropriate driver installation)

## Operation Flow
1.  **Quick Setup (Recommended)**:
    -   The program will automatically open the "Quick Setup Wizard".
    -   Follow the on-screen instructions to select your application scenario and basic requirements step-by-step.
    -   The wizard will automatically configure relevant parameters upon completion.
    -   If quick setup is not needed, select the language and model, then click the button to enter the main program.
2.  **Connect Controller**:
    -   Select the correct COM Port, Baud Rate, and Address in the "Modbus Communication Settings" area at the top left of the main program.
    -   Click the "Connect" button.
3.  **Monitor Controller Status**:
    -   After a successful connection, the program will automatically start polling the controller status. The "Real-time Monitoring Area" at the top will display the controller's status, including current, input signals, and fault status.
    -   Click the "Real-time Chart" button in the top right of the monitoring area to open a new window and observe real-time changes in current and signals.
4.  **Configure Parameters**:
    -   The "Parameter Settings Area" in the middle allows configuration of controller parameters, including max/min current, ramp time, PWM frequency, dither parameters, and PID settings.
    -   Check the static characteristic curve at the bottom to verify if the parameter settings meet expectations.
    -   After monitoring configuration, click the "Apply to Controller" button to write all modified parameters to the controller at once.
5.  **Save and Load Parameters**:
    -   Use "Save Local" to save tuned parameters.
    -   Use "Load Local" to load previously saved parameter schemes.
6.  **Change Model or Language (If needed)**: Switch models and languages using the dropdown menu in the top right corner of the main program.
