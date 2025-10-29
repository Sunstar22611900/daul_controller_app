#根據gemini02版本手動修改排版

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import ttkbootstrap as ttk
import serial.tools.list_ports
import modbus_tk
import modbus_tk.defines as defines
import modbus_tk.modbus_rtu
import json
import threading
import time
import sys
import os
import math
from collections import deque
from datetime import datetime, timedelta
import csv

# Matplotlib imports for charting
import matplotlib
matplotlib.use("TkAgg")

# --- Matplotlib 中文顯示設定 ---
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 指定預設字體
matplotlib.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題
# ---

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import date2num, DateFormatter

# --- 全局變量 ---
# 用於儲存Modbus Master物件，方便在不同函數中存取
MODBUS_MASTER = None
# 控制每秒輪詢是否啟用的標誌 (現在由_toggle_connection管理)
POLLING_ACTIVE = False
# 儲存每秒輪詢的線程物件 (現在由_toggle_connection管理)
POLLING_THREAD = None
# 儲存參數檔案的預設目錄
PARAMETERS_DIR = "modbus_parameters"

# --- 語言包 ---
TEXTS = {
    "zh": {
        "APP_TITLE": "SUNSTAR Modbus RTU 雙控制器監控調整程式 V1.0",
        "MODBUS_PARAMS_FRAME_TEXT": "Modbus通訊參數設置",
        "COM_PORT_LABEL": "通訊端口",
        "BAUDRATE_LABEL": "鮑率",
        "SLAVE_ID_LABEL": "設備位址",
        "REFRESH_PORTS_BUTTON": "刷新端口",
        "CONNECT_BUTTON": "連接",
        "DISCONNECT_BUTTON": "斷開",
        "MONITOR_AREA_A_FRAME_TEXT": "即時監控 (A組輸出: 0000H~0002H)",
        "MONITOR_AREA_B_FRAME_TEXT": "即時監控 (B組輸出: 0003H~0005H)",
        "OUTPUT_CURRENT_LABEL": "輸出電流",
        "INPUT_SIGNAL_LABEL": "輸入信號",
        "CURRENT_STATUS_LABEL": "目前狀態",
        "WRITABLE_PARAMS_FRAME_TEXT": "可寫入參數",
        "WRITE_BUTTON": "寫入",
        "BATCH_PARAMS_FRAME_TEXT": "儲存/讀取/寫入",
        "SAVE_PARAMS_BUTTON": "本地儲存",
        "LOAD_PARAMS_BUTTON": "本地讀取",
        "BATCH_WRITE_BUTTON": "套用至控制器",
        "COM_PORT_NOT_FOUND_WARNING": "未找到可用端口。請確認設備已連接且驅動已安裝。",
        "COM_PORT_SELECT_ERROR": "請選擇一個通訊端口。",
        "COM_PORT_OPEN_FAIL": "無法打開端口 {port}。可能原因：\n1. 端口已被其他程式佔用。\n2. 串口名稱不正確。\n3. 驅動問題。\n錯誤: {e}",
        "MODBUS_CONNECT_FAIL": "無法連接到Modbus設備: {e}",
        "MODBUS_CONNECTED": "成功連接到 {port} (鮑率: {baudrate})。",
        "MODBUS_DISCONNECTED": "Modbus已斷開連接。",
        "MODBUS_DISCONNECT_FAIL": "斷開連接失敗: {e}",
        "SLAVE_ID_ERROR": "設備位址必須是1~247之間的整數。",
        "READ_REGISTERS_FAIL": "讀取寄存器失敗: {e}\n請檢查連接和設備位址。",
        "MODBUS_NOT_CONNECTED_WARNING": "Modbus通訊未建立，請先連接。",
        "READ_REGISTERS_POLLING_FAIL": "輪詢讀取寄存器失敗: {e}",
        "INPUT_EMPTY_ERROR": "寄存器 {reg_hex}: 輸入值不能為空。",
        "INPUT_RANGE_ERROR": "{type_name}超出範圍！請輸入 {min_val}~{max_val} 之間的值。",
        "INPUT_VALUE_TYPE_ERROR": "{type_name}必須是有效的數字。",
        "COMBOBOX_SELECT_ERROR": "寄存器 {reg_hex}: 請從下拉選單中選擇一個有效的選項。",
        "VALUE_CONVERSION_ERROR": "寄存器 {reg_hex} 數值轉換失敗，請檢查輸入格式。",
        "UNIT_MULTIPLE_ERROR": "寄存器 {reg_hex} 輸入值 {display_value} 不是 {unit_step} 的倍數。",
        "CURRENT_RANGE_ERROR": "最大電流必須大於等於最小電流 + 0.1。",
        "MODBUS_WRITE_FAIL_GENERAL": "寫入寄存器 0x{register_address:04X} 失敗: {e}",
        "MODBUS_WRITE_SUCCESS": "成功將數值 {value_str} 寫入寄存器 0x{register_address:04X}。",
        "WRITE_VALUE_DETERMINE_FAIL": "寄存器 {reg_hex}: 無法確定要寫入的值。",
        "PARAM_SAVE_PROMPT": "請輸入儲存名稱:",
        "FILE_EXISTS_CONFIRM": "名稱 \'{filename}\' 已存在，是否覆蓋原存檔？",
        "SAVE_SUCCESS": "參數已成功儲存為 \'{filename}\'.",
        "SAVE_FAIL": "儲存參數失敗: {e}",
        "LOAD_FAIL_NO_FILES": "未找到任何已儲存的參數檔案。",
        "LOAD_PROMPT": "請選擇要讀取的參數方案:",
        "FILE_FORMAT_ERROR": "檔案 \'{fname}\' 格式不正確，已跳過。",
        "FILE_READ_ERROR": "讀取檔案 \'{fname}\' 失敗: {e}",
        "LOAD_SUCCESS": "參數方案 \'{selected_name}\' 已成功讀取。",
        "SELECT_ITEM_ERROR": "請選擇一個參數方案。",
        "LOAD_BUTTON": "讀取",
        "CANCEL_BUTTON": "取消",
        "BATCH_WRITE_PROGRESS_TITLE": "寫入進度",
        "BATCH_WRITE_PREPARING": "準備寫入...",
        "BATCH_WRITE_IN_PROGRESS": "正在寫入寄存器 0x{register_address:04X} ({i}/{total_registers})...",
        "BATCH_WRITE_SUCCESS_ALL": "所有參數已成功寫入控制器！",
        "BATCH_WRITE_PARTIAL_FAIL": "寫入部分失敗。成功寫入 {success_count}/{total_registers} 個參數。\n失敗寄存器: {failed_registers_list}",
        "INFO_TITLE": "資訊",
        "WARNING_TITLE": "警告",
        "ERROR_TITLE": "錯誤",
        "CONFIRM_TITLE": "確認",
        "CONFIRM_DELETE_TITLE": "刪除確認",
        "CONFIRM_DELETE_MSG": "您確定要刪除參數方案",
        "DELETE_BUTTON": "刪除",
        "NO_ITEM_SELECTED_MSG": "請選擇一個項目。",
        "FACTORY_RESET_NO_ACTION_MSG": "恢復出廠設置 (0) 不執行任何操作。",
        "FACTORY_RESET_SUCCESS_MSG": "恢復出廠設置 (5) 指令已發送，5秒後將重新讀取寄存器。",
        "SKIP_REGISTER_BATCH_WRITE": "跳過寄存器 0x{register_address:04X} ({i}/{total_registers})...",
        "FILE_NOT_FOUND_FOR_DELETE": "檔案 \'{filename}\' 不存在，無法刪除。",
        "DELETE_FAIL": "刪除檔案 \'{filename}\' 失敗: {e}",
        "DELETE_SUCCESS": "參數已成功刪除為 \'{filename}\'.",
        "FACTORY_RESET_CONFIRM_BATCH_MSG": "即將將控制器恢復出廠設置，是否確定?",
        "FACTORY_RESET_COUNTDOWN_MSG": "控制器重置中，請稍候... {seconds} 秒後將重新讀取參數。",
        "CHART_SAVE_SUCCESS_MSG": "圖表資料已成功儲存。",
        "CHART_SAVE_ERROR_MSG": "儲存圖表資料失敗: {e}",
        
        # 新增/修改的可寫入參數區的翻譯鍵
        "COMMON_PARAMS_FRAME_TEXT": "通用參數",
        "A_GROUP_PARAMS_FRAME_TEXT": "A組輸出參數",
        "B_GROUP_PARAMS_FRAME_TEXT": "B組輸出參數",
        "PID_PARAMS_FRAME_TEXT": "PID參數",

        "SIGNAL_SELECTION_1": "信號 1 選擇",
        "SIGNAL_SELECTION_2": "信號 2 選擇",
        "PANEL_DISPLAY_MODE": "面板顯示模式",
        "RS485_CONTROL_SIGNAL_1": "第一組485控制信號 (0~100%)",
        "RS485_CONTROL_SIGNAL_2": "第二組485控制信號 (0~100%)",
        "DEVICE_ADDRESS_ADJUSTMENT": "設備位址調整 (1~247)",
        "DEVICE_BAUDRATE_ADJUSTMENT": "設備鮑率調整",
        "FACTORY_RESET": "恢復出廠設置",
        "A_INPUT_SIGNAL_SELECTION": "輸入信號選擇",
        "A_FEEDBACK_SIGNAL": "反饋信號",
        "A_MAX_CURRENT": "最大電流 (0.20~3.00A)",
        "A_MIN_CURRENT": "最小電流 (0.00~1.00A)",
        "A_CURRENT_RISE_TIME": "電流上升時間 (0.1~5.0s)",
        "A_CURRENT_FALL_TIME": "電流下降時間 (0.1~5.0s)",
        "A_COMMAND_DEAD_ZONE": "指令死區 (0~5%)",
        "A_PWM_FREQUENCY": "PWM頻率 (70~1000Hz)",
        "A_TREMOR_FREQUENCY": "震顫頻率 (70~500Hz)",
        "A_DITHER_AMPLITUDE": "震顫幅度 (0~25%)",
        "B_INPUT_SIGNAL_SELECTION": "輸入信號選擇",
        "B_FEEDBACK_SIGNAL": "反饋信號",
        "B_MAX_CURRENT": "最大電流 (0.20~3.00A)",
        "B_MIN_CURRENT": "最小電流 (0.00~1.00A)",
        "B_CURRENT_RISE_TIME": "電流上升時間 (0.1~5.0s)",
        "B_CURRENT_FALL_TIME": "電流下降時間 (0.1~5.0s)",
        "B_COMMAND_DEAD_ZONE": "指令死區 (0~5%)",
        "B_PWM_FREQUENCY": "PWM頻率 (70~1000Hz)",
        "B_TREMOR_FREQUENCY": "震顫頻率 (70~500Hz)",
        "B_DITHER_AMPLITUDE": "震顫幅度 (0~25%)",
        "SIGNAL_1_P": "信號1 P (0~100)",
        "SIGNAL_1_I": "信號1 I (0~100)",
        "SIGNAL_1_D": "信號1 D (0~100)",
        "SIGNAL_2_P": "信號2 P (0~100)",
        "SIGNAL_2_I": "信號2 I (0~100)",
        "SIGNAL_2_D": "信號2 D (0~100)",
        "LANGUAGE_LABEL": "Language",
        "UNKNOWN_STATUS": "未知狀態",
        "WARNING_READ_DATA_INSUFFICIENT": "警告: 讀取到的寄存器數據不足以更新所有可寫入參數。",
        "PARAM_SAVE_PROMPT_TITLE": "參數儲存",
        "CONTROLLER_MODE_CHART_FRAME_TEXT": "控制器模式圖表",
        "OUTPUT_CHARACTERISTICS": "輸出特性",
        "LINKED_MODE_OUTPUT_CHARACTERISTICS": "連動模式輸出特性 (A組輸出 & B組輸出)",
        "CURRENT": "電流",
        "TIME": "時間",
        "A_GROUP_LEGEND": "A組輸出曲線",
        "B_GROUP_LEGEND": "B組輸出曲線",
        "INPUT_SIGNAL": "輸入信號",
        "DUAL_OUTPUT_DUAL_SLOPE_MODE_TEXT": "雙組信號-雙組輸出",
        "DUAL_OUTPUT_SINGLE_SLOPE_MODE_TEXT": "單組信號-雙組輸出",
        "SINGLE_OUTPUT_MODE_TEXT": "單組輸出",

        # --- Real-time Chart ---
        "SHOW_CHART_BUTTON": "即時圖表",
        "CLOSE_CHART_BUTTON": "關閉圖表",
        "CHART_WINDOW_TITLE": "即時數據圖表",
        "SAVE_CHART_DATA_BUTTON": "儲存圖表數據",
        "Y_AXIS_CURRENT": "輸出電流 (A)",
        "Y_AXIS_SIGNAL": "輸入信號 (%)",
        "X_AXIS_TIME": "時間",
        "SAVE_DIALOG_TITLE": "儲存數據為 CSV",
        "FILE_TYPE_CSV": "CSV 檔案",
        "LEGEND_CURRENT_A": "A組 電流",
        "LEGEND_SIGNAL_A": "A組 信號",
        "LEGEND_CURRENT_B": "B組 電流",
        "LEGEND_SIGNAL_B": "B組 信號",
        "LEGEND_CURRENT_S": "輸出電流",
        "LEGEND_SIGNAL_S": "輸入信號",
        "CHART_A_TITLE": "A組輸出",
        "CHART_B_TITLE": "B組輸出",
        "CHART_S_TITLE": "單組輸出",

        # --- 模式選擇與單組控制器 ---
        "APP_TITLE_DUAL": "SUNSTAR Modbus RTU 雙控制器監控調整程式 V2.0",
        "APP_TITLE_SINGLE": "SUNSTAR Modbus RTU 單控制器監控調整程式 V2.0",
        "MODE_SELECTION_TITLE": "型號選擇",
        "MODE_SELECTION_PROMPT": "請選擇要操作的控制器型號：",
        "DUAL_CONTROLLER_BUTTON": "SY-DPCA-*-2",
        "SINGLE_CONTROLLER_BUTTON": "SY-DPCA-*-1",
        "SWITCH_MODE_FRAME_TEXT": "型號切換",
        "DUAL_MODE_OPTION": "SY-DPCA-*-2",
        "SINGLE_MODE_OPTION": "SY-DPCA-*-1",
        "CONFIRM_SWITCH_MODE_TITLE": "確認切換模式",
        "CONFIRM_SWITCH_MODE_MSG": "切換模式將會斷開目前連線並重置介面，是否確定？",
        "BATCH_WRITE_PROGRESS_TITLE": "寫入進度",
        "BATCH_WRITE_IN_PROGRESS": "正在寫入寄存器 0x{register_address:04X} ({i}/{total_registers})...",
        "CURRENT_RANGE_ERROR_A": "A組輸出：最大電流必須大於等於最小電流 + 0.1A。",
        "CURRENT_RANGE_ERROR_B": "B組輸出：最大電流必須大於等於最小電流 + 0.1A。",
        "CURRENT_RANGE_ERROR_S": "單組輸出：最大電流必須大於等於最小電流 + 0.1A。",
        "MONITOR_AREA_SINGLE_FRAME_TEXT": "即時監控 (輸出: 0000H~0002H)",
        "S_SIGNAL_SELECTION": "信號選擇",
        "S_ENABLE_MODE": "外部啟動功能",
        "S_DISPLAY_MODE": "顯示模式",
        "S_485_CONTROL_SIGNAL": "485控制信號 (0~100%)",
        "S_FACTORY_RESET": "恢復出廠設置",
        "S_MAX_CURRENT": "最大電流 (0.00~3.00A)",
        "S_MIN_CURRENT": "最小電流 (0.00~1.00A)",
        "S_CURRENT_RISE_TIME": "電流上升時間 (0.1~5.0s)",
        "S_CURRENT_FALL_TIME": "電流下降時間 (0.1~5.0s)",
        "S_DITHER_FREQUENCY": "震顫頻率 (70~350Hz)",
        "S_DEAD_ZONE_SETTING": "指令死區 (0~5%)",
        
        # Register value maps (for localized display)
        "STATUS_MAP_VALUES": {
            0: "正常",
            1: "4~20mA信號開路",
            2: "4~20mA信號過載",
            3: "線圈開路",
            4: "線圈短路"
        },
        "S_STATUS_MAP_VALUES": {
            0: "正常",
            1: "信號斷線",
            2: "過載",
            3: "線圈開路",
            4: "線圈短路"
        },
        "S_SIGNAL_SELECTION_MAP_VALUES": {
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA",
            3: "RS485",
            4: "面板控制"
        },
        "S_ENABLE_MODE_MAP_VALUES": {
            0: "禁用",
            1: "啟用"
        },
        "S_DISPLAY_MODE_MAP_VALUES": {
            0: "顯示電流",
            1: "顯示輸入信號",
            2: "不顯示"
        },
        "S_FACTORY_RESET_MAP_VALUES": {
            5: "恢復出廠設置"
        },
        "SIGNAL_SELECTION_MAP_VALUES": { # For 0006H, 0007H
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA"
        },
        "PANEL_DISPLAY_MODE_MAP_VALUES": { # For 0008H
            0: "顯示A組輸出電流",
            1: "顯示A組輸入信號",
            2: "顯示B組輸出電流",
            3: "顯示B組輸入信號",
            4: "不顯示"
        },
        "DEVICE_BAUDRATE_MAP_VALUES": { # For 000CH
            0: "4800",
            1: "9600",
            2: "19200",
            3: "38400",
            4: "57600"
        },
        "FACTORY_RESET_MAP_VALUES": { # For 000DH
            0: "無作用",
            5: "恢復出廠設置"
        },
        "A_INPUT_SIGNAL_SELECTION_MAP_VALUES": { # For 000EH
            0: "信號 1",
            1: "第一組485"
        },
        "B_INPUT_SIGNAL_SELECTION_MAP_VALUES": { # For 0018H
            0: "無輸出",
            1: "信號 1",
            2: "信號 2",
            3: "第一組485",
            4: "第二組485"
        },
        "FEEDBACK_SIGNAL_MAP_VALUES": { # For 000FH, 0019H
            0: "關閉",
            1: "信號 1",
            2: "信號 2"
        }
    },
    "en": {
        "APP_TITLE": "SUNSTAR Modbus RTU Dual Controller Setup V1.0",
        "MODBUS_PARAMS_FRAME_TEXT": "Modbus Setting",
        "COM_PORT_LABEL": "Port",
        "BAUDRATE_LABEL": "Baud Rate",
        "SLAVE_ID_LABEL": "Address",
        "REFRESH_PORTS_BUTTON": "Refresh",
        "CONNECT_BUTTON": "Connect",
        "DISCONNECT_BUTTON": "Disconnect",
        "MONITOR_AREA_A_FRAME_TEXT": "Real-time Monitoring (Output A: 0000H~0002H)",
        "MONITOR_AREA_B_FRAME_TEXT": "Real-time Monitoring (Output B: 0003H~0005H)",
        "OUTPUT_CURRENT_LABEL": "Output Current",
        "INPUT_SIGNAL_LABEL": "Input Command",
        "CURRENT_STATUS_LABEL": "Status",
        "WRITABLE_PARAMS_FRAME_TEXT": "Writable Parameters",
        "WRITE_BUTTON": "Write",
        "BATCH_PARAMS_FRAME_TEXT": "Batch SAVE/LOAD/WRITE",
        "SAVE_PARAMS_BUTTON": "SAVE locally",
        "LOAD_PARAMS_BUTTON": "LOAD locally",
        "BATCH_WRITE_BUTTON": "APPLY to Controller",
        "COM_PORT_NOT_FOUND_WARNING": "No available COM ports found. Please ensure the device is connected and drivers are installed.",
        "COM_PORT_SELECT_ERROR": "Please select a communication port.",
        "COM_PORT_OPEN_FAIL": "Failed to open COM port {port}. Possible reasons:\n1. Port is in use by another program.\n2. Incorrect port name.\n3. Driver issues.\nError: {e}",
        "MODBUS_CONNECT_FAIL": "Failed to connect to Modbus device: {e}",
        "MODBUS_CONNECTED": "Successfully connected to {port} (Baud Rate: {baudrate}).",
        "MODBUS_DISCONNECTED": "Modbus disconnected.",
        "MODBUS_DISCONNECT_FAIL": "Failed to disconnect: {e}",
        "SLAVE_ID_ERROR": "Device address must be an integer between 1 and 247.",
        "READ_REGISTERS_FAIL": "Failed to read registers: {e}\nPlease check connection and device address.",
        "MODBUS_NOT_CONNECTED_WARNING": "Modbus communication not established. Please connect first.",
        "READ_REGISTERS_POLLING_FAIL": "Polling read failed: {e}",
        "INPUT_EMPTY_ERROR": "Register {reg_hex}: Input value cannot be empty.",
        "INPUT_RANGE_ERROR": "{type_name} out of range! Please enter a value between {min_val}~{max_val}.",
        "INPUT_VALUE_TYPE_ERROR": "{type_name} must be a valid number.",
        "COMBOBOX_SELECT_ERROR": "Register {reg_hex}: Please select a valid option from the dropdown.",
        "VALUE_CONVERSION_ERROR": "Register {reg_hex} value conversion failed. Please check input format.",
        "UNIT_MULTIPLE_ERROR": "Register {reg_hex} input value {display_value} is not a multiple of {unit_step}.",
        "CURRENT_RANGE_ERROR": "Maximum current must be greater than or equal to minimum current + 0.1.",
        "MODBUS_WRITE_FAIL_GENERAL": "Failed to write register 0x{register_address:04X}: {e}",
        "MODBUS_WRITE_SUCCESS": "Successfully wrote value {value_str} to register 0x{register_address:04X}.",
        "WRITE_VALUE_DETERMINE_FAIL": "Register {reg_hex}: Unable to determine value to write.",
        "PARAM_SAVE_PROMPT": "Please enter a name for saving:",
        "FILE_EXISTS_CONFIRM": "Name \'{filename}\' already exists. Overwrite?",
        "SAVE_SUCCESS": "Parameters successfully saved as \'{filename}\'.",
        "SAVE_FAIL": "Failed to save parameters: {e}",
        "LOAD_FAIL_NO_FILES": "No saved parameter files found.",
        "LOAD_PROMPT": "Please select a parameter set to load:",
        "FILE_FORMAT_ERROR": "File \'{fname}\' has incorrect format, skipped.",
        "FILE_READ_ERROR": "Failed to read file \'{fname}\': {e}",
        "LOAD_SUCCESS": "Parameter set \'{selected_name}\' successfully loaded.",
        "SELECT_ITEM_ERROR": "Please select an item.",
        "LOAD_BUTTON": "Load",
        "CANCEL_BUTTON": "Cancel",
        "BATCH_WRITE_PROGRESS_TITLE": "Write Progress",
        "BATCH_WRITE_PREPARING": "Preparing to write...",
        "BATCH_WRITE_IN_PROGRESS": "Writing register 0x{register_address:04X} ({i}/{total_registers})...",
        "BATCH_WRITE_SUCCESS_ALL": "All parameters successfully written to controller!",
        "BATCH_WRITE_PARTIAL_FAIL": "write partially failed. Successfully wrote {success_count}/{total_registers} parameters.\nFailed Registers: {failed_registers_list}",
        "INFO_TITLE": "Information",
        "WARNING_TITLE": "Warning",
        "ERROR_TITLE": "Error",
        "CONFIRM_TITLE": "Confirm",
        "CONFIRM_DELETE_TITLE": "Delete Confirmation",
        "CONFIRM_DELETE_MSG": "Are you sure you want to delete parameter set",
        "DELETE_BUTTON": "Delete",
        "NO_ITEM_SELECTED_MSG": "Please select an item.",
        "FACTORY_RESET_NO_ACTION_MSG": "Factory Reset (0) performs no action.",
        "FACTORY_RESET_SUCCESS_MSG": "Factory Reset (5) command sent. Re-reading registers in 5 seconds.",
        "SKIP_REGISTER_BATCH_WRITE": "Skipping register 0x{register_address:04X} ({i}/{total_registers})...",
        "FILE_NOT_FOUND_FOR_DELETE": "File \'{filename}\' not found for deletion.",
        "DELETE_FAIL": "Failed to delete file \'{filename}\': {e}",
        "DELETE_SUCCESS": "Parameters successfully deleted as \'{filename}\'.",
        "FACTORY_RESET_CONFIRM_BATCH_MSG": "You are about to factory reset the controller. Are you sure?",
        "FACTORY_RESET_COUNTDOWN_MSG": "Controller is resetting, please wait... Re-reading parameters in {seconds} seconds.",
        "CHART_SAVE_SUCCESS_MSG": "Chart data saved successfully.",
        "CHART_SAVE_ERROR_MSG": "Failed to save chart data: {e}",
        
        # New/Modified writable parameter area translations
        "COMMON_PARAMS_FRAME_TEXT": "Common Parameters",
        "A_GROUP_PARAMS_FRAME_TEXT": "Output A Parameters",
        "B_GROUP_PARAMS_FRAME_TEXT": "Output B Parameters",
        "PID_PARAMS_FRAME_TEXT": "PID Parameters",

        "SIGNAL_SELECTION_1": "Command 1 Selection",
        "SIGNAL_SELECTION_2": "Command 2 Selection",
        "PANEL_DISPLAY_MODE": "Panel Display Mode",
        "RS485_CONTROL_SIGNAL_1": "RS485 Command 1 (0~100%)",
        "RS485_CONTROL_SIGNAL_2": "RS485 Command 2 (0~100%)",
        "DEVICE_ADDRESS_ADJUSTMENT": "Device Address Adjustment (1~247)",
        "DEVICE_BAUDRATE_ADJUSTMENT": "Device Baud Rate Adjustment",
        "FACTORY_RESET": "Factory Reset",
        "A_INPUT_SIGNAL_SELECTION": "Input Command Selection",
        "A_FEEDBACK_SIGNAL": "Feedback Command",
        "A_MAX_CURRENT": "Max Output Current (0.20~3.00A)",
        "A_MIN_CURRENT": "Min Output Current (0.00~1.00A)",
        "A_CURRENT_RISE_TIME": "Ramp up Time (0.1~5.0s)",
        "A_CURRENT_FALL_TIME": "Ramp down Time (0.1~5.0s)",
        "A_COMMAND_DEAD_ZONE": "Command Deadband (0~5%)",
        "A_PWM_FREQUENCY": "PWM Frequency (70~1000Hz)",
        "A_TREMOR_FREQUENCY": "Dither Frequency (70~500Hz)",
        "A_DITHER_AMPLITUDE": "Dither Amplitude (0~25%)",
        "B_INPUT_SIGNAL_SELECTION": "Input Command Selection",
        "B_FEEDBACK_SIGNAL": "Feedback Command",
        "B_MAX_CURRENT": "Max Output Current (0.20~3.00A)",
        "B_MIN_CURRENT": "Min Output Current (0.00~1.00A)",
        "B_CURRENT_RISE_TIME": "Ramp up Time (0.1~5.0s)",
        "B_CURRENT_FALL_TIME": "Ramp down Time (0.1~5.0s)",
        "B_COMMAND_DEAD_ZONE": "Command Deadband (0~5%)",
        "B_PWM_FREQUENCY": "PWM Frequency (70~1000Hz)",
        "B_TREMOR_FREQUENCY": "Dither Frequency (70~500Hz)",
        "B_DITHER_AMPLITUDE": "Dither Amplitude (0~25%)",
        "SIGNAL_1_P": "Command 1 P (0~100)",
        "SIGNAL_1_I": "Command 1 I (0~100)",
        "SIGNAL_1_D": "Command 1 D (0~100)",
        "SIGNAL_2_P": "Command 2 P (0~100)",
        "SIGNAL_2_I": "Command 2 I (0~100)",
        "SIGNAL_2_D": "Command 2 D (0~100)",
        "LANGUAGE_LABEL": "Language",
        "UNKNOWN_STATUS": "Unknown Status",
        "WARNING_READ_DATA_INSUFFICIENT": "Warning: Insufficient register data read to update all writable parameters.",
        "PARAM_SAVE_PROMPT_TITLE": "Save Parameters",
        "CONTROLLER_MODE_CHART_FRAME_TEXT": "Controller Mode Chart",
        "OUTPUT_CHARACTERISTICS": "Output Characteristics",
        "LINKED_MODE_OUTPUT_CHARACTERISTICS": "Linked Mode Output Characteristics (Output A & B)",
        "CURRENT": "Current",
        "TIME": "Time",
        "A_GROUP_LEGEND": "Output A Curve",
        "B_GROUP_LEGEND": "Output B Curve",
        "INPUT_SIGNAL": "Input Command",
        "DUAL_OUTPUT_DUAL_SLOPE_MODE_TEXT": "Dual Output Dual Slope",
        "DUAL_OUTPUT_SINGLE_SLOPE_MODE_TEXT": "Dual Output Single Slope",
        "SINGLE_OUTPUT_MODE_TEXT": "Single Output",

        # --- Real-time Chart ---
        "SHOW_CHART_BUTTON": "Real-time Chart",
        "CLOSE_CHART_BUTTON": "Close Chart",
        "CHART_WINDOW_TITLE": "Real-time Data Chart",
        "SAVE_CHART_DATA_BUTTON": "Save Chart Data",
        "Y_AXIS_CURRENT": "Output Current (A)",
        "Y_AXIS_SIGNAL": "Input Command (%)",
        "X_AXIS_TIME": "Time",
        "SAVE_DIALOG_TITLE": "Save Data as CSV",
        "FILE_TYPE_CSV": "CSV Files",
        "LEGEND_CURRENT_A": "Output A Current",
        "LEGEND_SIGNAL_A": "Output A Command",
        "LEGEND_CURRENT_B": "Output B Current",
        "LEGEND_SIGNAL_B": "Output B Command",
        "LEGEND_CURRENT_S": "Output Current",
        "LEGEND_SIGNAL_S": "Input Command",
        "CHART_A_TITLE": "Output A",
        "CHART_B_TITLE": "Output B",
        "CHART_S_TITLE": "Single Output",

        # --- Mode Selection & Single Controller ---
        "APP_TITLE_DUAL": "SUNSTAR Modbus RTU Dual Controller Setup V2.0",
        "APP_TITLE_SINGLE": "SUNSTAR Modbus RTU Single Controller Setup V2.0",
        "MODE_SELECTION_TITLE": "Model Selection",
        "MODE_SELECTION_PROMPT": "Please select the controller model:",
        "DUAL_CONTROLLER_BUTTON": "SY-DPCA-*-2",
        "SINGLE_CONTROLLER_BUTTON": "SY-DPCA-*-1",
        "SWITCH_MODE_FRAME_TEXT": "Model Switch",
        "DUAL_MODE_OPTION": "SY-DPCA-*-2",
        "SINGLE_MODE_OPTION": "SY-DPCA-*-1",
        "CONFIRM_SWITCH_MODE_TITLE": "Confirm Mode Switch",
        "CONFIRM_SWITCH_MODE_MSG": "Switching modes will disconnect the current session and reset the interface. Are you sure?",
        "BATCH_WRITE_PROGRESS_TITLE": "Write Progress",
        "BATCH_WRITE_IN_PROGRESS": "Writing register 0x{register_address:04X} ({i}/{total_registers})...",
        "CURRENT_RANGE_ERROR_A": "Output A: Maximum current must be >= Minimum current + 0.1A.",
        "CURRENT_RANGE_ERROR_B": "Output B: Maximum current must be >= Minimum current + 0.1A.",
        "CURRENT_RANGE_ERROR_S": "Single Output: Maximum current must be >= Minimum current + 0.1A.",
        "MONITOR_AREA_SINGLE_FRAME_TEXT": "Real-time Monitoring (Output: 0000H~0002H)",
        "S_SIGNAL_SELECTION": "Command Selection",
        "S_ENABLE_MODE": "Enable Mode",
        "S_DISPLAY_MODE": "Panel Display Mode",
        "S_485_CONTROL_SIGNAL": "RS485 Command (0~100%)",
        "S_FACTORY_RESET": "Factory Reset",
        "S_MAX_CURRENT": "Max Output Current (0.00~3.00A)",
        "S_MIN_CURRENT": "Min Output Current (0.00~1.00A)",
        "S_CURRENT_RISE_TIME": "Ramp up Time (0.1~5.0s)",
        "S_CURRENT_FALL_TIME": "Ramp down Time (0.1~5.0s)",
        "S_DITHER_FREQUENCY": "Dither Frequency (70~350Hz)",
        "S_DEAD_ZONE_SETTING": "Command Deadband (0~5%)",
        
        # Register value maps (for localized display)
        "STATUS_MAP_VALUES": {
            0: "Normal",
            1: "4~20mA command open",
            2: "4~20mA command overload",
            3: "Coil open",
            4: "Coil short"

        },
        "S_STATUS_MAP_VALUES": {
            0: "Normal",
            1: "Current Signal Broken",
            2: "Overload",
            3: "Coil Open",
            4: "Coil Short"
        },
        "S_SIGNAL_SELECTION_MAP_VALUES": {
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA",
            3: "RS485",
            4: "Panel Control"
        },
        "S_ENABLE_MODE_MAP_VALUES": {
            0: "Disabled",
            1: "Enabled"
        },
        "S_DISPLAY_MODE_MAP_VALUES": {
            0: "Show Output Current",
            1: "Show Input Command",
            2: "No Display"
        },
        "S_FACTORY_RESET_MAP_VALUES": {
            5: "Factory Reset"
        },
        "SIGNAL_SELECTION_MAP_VALUES": { # For 0006H, 0007H
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA"
        },
        "PANEL_DISPLAY_MODE_MAP_VALUES": { # For 0008H
            0: "Show Output A Current",
            1: "Show Command for Output A",
            2: "Show Output B Current",
            3: "Show Command for Output B",
            4: "Do Not Display"
        },
        "DEVICE_BAUDRATE_MAP_VALUES": { # For 000CH
            0: "4800",
            1: "9600",
            2: "19200",
            3: "38400",
            4: "57600"
        },
        "FACTORY_RESET_MAP_VALUES": { # For 000DH
            0: "No Action",
            5: "Factory Reset"
        },
        "A_INPUT_SIGNAL_SELECTION_MAP_VALUES": { # For 000EH
            0: "Command 1",
            1: "RS485 Command 1"
        },
        "B_INPUT_SIGNAL_SELECTION_MAP_VALUES": { # For 0018H
            0: "No Output",
            1: "Command 1",
            2: "Command 2",
            3: "RS485 Command 1",
            4: "RS485 Command 2"
        },
        "FEEDBACK_SIGNAL_MAP_VALUES": { # For 000FH, 0019H
            0: "Off",
            1: "Command 1",
            2: "Command 2"
        }
    }
}


# --- 輔助函數 ---

def convert_to_float(value, scale):
    """
    將寄存器讀取到的整數值轉換為浮點數。
    例如：值為67，scale為100，則轉換為0.67。
    """
    try:
        return float(value) / scale
    except (ValueError, TypeError):
        return None

def convert_to_register_value(value, scale):
    """
    將浮點數值轉換為寄存器可寫入的整數值。
    例如：值為0.67，scale為100，則轉換為67。
    """
    try:
        return int(float(value) * scale)
    except (ValueError, TypeError):
        return None

def validate_input_range(value, min_val, max_val, type_name="", is_int=False):
    """
    驗證輸入值是否在指定範圍內，並提供錯誤提示。
    :param value: 用戶輸入的字串值。
    :param min_val: 允許的最小值。
    :param max_val: 允許的最大值。
    :param type_name: 該輸入欄位的名稱，用於錯誤提示。
    :param is_int: 如果為True，表示需要驗證為整數。
    :return: 如果在範圍內且格式正確則返回True，否則返回False。
    """
    try:
        if is_int:
            num_value = int(value)
        else:
            num_value = float(value)
        
        if not (min_val <= num_value <= max_val):
            messagebox.showwarning(ModbusMonitorApp.get_current_translation("WARNING_TITLE"),
                                   ModbusMonitorApp.get_current_translation("INPUT_RANGE_ERROR").format(type_name=type_name, min_val=min_val, max_val=max_val))
            return False
        return True
    except ValueError:
        messagebox.showwarning(ModbusMonitorApp.get_current_translation("WARNING_TITLE"),
                               ModbusMonitorApp.get_current_translation("INPUT_VALUE_TYPE_ERROR").format(type_name=type_name))
        return False

def validate_current_range(max_curr_str, min_curr_str):
    """
    驗證最大電流和最小電流的特殊限制：最大電流必須大於等於最小電流 + 0.1。
    """
    try:
        max_curr = float(max_curr_str)
        min_curr = float(min_curr_str)
        if not (max_curr >= min_curr + 0.1):
            messagebox.showwarning(ModbusMonitorApp.get_current_translation("WARNING_TITLE"),
                                   ModbusMonitorApp.get_current_translation("CURRENT_RANGE_ERROR"))
            return False
        return True
    except ValueError:
        # 如果數字格式本身有問題，交給validate_input_range處理
        return True 
    
def write_modbus_register(slave_id, register_address, value):
    """
    向Modbus設備寫入單個寄存器（功能碼06H）。
    :param slave_id: 從站設備位址。
    :param register_address: 寄存器地址（十進制）。
    :param value: 要寫入的數值。
    :return: 寫入成功返回True，失敗返回False。
    """
    global MODBUS_MASTER
    if MODBUS_MASTER:
        try:
            print(f"嘗試寫入 Modbus: Slave ID={slave_id}, Reg=0x{register_address:04X}, Value={value}")
            MODBUS_MASTER.execute(slave_id, defines.WRITE_SINGLE_REGISTER, register_address, output_value=value)
            print(f"寫入成功: Reg=0x{register_address:04X}, Value={value}")
            return True
        except Exception as e:
            messagebox.showerror(ModbusMonitorApp.get_current_translation("ERROR_TITLE"),
                                 ModbusMonitorApp.get_current_translation("MODBUS_WRITE_FAIL_GENERAL").format(register_address=register_address, e=e))
            print(f"寫入失敗: Reg=0x{register_address:04X}, Error: {e}")
            return False
    else:
        messagebox.showwarning(ModbusMonitorApp.get_current_translation("WARNING_TITLE"),
                               ModbusMonitorApp.get_current_translation("MODBUS_NOT_CONNECTED_WARNING"))
        print("Modbus通訊未建立，無法寫入。")
        return False

# --- GUI 介面 ---
class RealtimeChartWindow(tk.Toplevel):
    def __init__(self, master, app_instance):
        super().__init__(master)
        self.app = app_instance # Reference to the main application instance
        self.controller_mode = self.app.controller_mode

        self.title(self.app.get_current_translation("CHART_WINDOW_TITLE"))
        # 移除標題列
        self.overrideredirect(True)
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 用於記錄滑鼠點擊時的起始座標
        self._drag_start_x = 0
        self._drag_start_y = 0

        # --- 綁定滑鼠事件以實現拖曳 ---
        # 1. 左鍵按下時，記錄起始座標
        self.bind('<Button-1>', self.start_drag)
        # 2. 左鍵按住並移動時，移動視窗
        self.bind('<B1-Motion>', self.drag_window)
        # 3. 可以在釋放時清除，但通常非必要，因為 start_drag 會更新
        # self.master.bind('<ButtonRelease-1>', self.stop_drag)

        self._create_widgets()
        self._create_charts() # Creates axes and empty plot lines
        self._update_language() # Sets initial text and layout

        # Start a periodic update for the chart
        self.after_id = self.after(250, self._periodic_update) # Reduced frequency

    def start_drag(self, event):
        """滑鼠左鍵按下時，記錄相對於視窗左上角的座標"""
        # 記錄滑鼠點擊位置相對於視窗左上角 (0, 0) 的偏移
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    def drag_window(self, event):
        """滑鼠按住並移動時，計算並設定視窗的新位置"""
        # 計算視窗的新位置：
        # 新位置 = 滑鼠的螢幕絕對位置 - 滑鼠點擊時的偏移)
        # event.x_root 和 event.y_root 是滑鼠相對於整個螢幕的絕對座標
        new_x = event.x_root - self._drag_start_x
        new_y = event.y_root - self._drag_start_y
        # 移動視窗
        self.geometry(f'+{new_x}+{new_y}')

    def _create_widgets(self):
        # Frame for charts
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Save button
        self.save_button = ttk.Button(self, text=self.app.get_current_translation("SAVE_CHART_DATA_BUTTON"),
                                      command=self._save_data)
        self.save_button.pack(side=tk.BOTTOM, pady=5)

    def _create_charts(self):
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.lines = {}
        self.axes = []

        if self.controller_mode == 'dual':
            # Two subplots for dual mode, with explicit x-axis sharing
            ax1_a = self.figure.add_subplot(211)
            ax2_a = ax1_a.twinx()
            self.axes.append((ax1_a, ax2_a))
            self.lines['a_current'], = ax1_a.plot([], [], color='dodgerblue')
            self.lines['a_signal'], = ax2_a.plot([], [], color='limegreen')

            # Explicitly share the x-axis with the first plot
            ax1_b = self.figure.add_subplot(212, sharex=ax1_a)
            ax2_b = ax1_b.twinx()
            self.axes.append((ax1_b, ax2_b))
            self.lines['b_current'], = ax1_b.plot([], [], color='dodgerblue')
            self.lines['b_signal'], = ax2_b.plot([], [], color='limegreen')
        else:
            # One subplot for single mode
            ax1_s = self.figure.add_subplot(111)
            ax2_s = ax1_s.twinx()
            self.axes.append((ax1_s, ax2_s))
            self.lines['s_current'], = ax1_s.plot([], [], color='dodgerblue')
            self.lines['s_signal'], = ax2_s.plot([], [], color='limegreen')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _periodic_update(self):
        self.update_chart_data()
        self.after_id = self.after(250, self._periodic_update) # Reduced frequency

    def update_chart_data(self):
        # Create a consistent snapshot of the data under a lock
        with self.app.chart_data_lock:
            time_data = list(self.app.time_history)
            if not time_data:
                return

            if self.controller_mode == 'dual':
                current_a_data = list(self.app.current_history_0000)
                signal_a_data = list(self.app.signal_history_0001)
                current_b_data = list(self.app.current_history_0003)
                signal_b_data = list(self.app.signal_history_0004)
                # Basic validation to prevent crash on race condition
                if not (len(time_data) == len(current_a_data) == len(signal_a_data) == len(current_b_data) == len(signal_b_data)):
                    return # Skip this update cycle
            else: # single
                current_a_data = list(self.app.current_history_0000)
                signal_a_data = list(self.app.signal_history_0001)
                if not (len(time_data) == len(current_a_data) == len(signal_a_data)):
                    return # Skip this update cycle

        # GUI updates should happen outside the lock
        time_data_dt = [datetime.fromtimestamp(t) for t in time_data]

        if self.controller_mode == 'dual':
            self.lines['a_current'].set_data(time_data_dt, current_a_data)
            self.lines['a_signal'].set_data(time_data_dt, signal_a_data)
            self.lines['b_current'].set_data(time_data_dt, current_b_data)
            self.lines['b_signal'].set_data(time_data_dt, signal_b_data)
        else: # single
            self.lines['s_current'].set_data(time_data_dt, current_a_data)
            self.lines['s_signal'].set_data(time_data_dt, signal_a_data)

        # Update X-axis limits and redraw
        end_time = time_data_dt[-1]
        start_time = end_time - timedelta(seconds=20)

        # Set the x-limit on the first subplot; others share the x-axis and will update.
        if self.axes:
            self.axes[0][0].set_xlim(start_time, end_time)

        for ax1, ax2 in self.axes:
            # Autoscale the y-axes only
            ax1.relim()
            ax1.autoscale_view(scalex=False, scaley=True)
            ax2.relim()
            ax2.autoscale_view(scalex=False, scaley=True)

        self.canvas.draw_idle()

    def _save_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[(self.app.get_current_translation("FILE_TYPE_CSV"), "*.csv")],
            title=self.app.get_current_translation("SAVE_DIALOG_TITLE")
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header based on mode
                if self.controller_mode == 'dual':
                    writer.writerow([
                        self.app.get_current_translation("X_AXIS_TIME"),
                        self.app.get_current_translation("LEGEND_CURRENT_A"),
                        self.app.get_current_translation("LEGEND_SIGNAL_A"),
                        self.app.get_current_translation("LEGEND_CURRENT_B"),
                        self.app.get_current_translation("LEGEND_SIGNAL_B")
                    ])
                    for i in range(len(self.app.time_history)):
                        writer.writerow([
                            datetime.fromtimestamp(self.app.time_history[i]).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            self.app.current_history_0000[i],
                            self.app.signal_history_0001[i],
                            self.app.current_history_0003[i],
                            self.app.signal_history_0004[i]
                        ])
                else: # single
                    writer.writerow([
                        self.app.get_current_translation("X_AXIS_TIME"),
                        self.app.get_current_translation("LEGEND_CURRENT_S"),
                        self.app.get_current_translation("LEGEND_SIGNAL_S")
                    ])
                    for i in range(len(self.app.time_history)):
                        writer.writerow([
                            datetime.fromtimestamp(self.app.time_history[i]).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            self.app.current_history_0000[i],
                            self.app.signal_history_0001[i]
                        ])
            messagebox.showinfo(self.app.get_current_translation("INFO_TITLE"),
                                self.app.get_current_translation("CHART_SAVE_SUCCESS_MSG"))
        except Exception as e:
            messagebox.showerror(self.app.get_current_translation("ERROR_TITLE"),
                                 self.app.get_current_translation("CHART_SAVE_ERROR_MSG").format(e=e))

    def _on_closing(self):
        self.after_cancel(self.after_id) # Stop periodic updates
        self.app.chart_window = None # Clear reference in main app
        self.destroy()

    def _update_language(self):
        self.title(self.app.get_current_translation("CHART_WINDOW_TITLE"))
        self.save_button.config(text=self.app.get_current_translation("SAVE_CHART_DATA_BUTTON"))
        
        # Set all text properties for the axes and legends
        if self.controller_mode == 'dual':
            ax1_a, ax2_a = self.axes[0]
            ax1_b, ax2_b = self.axes[1]
            
            ax1_a.set_title(self.app.get_current_translation("CHART_A_TITLE"))
            ax1_b.set_title(self.app.get_current_translation("CHART_B_TITLE"))
            ax1_b.set_xlabel(self.app.get_current_translation("X_AXIS_TIME"))

            # Update labels for lines
            self.lines['a_current'].set_label(self.app.get_current_translation("LEGEND_CURRENT_A"))
            self.lines['a_signal'].set_label(self.app.get_current_translation("LEGEND_SIGNAL_A"))
            self.lines['b_current'].set_label(self.app.get_current_translation("LEGEND_CURRENT_B"))
            self.lines['b_signal'].set_label(self.app.get_current_translation("LEGEND_SIGNAL_B"))

            # Combine and create legends
            lines_a = [self.lines['a_current'], self.lines['a_signal']]
            ax1_a.legend(lines_a, [l.get_label() for l in lines_a], loc='upper left')

            lines_b = [self.lines['b_current'], self.lines['b_signal']]
            ax1_b.legend(lines_b, [l.get_label() for l in lines_b], loc='upper left')

        else: # single
            ax1, ax2 = self.axes[0]
            ax1.set_title(self.app.get_current_translation("CHART_S_TITLE"))
            ax1.set_xlabel(self.app.get_current_translation("X_AXIS_TIME"))
            
            # Update labels for lines
            self.lines['s_current'].set_label(self.app.get_current_translation("LEGEND_CURRENT_S"))
            self.lines['s_signal'].set_label(self.app.get_current_translation("LEGEND_SIGNAL_S"))

            # Combine and create legend
            lines_s = [self.lines['s_current'], self.lines['s_signal']]
            ax1.legend(lines_s, [l.get_label() for l in lines_s], loc='upper left')

        # Common axis properties
        for ax1, ax2 in self.axes:
            ax1.set_ylabel(self.app.get_current_translation("Y_AXIS_CURRENT"), color='dodgerblue')
            ax2.set_ylabel(self.app.get_current_translation("Y_AXIS_SIGNAL"), color='limegreen')
            ax1.tick_params(axis='y', labelcolor='dodgerblue')
            ax2.yaxis.set_label_position("right")
            ax2.yaxis.tick_right()
            ax2.tick_params(axis='y', labelcolor='limegreen')
            ax1.set_ylim(0, 3)
            ax2.set_ylim(0, 100)
            ax1.grid(True)
            ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        
        self.figure.tight_layout()
        self.canvas.draw_idle()

class ModbusMonitorApp:
    # 類級變量，用於獲取當前翻譯，以便於輔助函數使用
    _current_translations = TEXTS["zh"] 

    # --- 雙組控制器參數設定 ---
    writable_params_config = [
        # --- 通用參數 ---
        {'reg': '0006H', 'title_key': 'SIGNAL_SELECTION_1', 'type': 'combobox', 'map_key': 'SIGNAL_SELECTION_MAP_VALUES', 'group': 'common'},
        {'reg': '0007H', 'title_key': 'SIGNAL_SELECTION_2', 'type': 'combobox', 'map_key': 'SIGNAL_SELECTION_MAP_VALUES', 'group': 'common'},
        {'reg': '0008H', 'title_key': 'PANEL_DISPLAY_MODE', 'type': 'combobox', 'map_key': 'PANEL_DISPLAY_MODE_MAP_VALUES', 'group': 'common'},
        {'reg': '0009H', 'title_key': 'RS485_CONTROL_SIGNAL_1', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': False, 'group': 'common'},
        {'reg': '000AH', 'title_key': 'RS485_CONTROL_SIGNAL_2', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': False, 'group': 'common'},
        {'reg': '000BH', 'title_key': 'DEVICE_ADDRESS_ADJUSTMENT', 'type': 'entry', 'min': 1, 'max': 247, 'scale': 1, 'is_int': False, 'group': 'common'},
        {'reg': '000CH', 'title_key': 'DEVICE_BAUDRATE_ADJUSTMENT', 'type': 'combobox', 'map_key': 'DEVICE_BAUDRATE_MAP_VALUES', 'group': 'common'},
        {'reg': '000DH', 'title_key': 'FACTORY_RESET', 'type': 'combobox', 'map_key': 'FACTORY_RESET_MAP_VALUES', 'group': 'common'},
        # --- A組參數 ---
        {'reg': '000EH', 'title_key': 'A_INPUT_SIGNAL_SELECTION', 'type': 'combobox', 'map_key': 'A_INPUT_SIGNAL_SELECTION_MAP_VALUES', 'group': 'a_group'},
        {'reg': '000FH', 'title_key': 'A_FEEDBACK_SIGNAL', 'type': 'combobox', 'map_key': 'FEEDBACK_SIGNAL_MAP_VALUES', 'group': 'a_group'},
        {'reg': '0010H', 'title_key': 'A_MAX_CURRENT', 'type': 'entry', 'min': 0.20, 'max': 3.00, 'scale': 100, 'is_int': False, 'group': 'a_group'},
        {'reg': '0011H', 'title_key': 'A_MIN_CURRENT', 'type': 'entry', 'min': 0.00, 'max': 1.00, 'scale': 100, 'is_int': False, 'group': 'a_group'},
        {'reg': '0012H', 'title_key': 'A_CURRENT_RISE_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'unit_step': 0.1, 'is_int': False, 'group': 'a_group'},
        {'reg': '0013H', 'title_key': 'A_CURRENT_FALL_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'unit_step': 0.1, 'is_int': False, 'group': 'a_group'},
        {'reg': '0014H', 'title_key': 'A_COMMAND_DEAD_ZONE', 'type': 'entry', 'min': 0, 'max': 5, 'scale': 1, 'is_int': True, 'group': 'a_group'},
        {'reg': '0015H', 'title_key': 'A_PWM_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 1000, 'scale': 10, 'unit_step': 10, 'group': 'a_group'},
        {'reg': '0016H', 'title_key': 'A_TREMOR_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 500, 'scale': 10, 'unit_step': 10, 'group': 'a_group'},
        {'reg': '0017H', 'title_key': 'A_DITHER_AMPLITUDE', 'type': 'entry', 'min': 0, 'max': 25, 'scale': 1, 'is_int': True, 'group': 'a_group'},
        # --- B組參數 ---
        {'reg': '0018H', 'title_key': 'B_INPUT_SIGNAL_SELECTION', 'type': 'combobox', 'map_key': 'B_INPUT_SIGNAL_SELECTION_MAP_VALUES', 'group': 'b_group'},
        {'reg': '0019H', 'title_key': 'B_FEEDBACK_SIGNAL', 'type': 'combobox', 'map_key': 'FEEDBACK_SIGNAL_MAP_VALUES', 'group': 'b_group'},
        {'reg': '001AH', 'title_key': 'B_MAX_CURRENT', 'type': 'entry', 'min': 0.20, 'max': 3.00, 'scale': 100, 'is_int': False, 'group': 'b_group'},
        {'reg': '001BH', 'title_key': 'B_MIN_CURRENT', 'type': 'entry', 'min': 0.00, 'max': 1.00, 'scale': 100, 'is_int': False, 'group': 'b_group'},
        {'reg': '001CH', 'title_key': 'B_CURRENT_RISE_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'is_int': False, 'group': 'b_group'},
        {'reg': '001DH', 'title_key': 'B_CURRENT_FALL_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'is_int': False, 'group': 'b_group'},
        {'reg': '001EH', 'title_key': 'B_COMMAND_DEAD_ZONE', 'type': 'entry', 'min': 0, 'max': 5, 'scale': 1, 'is_int': True, 'group': 'b_group'},
        {'reg': '001FH', 'title_key': 'B_PWM_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 1000, 'scale': 10, 'unit_step': 10, 'group': 'b_group'},
        {'reg': '0020H', 'title_key': 'B_TREMOR_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 500, 'scale': 10, 'unit_step': 10, 'group': 'b_group'},
        {'reg': '0021H', 'title_key': 'B_DITHER_AMPLITUDE', 'type': 'entry', 'min': 0, 'max': 25, 'scale': 1, 'is_int': True, 'group': 'b_group'},
        # --- PID參數 ---
        {'reg': '0022H', 'title_key': 'SIGNAL_1_P', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
        {'reg': '0023H', 'title_key': 'SIGNAL_1_I', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
        {'reg': '0024H', 'title_key': 'SIGNAL_1_D', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
        {'reg': '0025H', 'title_key': 'SIGNAL_2_P', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
        {'reg': '0026H', 'title_key': 'SIGNAL_2_I', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
        {'reg': '0027H', 'title_key': 'SIGNAL_2_D', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True, 'group': 'pid'},
    ]

    # --- 單組控制器參數設定 ---
    single_writable_params_config = [
        {'reg': '0003H', 'title_key': 'S_SIGNAL_SELECTION', 'type': 'combobox', 'map_key': 'S_SIGNAL_SELECTION_MAP_VALUES'},
        {'reg': '0004H', 'title_key': 'S_ENABLE_MODE', 'type': 'combobox', 'map_key': 'S_ENABLE_MODE_MAP_VALUES'},
        {'reg': '0005H', 'title_key': 'S_DISPLAY_MODE', 'type': 'combobox', 'map_key': 'S_DISPLAY_MODE_MAP_VALUES'},
        {'reg': '0006H', 'title_key': 'S_485_CONTROL_SIGNAL', 'type': 'entry', 'min': 0, 'max': 100, 'scale': 1, 'is_int': True},
        {'reg': '0007H', 'title_key': 'S_FACTORY_RESET', 'type': 'combobox', 'map_key': 'S_FACTORY_RESET_MAP_VALUES'},
        {'reg': '0008H', 'title_key': 'S_MAX_CURRENT', 'type': 'entry', 'min': 0.00, 'max': 3.00, 'scale': 100},
        {'reg': '0009H', 'title_key': 'S_MIN_CURRENT', 'type': 'entry', 'min': 0.00, 'max': 1.00, 'scale': 100},
        {'reg': '000AH', 'title_key': 'S_CURRENT_RISE_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'unit_step': 0.1},
        {'reg': '000BH', 'title_key': 'S_CURRENT_FALL_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10, 'unit_step': 0.1},
        {'reg': '000CH', 'title_key': 'S_DITHER_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 350, 'scale': 10, 'unit_step': 10},
        {'reg': '000DH', 'title_key': 'S_DEAD_ZONE_SETTING', 'type': 'entry', 'min': 0, 'max': 5, 'scale': 1, 'is_int': True},
    ]

    @staticmethod
    def get_current_translation(key):
        return ModbusMonitorApp._current_translations.get(key, key) # Fallback to key if not found

    def __init__(self, master):
        self.master = master
        self.controller_mode = None
        self.main_widgets_created = False
        self.chart_window = None # For chart window reference

        self.master.withdraw() # Hide main window

        # --- Initialize basic variables ---
        self.current_language_code = tk.StringVar(value="zh")
        self._current_translations = TEXTS[self.current_language_code.get()]
        self.translations = self._current_translations
        self.modbus_master = None
        self.polling_active = False
        self.polling_thread = None
        self.last_status_code_a = None
        self.last_status_code_b = None
        self.saved_parameters = {}
        self.writable_labels, self.writable_entries, self.writable_controls = {}, {}, {}
        self.monitor_labels_info_a, self.monitor_display_controls_a = {}, {}
        self.monitor_labels_info_b, self.monitor_display_controls_b = {}, {}
        if not os.path.exists(PARAMETERS_DIR):
            os.makedirs(PARAMETERS_DIR)

        self.chart_data_lock = threading.Lock()

        # --- Chart Data History ---
        self.MAX_HISTORY_POINTS = 2000 # 200 seconds * 10 samples/second (polling interval is 0.1s)
        self.time_history = deque(maxlen=self.MAX_HISTORY_POINTS)
        self.current_history_0000 = deque(maxlen=self.MAX_HISTORY_POINTS)
        self.signal_history_0001 = deque(maxlen=self.MAX_HISTORY_POINTS)
        self.current_history_0003 = deque(maxlen=self.MAX_HISTORY_POINTS) # For dual mode B group
        self.signal_history_0004 = deque(maxlen=self.MAX_HISTORY_POINTS) # For dual mode B group

        # Show the mode selection dialog and wait for a choice
        self._show_mode_selection_dialog()

        # If the dialog was closed, self.master is destroyed, and the script will terminate.
        # If a mode was selected, proceed with building the main UI.
        if self.controller_mode is None:
            return # Exit __init__ if no mode was selected

        self._setup_main_window()
        self._create_widgets()
        self._refresh_ports()
        self.main_widgets_created = True
        self.current_language_code.trace_add("write", self._update_all_text)
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.master.deiconify() # Show the now fully configured window

    def _setup_main_window(self):
        """Configure the main window after mode selection."""
        app_title_key = "APP_TITLE_DUAL" if self.controller_mode == 'dual' else "APP_TITLE_SINGLE"
        self.master.title(self.get_current_translation(app_title_key))
        self.master.geometry("960x1000")
        self.master.resizable(True, True)

    def _show_mode_selection_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title(TEXTS["zh"]["MODE_SELECTION_TITLE"]) # Use a fixed language for this initial dialog
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        # Do not make it transient to the hidden master window
        dialog.grab_set()

        # Center the dialog on the screen
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog.winfo_width() // 2)
        y = (screen_height // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        label = ttk.Label(dialog, text=TEXTS["zh"]["MODE_SELECTION_PROMPT"], font=("", 12))
        label.pack(pady=20)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        def select_mode(mode):
            self.controller_mode = mode
            dialog.destroy()

        dual_button = ttk.Button(button_frame, text=TEXTS["zh"]["DUAL_CONTROLLER_BUTTON"], command=lambda: select_mode('dual'), width=20)
        dual_button.pack(side=tk.LEFT, padx=10)

        single_button = ttk.Button(button_frame, text=TEXTS["zh"]["SINGLE_CONTROLLER_BUTTON"], command=lambda: select_mode('single'), width=20)
        single_button.pack(side=tk.LEFT, padx=10)

        # If the user closes the dialog window, destroy the main window to exit the app
        dialog.protocol("WM_DELETE_WINDOW", self.master.destroy)

        dialog.wait_window() # Wait until the dialog is closed or the master is destroyed

    def _on_closing(self):
        """處理視窗關閉事件，停止輪詢線程並關閉Modbus連接。"""
        if self.chart_window: 
            self.chart_window.destroy()

        # Ensure polling stops if active
        if self.polling_active:
            self.polling_active = False # Signal thread to stop
            if self.polling_thread and self.polling_thread.is_alive():
                self.polling_thread.join(timeout=1.0) # Wait for thread to finish
            self.polling_thread = None # Clear thread reference
            self._clear_monitor_area() # Clear monitor display on exit

        if self.modbus_master:
            try:
                self.modbus_master.close()
                self.modbus_master = None
                global MODBUS_MASTER # Also clear global reference
                MODBUS_MASTER = None
            except Exception as e:
                print(f"Error closing Modbus master on exit: {e}") # Print to console, no messagebox on app close
        self.master.destroy()

    def _toggle_chart_window(self):
        """Toggle the real-time chart window."""
        if self.chart_window and self.chart_window.winfo_exists():
            self.chart_window.destroy()
            self.chart_window = None
            if hasattr(self, 'chart_button'):
                self.chart_button.config(text=self.get_current_translation("SHOW_CHART_BUTTON"), bootstyle="primary_toolbutton")
        else:
            self.chart_window = RealtimeChartWindow(self.master, self) # Pass self (ModbusMonitorApp instance)
            if hasattr(self, 'chart_button'):
                self.chart_button.config(text=self.get_current_translation("CLOSE_CHART_BUTTON"), bootstyle="primary_button")


    def _create_widgets(self):
        """創建所有GUI元件並佈局。"""
        # --- 主窗口網格佈局設定 ---
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # --- 主內容框架 (固定寬度) ---
        self.main_content_frame = ttk.Frame(self.master)
        self.main_content_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # --- 頂部區域框架 (通用) ---
        top_frame = ttk.Frame(self.main_content_frame)
        top_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        top_frame.grid_columnconfigure(0, weight=1)

        # --- 模式切換 (Combobox) ---
        self.mode_switch_frame = ttk.LabelFrame(top_frame, text=self.get_current_translation("SWITCH_MODE_FRAME_TEXT"), padding="10")
        self.mode_switch_frame.pack(side=tk.RIGHT, padx=(10, 0))
        self.mode_combobox_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(self.mode_switch_frame, textvariable=self.mode_combobox_var, values=[self.get_current_translation("DUAL_MODE_OPTION"), self.get_current_translation("SINGLE_MODE_OPTION")], state="readonly", width=12)
        self.mode_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_select)
        # Set initial value
        current_mode_text = self.get_current_translation("DUAL_MODE_OPTION") if self.controller_mode == 'dual' else self.get_current_translation("SINGLE_MODE_OPTION")
        self.mode_combobox_var.set(current_mode_text)

        # --- 語言選擇 (通用) ---
        self.language_frame = ttk.LabelFrame(top_frame, text=self.get_current_translation("LANGUAGE_LABEL"), padding="10")
        self.language_frame.pack(side=tk.RIGHT, padx=(10, 0))
        self.language_combobox_var = tk.StringVar(value="中文")
        self.language_combobox = ttk.Combobox(self.language_frame, values=["中文", "English"], state="readonly", width=7, textvariable=self.language_combobox_var)
        self.language_combobox.grid(row=0, column=0, padx=5, pady=5)
        self.language_combobox.bind("<<ComboboxSelected>>", self._on_language_select)

        # --- Modbus通訊參數設置區域 (通用) ---
        self.modbus_params_frame = ttk.LabelFrame(top_frame, text=self.get_current_translation("MODBUS_PARAMS_FRAME_TEXT"), padding="10")
        self.modbus_params_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # ... (內容與原版相同)
        self.com_port_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("COM_PORT_LABEL"))
        self.com_port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_combobox = ttk.Combobox(self.modbus_params_frame, state="readonly", width=10)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.baudrate_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("BAUDRATE_LABEL"))
        self.baudrate_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.baudrate_combobox = ttk.Combobox(self.modbus_params_frame, values=[4800, 9600, 19200, 38400, 57600], state="readonly", width=8)
        self.baudrate_combobox.set(19200)
        self.baudrate_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.slave_id_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("SLAVE_ID_LABEL"))
        self.slave_id_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.slave_id_var = tk.StringVar(value="1")
        self.slave_id_spinbox = ttk.Spinbox(self.modbus_params_frame, from_=1, to=247, increment=1, width=5, textvariable=self.slave_id_var)
        self.slave_id_spinbox.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        self.refresh_ports_button = ttk.Button(self.modbus_params_frame, text=self.get_current_translation("REFRESH_PORTS_BUTTON"), bootstyle="primary.Outline", command=self._refresh_ports)
        self.refresh_ports_button.grid(row=0, column=6, padx=5, pady=5)
        self.connect_button = ttk.Checkbutton(self.modbus_params_frame, text=self.get_current_translation("CONNECT_BUTTON"), bootstyle="primary_toolbutton", command=self._toggle_connection)
        self.connect_button.grid(row=0, column=7, padx=5, pady=5, sticky=tk.E)

        # --- 分隔線 ---
        ttk.Separator(self.main_content_frame, orient='horizontal').grid(row=1, column=0, pady=5, sticky='ew')

        # --- 動態內容框架 ---
        self.dynamic_content_frame = ttk.Frame(self.main_content_frame)
        self.dynamic_content_frame.grid(row=2, column=0, sticky='nsew')
        self.dynamic_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(2, weight=1)

        # 根據模式建立對應的UI
        self._build_ui_for_mode()

    def _build_ui_for_mode(self):
        """根據 self.controller_mode 建立對應的 UI。"""
        # 清除舊的動態內容
        for widget in self.dynamic_content_frame.winfo_children():
            widget.destroy()

        if self.controller_mode == 'dual':
            self._create_dual_controller_ui()
        elif self.controller_mode == 'single':
            self._create_single_controller_ui()

    def _create_dual_controller_ui(self):
        """為雙組控制器創建GUI元件。"""
        self.dynamic_content_frame.grid_rowconfigure(0, weight=0)  # 即時監控
        self.dynamic_content_frame.grid_rowconfigure(1, weight=1)  # 可寫入參數
        self.dynamic_content_frame.grid_rowconfigure(2, weight=0)  # 圖表區

        # --- 即時監控區框架 ---
        monitor_area_frame = ttk.Frame(self.dynamic_content_frame)
        monitor_area_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        monitor_area_frame.grid_columnconfigure(0, weight=1)
        monitor_area_frame.grid_columnconfigure(1, weight=1)
        
        # Monitor frames on row 0, below the button
        self.monitor_frame_a = ttk.LabelFrame(monitor_area_frame, text=self.get_current_translation("MONITOR_AREA_A_FRAME_TEXT"), padding="10")
        self.monitor_frame_a.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=(5,0))
        self.monitor_frame_b = ttk.LabelFrame(monitor_area_frame, text=self.get_current_translation("MONITOR_AREA_B_FRAME_TEXT"), padding="10")
        self.monitor_frame_b.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=(5,0))

        # Chart Button on row 1, aligned to the right
        self.chart_button = ttk.Checkbutton(monitor_area_frame, text=self.get_current_translation("SHOW_CHART_BUTTON"), bootstyle="primary_toolbutton", command=self._toggle_chart_window)
        self.chart_button.grid(row=0, column=1, sticky='ne', padx=5, pady=20)

        self.monitor_labels_info_a, self.monitor_display_controls_a = self._create_monitor_widgets(self.monitor_frame_a, [("0000H", "OUTPUT_CURRENT_LABEL", "A"), ("0001H", "INPUT_SIGNAL_LABEL", "%"), ("0002H", "CURRENT_STATUS_LABEL", "")])
        self.monitor_labels_info_b, self.monitor_display_controls_b = self._create_monitor_widgets(self.monitor_frame_b, [("0003H", "OUTPUT_CURRENT_LABEL", "A"), ("0004H", "INPUT_SIGNAL_LABEL", "%"), ("0005H", "CURRENT_STATUS_LABEL", "")])
        self._clear_monitor_area()

        # --- 可寫入參數區 (Notebook) ---
        self.writable_params_area_frame = ttk.LabelFrame(self.dynamic_content_frame, text=self.get_current_translation("WRITABLE_PARAMS_FRAME_TEXT"), padding="10")
        self.writable_params_area_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.writable_params_area_frame.grid_rowconfigure(0, weight=1)
        self.writable_params_area_frame.grid_columnconfigure(0, weight=1)

        self.writable_params_notebook = ttk.Notebook(self.writable_params_area_frame)
        self.writable_params_notebook.grid(row=0, column=0, sticky="nsew")

        self.common_params_frame = ttk.Frame(self.writable_params_notebook, padding=5)
        self.a_group_params_frame = ttk.Frame(self.writable_params_notebook, padding=5)
        self.b_group_params_frame = ttk.Frame(self.writable_params_notebook, padding=5)
        self.pid_params_frame = ttk.Frame(self.writable_params_notebook, padding=5)

        self.writable_params_notebook.add(self.common_params_frame, text=self.get_current_translation("COMMON_PARAMS_FRAME_TEXT"))
        self.writable_params_notebook.add(self.a_group_params_frame, text=self.get_current_translation("A_GROUP_PARAMS_FRAME_TEXT"))
        self.writable_params_notebook.add(self.b_group_params_frame, text=self.get_current_translation("B_GROUP_PARAMS_FRAME_TEXT"))
        self.writable_params_notebook.add(self.pid_params_frame, text=self.get_current_translation("PID_PARAMS_FRAME_TEXT"))

        tab_frames = {
            "common": self.common_params_frame,
            "a_group": self.a_group_params_frame,
            "b_group": self.b_group_params_frame,
            "pid": self.pid_params_frame,
        }

        self.writable_labels, self.writable_entries, self.writable_controls = {}, {}, {}
        self._create_parameter_controls(self.writable_params_config, tab_frames)

        # --- 底部批量操作按鈕 ---
        self._create_batch_buttons(self.writable_params_area_frame, 1)

        # --- 圖表區 ---
        self.chart_area_frame = ttk.Frame(self.dynamic_content_frame)
        self.chart_area_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        self.chart_area_frame.grid_rowconfigure(0, weight=1)
        self.chart_area_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame = ttk.LabelFrame(self.chart_area_frame, text=self.get_current_translation("CONTROLLER_MODE_CHART_FRAME_TEXT"))
        self.chart_frame.grid(row=0, column=0, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_canvas = tk.Canvas(self.chart_frame, bg='white', highlightthickness=0)
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")

    def _create_single_controller_ui(self):
        """為單組控制器創建GUI元件。"""
        self.dynamic_content_frame.grid_rowconfigure(0, weight=0)  # 即時監控
        self.dynamic_content_frame.grid_rowconfigure(1, weight=1)  # 可寫入參數
        self.dynamic_content_frame.grid_rowconfigure(2, weight=1)  # 圖表區

        # --- 即時監控區框架 ---
        monitor_area_frame = ttk.Frame(self.dynamic_content_frame)
        monitor_area_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        monitor_area_frame.grid_columnconfigure(0, weight=1)
        monitor_area_frame.grid_columnconfigure(1, weight=0)

        self.monitor_frame_a = ttk.LabelFrame(monitor_area_frame, text=self.get_current_translation("MONITOR_AREA_SINGLE_FRAME_TEXT"), padding="10")
        self.monitor_frame_a.grid(row=0, column=0, sticky='nsew', pady=(5,0))

        # Chart Button
        self.chart_button = ttk.Checkbutton(monitor_area_frame, text=self.get_current_translation("SHOW_CHART_BUTTON"), bootstyle="primary_toolbutton", command=self._toggle_chart_window)
        self.chart_button.grid(row=0, column=0, sticky='ne', padx=5, pady=20)

        self.monitor_labels_info_a, self.monitor_display_controls_a = self._create_monitor_widgets(self.monitor_frame_a, [("0000H", "OUTPUT_CURRENT_LABEL", "A"), ("0001H", "INPUT_SIGNAL_LABEL", "%"), ("0002H", "CURRENT_STATUS_LABEL", "")])
        self.monitor_labels_info_b, self.monitor_display_controls_b = {}, {}
        self._clear_monitor_area()

        # --- 可寫入參數區 ---
        self.writable_params_area_frame = ttk.LabelFrame(self.dynamic_content_frame, text=self.get_current_translation("WRITABLE_PARAMS_FRAME_TEXT"), padding="10")
        self.writable_params_area_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        self.writable_params_area_frame.grid_rowconfigure(0, weight=1)
        self.writable_params_area_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(self.writable_params_area_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.writable_params_area_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        canvas.bind("<Configure>", lambda e, c=canvas, w=canvas_window: c.itemconfig(w, width=e.width))

        self.writable_labels, self.writable_entries, self.writable_controls = {}, {}, {}
        self._create_parameter_controls(self.single_writable_params_config, {"single": scrollable_frame})

        self._create_batch_buttons(self.writable_params_area_frame, 1)

        # --- 圖表區 (for single controller) ---
        self.chart_area_frame = ttk.Frame(self.dynamic_content_frame)
        self.chart_area_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        self.chart_area_frame.grid_rowconfigure(0, weight=1)
        self.chart_area_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame = ttk.LabelFrame(self.chart_area_frame, text=self.get_current_translation("CONTROLLER_MODE_CHART_FRAME_TEXT"))
        self.chart_frame.grid(row=0, column=0, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_canvas = tk.Canvas(self.chart_frame, bg='white', highlightthickness=0)
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")


    def _create_parameter_controls(self, config, parent_frames):
        """通用函數: 根據設定檔和父框架創建參數控制元件。"""
        # Group parameters by their 'group' key or use a single group
        grouped_params = {}
        for param in config:
            group = param.get('group', 'single') # Default to 'single' if no group
            if group not in grouped_params:
                grouped_params[group] = []
            grouped_params[group].append(param)

        for group_name, params_in_group in grouped_params.items():
            parent_frame_container = parent_frames.get(group_name)
            if not parent_frame_container: continue

            # Determine if we are in a notebook tab or a direct scrollable frame
            if isinstance(parent_frame_container, ttk.Frame) and hasattr(parent_frame_container, 'scrollable_frame'):
                 parent_frame = parent_frame_container.scrollable_frame
            else: # It's the scrollable_frame itself
                 parent_frame = parent_frame_container

            # Configure columns for two-column layout
            parent_frame.grid_columnconfigure(0, weight=1)
            parent_frame.grid_columnconfigure(1, weight=1)
            parent_frame.grid_columnconfigure(2, weight=1)
            parent_frame.grid_columnconfigure(3, weight=1)

            num_params = len(params_in_group)
            midpoint = math.ceil(num_params / 2)

            # Create controls in two columns
            for i, param in enumerate(params_in_group):
                reg_hex = param['reg']
                if i < midpoint:
                    col_offset = 0
                    row_num = i
                else:
                    col_offset = 2
                    row_num = i - midpoint

                label = ttk.Label(parent_frame, text=f"{self.get_current_translation(param['title_key'])} ({reg_hex})")
                label.grid(row=row_num, column=col_offset, padx=5, pady=5, sticky=tk.W)
                self.writable_labels[reg_hex] = label

                var = tk.StringVar()
                self.writable_entries[reg_hex] = var
                control = None

                if param['type'] == 'combobox':
                    param['map'] = self.translations.get(param['map_key'], {})
                    param['rev_map'] = {v: k for k, v in param['map'].items()}
                    control = ttk.Combobox(parent_frame, textvariable=var, values=list(param['map'].values()), state="readonly", width=15)
                elif param['type'] in ['entry', 'entry_scaled', 'spinbox']:
                    control = ttk.Entry(parent_frame, textvariable=var, width=17)

                if control:
                    control.grid(row=row_num, column=col_offset + 1, padx=5, pady=5, sticky=tk.W)
                    self.writable_controls[reg_hex] = control

    def _create_batch_buttons(self, parent, row):
        """創建批量操作按鈕。"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.save_params_button = ttk.Button(buttons_frame, text=self.get_current_translation("SAVE_PARAMS_BUTTON"), bootstyle="primary.Outline", command=self._save_parameters_to_file, width=15)
        self.save_params_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.load_params_button = ttk.Button(buttons_frame, text=self.get_current_translation("LOAD_PARAMS_BUTTON"), bootstyle="primary.Outline", command=self._load_parameters_from_file, width=15)
        self.load_params_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.batch_write_button = ttk.Button(buttons_frame, text=self.get_current_translation("BATCH_WRITE_BUTTON"), bootstyle="primary.Outline", command=self._batch_write_parameters, width=15)
        self.batch_write_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    def _on_mode_select(self, event=None):
        """處理模式切換請求。"""
        selected_mode_str = self.mode_combobox_var.get()
        target_mode = 'dual' if selected_mode_str == self.get_current_translation("DUAL_MODE_OPTION") else 'single'

        if target_mode == self.controller_mode:
            return # Do nothing if the mode is not actually changed

        if messagebox.askyesno(self.get_current_translation("CONFIRM_SWITCH_MODE_TITLE"), self.get_current_translation("CONFIRM_SWITCH_MODE_MSG")):
            # Disconnect if connected
            if self.modbus_master:
                self._toggle_connection() # This will handle disconnection and UI clearing

            # Switch mode
            self.controller_mode = target_mode
            
            # Update title
            app_title_key = "APP_TITLE_DUAL" if self.controller_mode == 'dual' else "APP_TITLE_SINGLE"
            self.master.title(self.get_current_translation(app_title_key))

            # Re-build UI for the new mode
            self._build_ui_for_mode()
            # Update all text for the new UI
            self._update_all_text()
        else:
            # If user cancels, revert the combobox to the current mode
            current_mode_text = self.get_current_translation("DUAL_MODE_OPTION") if self.controller_mode == 'dual' else self.get_current_translation("SINGLE_MODE_OPTION")
            self.mode_combobox_var.set(current_mode_text)

    def _create_monitor_widgets(self, parent_frame, config):
        # Configure grid for the parent frame
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1) # Row for meters
        parent_frame.grid_rowconfigure(1, weight=1) # Row for status

        labels_info = {}
        display_controls = {}

        # --- Create and place Meter 1: Output Current ---
        current_config = next((c for c in config if c[1] == "OUTPUT_CURRENT_LABEL"), None)
        if current_config:
            reg_hex_current, title_key_current, unit_current = current_config
            initial_subtext_current = self.get_current_translation(title_key_current)
            current_meter = ttk.Meter(
                master=parent_frame,    
                metersize=160,
                padding=0,
                amountused=0,
                amounttotal=3000,
                textright='mA',
                subtext=initial_subtext_current,
                bootstyle='primary',
                metertype="semi",
                interactive=False,
                amountformat='{:,}'
            )
            current_meter.grid(row=0, column=0, sticky='nsew', padx=5, pady=0)
            labels_info[reg_hex_current] = {'title_label': None, 'unit': unit_current, 'title_key': title_key_current}
            display_controls[reg_hex_current] = current_meter

        # --- Create and place Meter 2: Input Signal ---
        signal_config = next((c for c in config if c[1] == "INPUT_SIGNAL_LABEL"), None)
        if signal_config:
            reg_hex_signal, title_key_signal, unit_signal = signal_config
            initial_subtext_signal = self.get_current_translation(title_key_signal)
            signal_meter = ttk.Meter(
                master=parent_frame,
                metersize=160,
                padding=0,
                amountused=0,
                amounttotal=100,
                textright='%',
                subtext=initial_subtext_signal,
                bootstyle='success',
                metertype="semi",
                interactive=False,
                # amountformat='{:.1f}'
            )
            signal_meter.grid(row=0, column=1, sticky='nsew', padx=5, pady=0)
            labels_info[reg_hex_signal] = {'title_label': None, 'unit': unit_signal, 'title_key': title_key_signal}
            display_controls[reg_hex_signal] = signal_meter

        # --- Create and place Status Display ---
        status_config = next((c for c in config if c[1] == "CURRENT_STATUS_LABEL"), None)
        if status_config:
            reg_hex_status, title_key_status, unit_status = status_config
            initial_subtext_status = self.get_current_translation("CURRENT_STATUS_LABEL")
            status_frame = ttk.LabelFrame(parent_frame, text=initial_subtext_status, padding=(10, 5))
            status_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=0, pady=0)
            status_label = ttk.Label(status_frame, text="----", anchor="center", font=('Arial', 16, 'bold'))
            status_label.pack(expand=True, fill='both')
            labels_info[reg_hex_status] = {'title_label': status_frame, 'unit': unit_status, 'title_key': title_key_status}
            display_controls[reg_hex_status] = status_label

        return labels_info, display_controls


    def _on_language_select(self, event=None):
        """處理語言選擇事件，更新 current_language_code 並觸發界面更新。"""
        selected_lang_display = self.language_combobox_var.get()
        if selected_lang_display == "中文":
            self.current_language_code.set("zh")
        elif selected_lang_display == "English":
            self.current_language_code.set("en")
        
        # _update_all_text will be called by the trace on current_language_code

    def _update_all_text(self, *args):
        """根據當前語言更新所有GUI元件的文字。"""
        if not self.main_widgets_created:
            return
            
        ModbusMonitorApp._current_translations = TEXTS[self.current_language_code.get()]
        self.translations = ModbusMonitorApp._current_translations

        app_title_key = "APP_TITLE_DUAL" if self.controller_mode == 'dual' else "APP_TITLE_SINGLE"
        self.master.title(self.translations[app_title_key])
        
        # Update common widgets
        self.modbus_params_frame.config(text=self.translations["MODBUS_PARAMS_FRAME_TEXT"])
        self.com_port_label.config(text=self.translations["COM_PORT_LABEL"])
        self.baudrate_label.config(text=self.translations["BAUDRATE_LABEL"])
        self.slave_id_label.config(text=self.translations["SLAVE_ID_LABEL"])
        self.refresh_ports_button.config(text=self.translations["REFRESH_PORTS_BUTTON"])
        self.connect_button.config(text=self.translations["DISCONNECT_BUTTON"] if self.modbus_master else self.translations["CONNECT_BUTTON"])
        self.language_frame.config(text=self.translations["LANGUAGE_LABEL"])
        
        # Update mode switch combobox
        self.mode_switch_frame.config(text=self.get_current_translation("SWITCH_MODE_FRAME_TEXT"))
        dual_text = self.translations["DUAL_MODE_OPTION"]
        single_text = self.translations["SINGLE_MODE_OPTION"]
        self.mode_combobox.config(values=[dual_text, single_text])
        if self.controller_mode == 'dual':
            self.mode_combobox_var.set(dual_text)
        else:
            self.mode_combobox_var.set(single_text)

        self.save_params_button.config(text=self.translations["SAVE_PARAMS_BUTTON"])
        self.load_params_button.config(text=self.translations["LOAD_PARAMS_BUTTON"])
        self.batch_write_button.config(text=self.translations["BATCH_WRITE_BUTTON"])
        if hasattr(self, 'chart_button'):
            self.chart_button.config(text=self.translations["CLOSE_CHART_BUTTON"]) if self.chart_window and self.chart_window.winfo_exists() else self.chart_button.config(text=self.translations["SHOW_CHART_BUTTON"])


        # Update mode-specific UI
        if self.controller_mode == 'dual':
            self.monitor_frame_a.config(text=self.translations["MONITOR_AREA_A_FRAME_TEXT"])
            self.monitor_frame_b.config(text=self.translations["MONITOR_AREA_B_FRAME_TEXT"])
            self.writable_params_area_frame.config(text=self.translations["WRITABLE_PARAMS_FRAME_TEXT"])
            self.writable_params_notebook.tab(self.common_params_frame, text=self.translations["COMMON_PARAMS_FRAME_TEXT"])
            self.writable_params_notebook.tab(self.a_group_params_frame, text=self.translations["A_GROUP_PARAMS_FRAME_TEXT"])
            self.writable_params_notebook.tab(self.b_group_params_frame, text=self.translations["B_GROUP_PARAMS_FRAME_TEXT"])
            self.writable_params_notebook.tab(self.pid_params_frame, text=self.translations["PID_PARAMS_FRAME_TEXT"])
            self.chart_frame.config(text=self.translations["CONTROLLER_MODE_CHART_FRAME_TEXT"])
            
            # Update monitor meter subtext
            self.monitor_display_controls_a['0000H'].configure(subtext=self.translations["OUTPUT_CURRENT_LABEL"])
            self.monitor_display_controls_a['0001H'].configure(subtext=self.translations["INPUT_SIGNAL_LABEL"])
            self.monitor_display_controls_b['0003H'].configure(subtext=self.translations["OUTPUT_CURRENT_LABEL"])
            self.monitor_display_controls_b['0004H'].configure(subtext=self.translations["INPUT_SIGNAL_LABEL"])

            # Update monitor status text
            # Update monitor status text
            self.monitor_labels_info_a['0002H']['title_label'].config(text=self.translations["CURRENT_STATUS_LABEL"])
            if hasattr(self, 'last_status_code_a') and self.last_status_code_a is not None:
                status_text_a = self.translations["STATUS_MAP_VALUES"].get(self.last_status_code_a, self.translations["UNKNOWN_STATUS"])
                self.monitor_display_controls_a['0002H'].config(text=status_text_a)
            
            self.monitor_labels_info_b['0005H']['title_label'].config(text=self.translations["CURRENT_STATUS_LABEL"])
            if hasattr(self, 'last_status_code_b') and self.last_status_code_b is not None:
                status_text_b = self.translations["STATUS_MAP_VALUES"].get(self.last_status_code_b, self.translations["UNKNOWN_STATUS"])
                self.monitor_display_controls_b['0005H'].config(text=status_text_b)

            config = self.writable_params_config
            self._draw_chart()

        elif self.controller_mode == 'single':
            self.monitor_frame_a.config(text=self.translations["MONITOR_AREA_SINGLE_FRAME_TEXT"])
            self.writable_params_area_frame.config(text=self.translations["WRITABLE_PARAMS_FRAME_TEXT"])
            self.chart_frame.config(text=self.translations["CONTROLLER_MODE_CHART_FRAME_TEXT"])
            
            # Update monitor meter subtext
            self.monitor_display_controls_a['0000H'].configure(subtext=self.translations["OUTPUT_CURRENT_LABEL"])
            self.monitor_display_controls_a['0001H'].configure(subtext=self.translations["INPUT_SIGNAL_LABEL"])

            # Update monitor status text
            self.monitor_labels_info_a['0002H']['title_label'].config(text=self.translations["CURRENT_STATUS_LABEL"])
            if hasattr(self, 'last_status_code_a') and self.last_status_code_a is not None:
                status_text_a = self.translations["S_STATUS_MAP_VALUES"].get(self.last_status_code_a, self.translations["UNKNOWN_STATUS"])
                self.monitor_display_controls_a['0002H'].config(text=status_text_a)
            
            config = self.single_writable_params_config
            self._draw_single_controller_chart()

        # Update writable parameters labels and combobox values
        for param_config in config:
            reg_hex = param_config['reg']
            if reg_hex in self.writable_labels:
                self.writable_labels[reg_hex].config(text=f"{self.translations.get(param_config['title_key'])} ({reg_hex})")
            
            if param_config['type'] == 'combobox' and reg_hex in self.writable_controls:
                new_map_values = self.translations[param_config['map_key']]
                current_numeric_value = None
                
                if 'rev_map' in param_config:
                    current_display_text = self.writable_entries[reg_hex].get()
                    current_numeric_value = param_config['rev_map'].get(current_display_text)

                self.writable_controls[reg_hex].config(values=list(new_map_values.values()))
                param_config['map'] = new_map_values
                param_config['rev_map'] = {v: k for k, v in new_map_values.items()}

                if current_numeric_value is not None:
                    self.writable_entries[reg_hex].set(new_map_values.get(current_numeric_value, ""))
                else:
                    self.writable_entries[reg_hex].set("")

        # Update chart window language if it exists
        if self.chart_window and self.chart_window.winfo_exists():
            self.chart_window._update_language()

    def _get_single_controller_chart_xaxis_properties(self):
        title = self.get_current_translation("S_SIGNAL_SELECTION")
        min_label, max_label, mid_label = '0%', '100%', '50%'

        try:
            mode_map = self.translations.get("S_SIGNAL_SELECTION_MAP_VALUES", {})
            mode_str = self.writable_entries['0003H'].get()
            
            if mode_str == mode_map.get(0): # 0-10V
                min_label, max_label, mid_label = '0V', '10V', '5V'
            elif mode_str == mode_map.get(1): # 0-5V
                min_label, max_label, mid_label = '0V', '5V', '2.5V'
            elif mode_str == mode_map.get(2): # 4-20mA
                min_label, max_label, mid_label = '4mA', '20mA', '12mA'

        except Exception as e:
            print(f"Error in _get_single_controller_chart_xaxis_properties: {e}")

        return {'title': title, 'min_label': min_label, 'max_label': max_label, 'mid_label': mid_label}

    def _draw_single_controller_chart(self):
        if not hasattr(self, 'chart_canvas') or not self.chart_canvas.winfo_exists():
            return
        
        self.chart_canvas.delete("all")
        canvas_width = self.chart_canvas.winfo_width()
        canvas_height = self.chart_canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1: # Not visible yet
            return

        # 參數
        try:
            max_current = float(self.writable_entries['0008H'].get())
            min_current = float(self.writable_entries['0009H'].get())
            dead_zone = float(self.writable_entries['000DH'].get())
        except (ValueError, KeyError):
            return # Not all params are available

        xaxis_props = self._get_single_controller_chart_xaxis_properties()
        max_y_val = 3.0
        chart_w, chart_h = 250, canvas_height * 0.5
        chart_x_start, chart_y_start = (canvas_width - chart_w) / 2, canvas_height * 0.25

        def map_x(p): return chart_x_start + (p / 100.0) * chart_w
        def map_y(c): return chart_y_start + chart_h * (1 - (c / max_y_val))

        # 繪製外框和座標軸
        self.chart_canvas.create_rectangle(chart_x_start, chart_y_start, chart_x_start + chart_w, chart_y_start + chart_h, outline="black")
        self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start + chart_w, chart_y_start + chart_h)
        self.chart_canvas.create_line(chart_x_start, chart_y_start, chart_x_start, chart_y_start + chart_h)

        # 座標軸標籤
        self.chart_canvas.create_text(chart_x_start, chart_y_start + chart_h + 5, text=xaxis_props['min_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + chart_w, chart_y_start + chart_h + 5, text=xaxis_props['max_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + chart_w / 2, chart_y_start + chart_h + 20, text=xaxis_props['title'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start + chart_h, text="0A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start, text=f"{max_y_val:.1f}A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 20, chart_y_start + chart_h / 2, text=self.get_current_translation("CURRENT"), anchor=tk.CENTER, angle=90)

        # 格線
        for p in range(10, 100, 10): self.chart_canvas.create_line(map_x(p), chart_y_start, map_x(p), chart_y_start + chart_h, fill="lightgray", dash=(2, 2))
        for c in [0.5, 1.0, 1.5, 2.0, 2.5]: self.chart_canvas.create_line(chart_x_start, map_y(c), chart_x_start + chart_w, map_y(c), fill="lightgray", dash=(2, 2))

        # 特性曲線
        points = [
            (map_x(0), map_y(0)),
            (map_x(dead_zone), map_y(0)),
            (map_x(dead_zone), map_y(min_current)),
            (map_x(100), map_y(max_current))
        ]
        self.chart_canvas.create_line(points, fill="Coral", width=2)

        # 參數文字
        text_x = chart_x_start + chart_w + 10
        text_y = chart_y_start + 10
        self.chart_canvas.create_text(text_x, text_y, anchor=tk.W, text=f"{self.get_current_translation('S_MAX_CURRENT').split('(')[0]}: {max_current:.2f}A", font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x, text_y + 15, anchor=tk.W, text=f"{self.get_current_translation('S_MIN_CURRENT').split('(')[0]}: {min_current:.2f}A", font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x, text_y + 30, anchor=tk.W, text=f"{self.get_current_translation('S_DEAD_ZONE_SETTING').split('(')[0]}: {dead_zone:.0f}%", font=("Arial", 8), fill="Coral")


    def _get_chart_xaxis_properties(self, group):
        """
        根據組別 ('A' 或 'B') 和相關參數確定X軸的標題和刻度。
        :param group: 'A' 或 'B'
        :return: dict with keys 'title', 'min_label', 'max_label', 'mid_label'
        """
        title = self.get_current_translation("INPUT_SIGNAL")
        min_label = '0%'
        max_label = '100%'
        mid_label = '50%'

        try:
            analog_mode_map = self.translations.get("SIGNAL_SELECTION_MAP_VALUES", {})

            def calculate_mid_label(min_l, max_l):
                if 'V' in max_l:
                    min_val = float(min_l.replace('V', ''))
                    max_val = float(max_l.replace('V', ''))
                    mid_val = (min_val + max_val) / 2
                    return f"{mid_val:.1f}V"
                elif 'mA' in max_l:
                    min_val = float(min_l.replace('mA', ''))
                    max_val = float(max_l.replace('mA', ''))
                    mid_val = (min_val + max_val) / 2
                    return f"{mid_val:.0f}mA"
                return '50%'

            if group == 'A':
                a_input_signal_map = self.translations.get("A_INPUT_SIGNAL_SELECTION_MAP_VALUES", {})
                source_str = self.writable_entries['000EH'].get()
                
                if source_str == a_input_signal_map.get(1):  # "第一組485"
                    title = source_str
                elif source_str == a_input_signal_map.get(0):  # "信號 1"
                    title = source_str
                    analog_mode_str = self.writable_entries['0006H'].get()
                    if analog_mode_str == analog_mode_map.get(0): min_label, max_label = '0V', '10V'
                    elif analog_mode_str == analog_mode_map.get(1): min_label, max_label = '0V', '5V'
                    elif analog_mode_str == analog_mode_map.get(2): min_label, max_label = '4mA', '20mA'

            elif group == 'B':
                b_input_signal_map = self.translations.get("B_INPUT_SIGNAL_SELECTION_MAP_VALUES", {})
                source_str = self.writable_entries['0018H'].get()

                if source_str == b_input_signal_map.get(4):  # "第二組485"
                    title = source_str
                elif source_str == b_input_signal_map.get(3):  # "第一組485"
                    title = source_str
                elif source_str == b_input_signal_map.get(2):  # "信號 2"
                    title = source_str
                    analog_mode_str = self.writable_entries['0007H'].get() # 信號2對應0007H
                    if analog_mode_str == analog_mode_map.get(0): min_label, max_label = '0V', '10V'
                    elif analog_mode_str == analog_mode_map.get(1): min_label, max_label = '0V', '5V'
                    elif analog_mode_str == analog_mode_map.get(2): min_label, max_label = '4mA', '20mA'
                elif source_str == b_input_signal_map.get(1):  # "信號 1"
                    title = source_str
                    analog_mode_str = self.writable_entries['0006H'].get() # 信號1對應0006H
                    if analog_mode_str == analog_mode_map.get(0): min_label, max_label = '0V', '10V'
                    elif analog_mode_str == analog_mode_map.get(1): min_label, max_label = '0V', '5V'
                    elif analog_mode_str == analog_mode_map.get(2): min_label, max_label = '4mA', '20mA'
            
            mid_label = calculate_mid_label(min_label, max_label)

        except Exception as e:
            print(f"Error in _get_chart_xaxis_properties for group {group}: {e}")
            # Fallback to default values on any error
            pass

        return {'title': title, 'min_label': min_label, 'max_label': max_label, 'mid_label': mid_label}

    def _draw_chart(self):
        """
        根據控制器模式和參數繪製圖表。
        """
        
        self.chart_canvas.delete("all") # 清除舊圖表

        # 獲取A組和B組的輸入信號選擇值 (顯示文字)
        a_input_signal_selection_str = self.writable_entries['000EH'].get()
        b_input_signal_selection_str = self.writable_entries['0018H'].get()
        
        # 獲取B組輸入信號選擇的數值 (用於判斷是否為"無輸出")
        b_input_signal_selection_map = self.translations["B_INPUT_SIGNAL_SELECTION_MAP_VALUES"]
        b_input_signal_selection_rev_map = {v: k for k, v in b_input_signal_selection_map.items()}
        b_input_signal_selection_val = b_input_signal_selection_rev_map.get(b_input_signal_selection_str)

        # 判斷模式
        mode_text = ""
        if b_input_signal_selection_val == 0: # "無輸出"或"No Output"
            mode_text = self.get_current_translation("SINGLE_OUTPUT_MODE_TEXT")
            self._draw_single_output_chart()
        elif a_input_signal_selection_str == b_input_signal_selection_str:
            mode_text = self.get_current_translation("DUAL_OUTPUT_SINGLE_SLOPE_MODE_TEXT")
            self._draw_linked_chart()
        else:
            mode_text = self.get_current_translation("DUAL_OUTPUT_DUAL_SLOPE_MODE_TEXT")
            self._draw_independent_charts()

        # 在圖表區最上方顯示模式名稱
        canvas_width = self.chart_canvas.winfo_width()
        self.chart_canvas.create_text(canvas_width / 2, 20, text=mode_text, font=("Arial", 14, "bold"))

    def _draw_independent_charts(self):
        # 繪製獨立模式的圖表 (A組和B組)
        canvas_width = self.chart_canvas.winfo_width()
        canvas_height = self.chart_canvas.winfo_height()

        # Y軸最大電流值 (3.0A)
        max_current_value = 3

        # 固定圖表寬度
        fixed_chart_w = 250 
        chart_h = canvas_height * 0.5 # Adjusted height for better visualization
        chart_y_start = canvas_height * 0.25 # Adjusted start Y for better visualization

        # Helper function to draw a single chart for independent mode
        def draw_single_independent_chart(x_center_ratio, max_curr, min_curr, dead_zone, line_color, group_label, xaxis_props):
            chart_x_start = canvas_width * x_center_ratio - (fixed_chart_w / 2)

            # 繪製圖表外框
            self.chart_canvas.create_rectangle(chart_x_start, chart_y_start, chart_x_start + fixed_chart_w, chart_y_start + chart_h, outline="black")

            # 繪製X軸 (根據xaxis_props)
            self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start + fixed_chart_w, chart_y_start + chart_h)
            self.chart_canvas.create_text(chart_x_start, chart_y_start + chart_h + 5, text=xaxis_props['min_label'], anchor=tk.N)
            self.chart_canvas.create_text(chart_x_start + fixed_chart_w, chart_y_start + chart_h + 5, text=xaxis_props['max_label'], anchor=tk.N)
            self.chart_canvas.create_text(chart_x_start + fixed_chart_w / 2, chart_y_start + chart_h + 20, text=xaxis_props['title'], anchor=tk.N)

            # 繪製Y軸 (電流 0~3A)
            self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start, chart_y_start)
            self.chart_canvas.create_text(chart_x_start - 5, chart_y_start + chart_h, text="0A", anchor=tk.E)
            self.chart_canvas.create_text(chart_x_start - 5, chart_y_start, text=f"{max_current_value}A", anchor=tk.E)
            self.chart_canvas.create_text(chart_x_start - 20, chart_y_start + chart_h / 2, text=self.get_current_translation("CURRENT"), anchor=tk.CENTER, angle=90)

            # 將百分比和電流值映射到畫布座標
            def map_x(percentage):
                return chart_x_start + (percentage / 100.0) * fixed_chart_w

            def map_y(current_val):
                return chart_y_start + chart_h * (1 - (current_val / max_current_value))

            # 繪製X軸格線 (每10%)
            for p in range(10, 100, 10):
                x_pos = map_x(p)
                self.chart_canvas.create_line(x_pos, chart_y_start, x_pos, chart_y_start + chart_h, fill="lightgray", dash=(2, 2))

            # 繪製Y軸格線 (每0.5A)
            for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
                y_pos = map_y(c)
                self.chart_canvas.create_line(chart_x_start, y_pos, chart_x_start + fixed_chart_w, y_pos, fill="lightgray", dash=(2, 2))

            # 曲線點
            points = []
            # (0%, 0A)
            points.append((map_x(0), map_y(0)))
            # (指令死區值, 0A)
            points.append((map_x(dead_zone), map_y(0)))
            # (指令死區值, 最小電流值)
            points.append((map_x(dead_zone), map_y(min_curr)))
            # (100%, 最大電流值)
            points.append((map_x(100), map_y(max_curr)))

            self.chart_canvas.create_line(points, fill=line_color, width=2, smooth=False)

            # 顯示參數值 (放置在圖表右側)
            text_x_offset = chart_x_start + fixed_chart_w + 10 # 距離圖表右側10像素
            text_y_start = chart_y_start + 10
            line_height = 15

            # 根據group_label選擇正確的翻譯鍵
            max_curr_key = f"{group_label}_MAX_CURRENT"
            min_curr_key = f"{group_label}_MIN_CURRENT"
            dead_zone_key = f"{group_label}_COMMAND_DEAD_ZONE"

            self.chart_canvas.create_text(text_x_offset, text_y_start, anchor=tk.W, 
                                          text=f"Output {group_label}", 
                                          font=("Arial", 8), fill=line_color)
            self.chart_canvas.create_text(text_x_offset, text_y_start + line_height, anchor=tk.W, 
                                          text=f"{self.get_current_translation(max_curr_key).split('(')[0].strip()}: {max_curr:.2f}A", 
                                          font=("Arial", 8), fill=line_color)
            self.chart_canvas.create_text(text_x_offset, text_y_start + 2 * line_height, anchor=tk.W, 
                                          text=f"{self.get_current_translation(min_curr_key).split('(')[0].strip()}: {min_curr:.2f}A", 
                                          font=("Arial", 8), fill=line_color)
            self.chart_canvas.create_text(text_x_offset, text_y_start + 3 * line_height, anchor=tk.W, 
                                          text=f"{self.get_current_translation(dead_zone_key).split('(')[0].strip()}: {dead_zone:.0f}%", 
                                          font=("Arial", 8), fill=line_color)


        # A組參數
        a_max_current = float(self.writable_entries['0010H'].get()) if self.writable_entries['0010H'].get() else 0.0
        a_min_current = float(self.writable_entries['0011H'].get()) if self.writable_entries['0011H'].get() else 0.0
        a_command_dead_zone = float(self.writable_entries['0014H'].get()) if self.writable_entries['0014H'].get() else 0.0
        xaxis_props_a = self._get_chart_xaxis_properties('A')
        draw_single_independent_chart(0.2, a_max_current, a_min_current, a_command_dead_zone, "Coral", "A", xaxis_props_a)

        # B組參數
        b_max_current = float(self.writable_entries['001AH'].get()) if self.writable_entries['001AH'].get() else 0.0
        b_min_current = float(self.writable_entries['001BH'].get()) if self.writable_entries['001BH'].get() else 0.0
        b_command_dead_zone = float(self.writable_entries['001EH'].get()) if self.writable_entries['001EH'].get() else 0.0
        xaxis_props_b = self._get_chart_xaxis_properties('B')
        draw_single_independent_chart(0.7, b_max_current, b_min_current, b_command_dead_zone, "MediumOrchid", "B", xaxis_props_b)

    def _draw_linked_chart(self):
        # 繪製連動模式的圖表
        canvas_width = self.chart_canvas.winfo_width()
        canvas_height = self.chart_canvas.winfo_height()

        # Y軸最大電流值 (3.0A)
        max_current_value = 3

        # 固定圖表寬度
        fixed_chart_w = 250
        chart_h = canvas_height * 0.5
        chart_x_start = (canvas_width - fixed_chart_w) / 2 # 居中
        chart_y_start = canvas_height * 0.25

        # 繪製圖表外框
        self.chart_canvas.create_rectangle(chart_x_start, chart_y_start, chart_x_start + fixed_chart_w, chart_y_start + chart_h, outline="black")

        # 獲取X軸屬性 (跟隨A組)
        xaxis_props = self._get_chart_xaxis_properties('A')

        # 繪製X軸
        self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start + fixed_chart_w, chart_y_start + chart_h)
        self.chart_canvas.create_text(chart_x_start, chart_y_start + chart_h + 5, text=xaxis_props['min_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + fixed_chart_w / 2, chart_y_start + chart_h + 5, text=xaxis_props['mid_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + fixed_chart_w, chart_y_start + chart_h + 5, text=xaxis_props['max_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + fixed_chart_w / 2, chart_y_start + chart_h + 20, text=xaxis_props['title'], anchor=tk.N)

        # 繪製Y軸 (電流 0~3A)
        self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start, chart_y_start)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start + chart_h, text="0A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start, text=f"{max_current_value}A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 20, chart_y_start + chart_h / 2, text=self.get_current_translation("CURRENT"), anchor=tk.CENTER, angle=90)

        # 將百分比和電流值映射到畫布座標
        def map_x(percentage):
            return chart_x_start + (percentage / 100.0) * fixed_chart_w

        def map_y(current_val):
            return chart_y_start + chart_h * (1 - (current_val / max_current_value))

        # 繪製X軸格線 (每10%)
        for p in range(10, 100, 10):
            x_pos = map_x(p)
            self.chart_canvas.create_line(x_pos, chart_y_start, x_pos, chart_y_start + chart_h, fill="lightgray", dash=(2, 2))

        # 繪製Y軸格線 (每0.5A)
        for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
            y_pos = map_y(c)
            self.chart_canvas.create_line(chart_x_start, y_pos, chart_x_start + fixed_chart_w, y_pos, fill="lightgray", dash=(2, 2))

        # 獲取A組和B組的參數
        a_max_current = float(self.writable_entries['0010H'].get()) if self.writable_entries['0010H'].get() else 0.0
        a_min_current = float(self.writable_entries['0011H'].get()) if self.writable_entries['0011H'].get() else 0.0
        a_command_dead_zone = float(self.writable_entries['0014H'].get()) if self.writable_entries['0014H'].get() else 0.0

        b_max_current = float(self.writable_entries['001AH'].get()) if self.writable_entries['001AH'].get() else 0.0
        b_min_current = float(self.writable_entries['001BH'].get()) if self.writable_entries['001BH'].get() else 0.0
        b_command_dead_zone = float(self.writable_entries['001EH'].get()) if self.writable_entries['001EH'].get() else 0.0

        # 模式二曲線點
        points_linked = []
        # (0%, B組最大電流值)
        points_linked.append((map_x(0), map_y(b_max_current)))
        # ((50% - B組指令死區值), B組最小電流值)
        points_linked.append((map_x(50 - b_command_dead_zone), map_y(b_min_current)))
        # ((50% - B組指令死區值), 0A)
        points_linked.append((map_x(50 - b_command_dead_zone), map_y(0)))
        # (50%, 0A) - 中間點
        points_linked.append((map_x(50), map_y(0)))
        # ((50% + A組指令死區值), 0A)
        points_linked.append((map_x(50 + a_command_dead_zone), map_y(0)))
        # ((50% + A組指令死區值), A組最小電流值)
        points_linked.append((map_x(50 + a_command_dead_zone), map_y(a_min_current)))
        # (100%, A組最大電流值)
        points_linked.append((map_x(100), map_y(a_max_current)))

        # 繪製紅色部分 (0% 到 50%)
        red_segment_points = points_linked[:4] # 包含到 (50%, 0A) 的點
        self.chart_canvas.create_line(red_segment_points, fill="MediumOrchid", width=2, smooth=False)

        # 繪製藍色部分 (50% 到 100%)
        blue_segment_points = points_linked[3:] # 從 (50%, 0A) 開始
        self.chart_canvas.create_line(blue_segment_points, fill="Coral", width=2, smooth=False)

        # 顯示參數值 (放置在圖表右側)
        text_x_offset = chart_x_start + fixed_chart_w + 10
        text_y_start = chart_y_start + 10
        line_height = 15

        # 顯示A組參數值
        self.chart_canvas.create_text(text_x_offset, text_y_start, anchor=tk.W, 
                                      text="Output A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_MAX_CURRENT').split('(')[0].strip()}: {a_max_current:.2f}A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 2 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_MIN_CURRENT').split('(')[0].strip()}: {a_min_current:.2f}A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 3 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_COMMAND_DEAD_ZONE').split('(')[0].strip()}: {a_command_dead_zone:.1f}%", 
                                      font=("Arial", 8), fill="Coral")

        # 顯示B組參數值
        self.chart_canvas.create_text(text_x_offset, text_y_start + 4 * line_height, anchor=tk.W, 
                                      text="Output B", 
                                      font=("Arial", 8), fill="MediumOrchid")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 5 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('B_MAX_CURRENT').split('(')[0].strip()}: {b_max_current:.2f}A", 
                                      font=("Arial", 8), fill="MediumOrchid")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 6 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('B_MIN_CURRENT').split('(')[0].strip()}: {b_min_current:.2f}A", 
                                      font=("Arial", 8), fill="MediumOrchid")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 7 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('B_COMMAND_DEAD_ZONE').split('(')[0].strip()}: {b_command_dead_zone:.1f}%", 
                                      font=("Arial", 8), fill="MediumOrchid")

    def _draw_single_output_chart(self):
        # 繪製單組輸出模式的圖表 (只顯示A組)
        canvas_width = self.chart_canvas.winfo_width()
        canvas_height = self.chart_canvas.winfo_height()

        # Y軸最大電流值 (3.0A)
        max_current_value = 3

        # 固定圖表寬度
        fixed_chart_w = 250
        chart_h = canvas_height * 0.5
        chart_x_start = (canvas_width - fixed_chart_w) / 2 # 居中
        chart_y_start = canvas_height * 0.25

        # 繪製圖表外框
        self.chart_canvas.create_rectangle(chart_x_start, chart_y_start, chart_x_start + fixed_chart_w, chart_y_start + chart_h, outline="black")

        # 獲取X軸屬性 (跟隨A組)
        xaxis_props = self._get_chart_xaxis_properties('A')

        # 繪製X軸
        self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start + fixed_chart_w, chart_y_start + chart_h)
        self.chart_canvas.create_text(chart_x_start, chart_y_start + chart_h + 5, text=xaxis_props['min_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + fixed_chart_w, chart_y_start + chart_h + 5, text=xaxis_props['max_label'], anchor=tk.N)
        self.chart_canvas.create_text(chart_x_start + fixed_chart_w / 2, chart_y_start + chart_h + 20, text=xaxis_props['title'], anchor=tk.N)

        # 繪製Y軸 (電流 0~3A)
        self.chart_canvas.create_line(chart_x_start, chart_y_start + chart_h, chart_x_start, chart_y_start)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start + chart_h, text="0A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 5, chart_y_start, text=f"{max_current_value}A", anchor=tk.E)
        self.chart_canvas.create_text(chart_x_start - 20, chart_y_start + chart_h / 2, text=self.get_current_translation("CURRENT"), anchor=tk.CENTER, angle=90)

        # 將百分比和電流值映射到畫布座標
        def map_x(percentage):
            return chart_x_start + (percentage / 100.0) * fixed_chart_w

        def map_y(current_val):
            return chart_y_start + chart_h * (1 - (current_val / max_current_value))

        # 繪製X軸格線 (每10%)
        for p in range(10, 100, 10):
            x_pos = map_x(p)
            self.chart_canvas.create_line(x_pos, chart_y_start, x_pos, chart_y_start + chart_h, fill="lightgray", dash=(2, 2))

        # 繪製Y軸格線 (每0.5A)
        for c in [0.5, 1.0, 1.5, 2.0, 2.5]:
            y_pos = map_y(c)
            self.chart_canvas.create_line(chart_x_start, y_pos, chart_x_start + fixed_chart_w, y_pos, fill="lightgray", dash=(2, 2))

        # A組參數
        a_max_current = float(self.writable_entries['0010H'].get()) if self.writable_entries['0010H'].get() else 0.0
        a_min_current = float(self.writable_entries['0011H'].get()) if self.writable_entries['0011H'].get() else 0.0
        a_command_dead_zone = float(self.writable_entries['0014H'].get()) if self.writable_entries['0014H'].get() else 0.0

        # 曲線點
        points = []
        # (0%, 0A)
        points.append((map_x(0), map_y(0)))
        # (指令死區值, 0A)
        points.append((map_x(a_command_dead_zone), map_y(0)))
        # (指令死區值, 最小電流值)
        points.append((map_x(a_command_dead_zone), map_y(a_min_current)))
        # (100%, 最大電流值)
        points.append((map_x(100), map_y(a_max_current)))

        self.chart_canvas.create_line(points, fill="Coral", width=2, smooth=False)

        # 顯示參數值 (放置在圖表右側)
        text_x_offset = chart_x_start + fixed_chart_w + 10 # 距離圖表右側10像素
        text_y_start = chart_y_start + 10
        line_height = 15

        self.chart_canvas.create_text(text_x_offset, text_y_start, anchor=tk.W, 
                                      text="Output A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_MAX_CURRENT').split('(')[0].strip()}: {a_max_current:.2f}A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 2 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_MIN_CURRENT').split('(')[0].strip()}: {a_min_current:.2f}A", 
                                      font=("Arial", 8), fill="Coral")
        self.chart_canvas.create_text(text_x_offset, text_y_start + 3 * line_height, anchor=tk.W, 
                                      text=f"{self.get_current_translation('A_COMMAND_DEAD_ZONE').split('(')[0].strip()}: {a_command_dead_zone:.1f}%", 
                                      font=("Arial", 8), fill="Coral")

    def _refresh_ports(self):
        """刷新電腦目前可用的串口。"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox['values'] = ports
        if ports:
            self.port_combobox.set(ports[0]) 
        else:
            self.port_combobox.set("") 
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("COM_PORT_NOT_FOUND_WARNING"))

    def _toggle_connection(self):
        """連接或斷開Modbus通訊。"""
        global MODBUS_MASTER
        if self.modbus_master:
            # 斷開連接邏輯
            if self.polling_active:
                self.polling_active = False # Signal thread to stop
                if self.polling_thread and self.polling_thread.is_alive():
                    self.polling_thread.join(timeout=1.0) # Wait for thread to finish
                self.polling_thread = None # Clear thread reference
            
            try:
                self.modbus_master.close()
                self.modbus_master = None
                MODBUS_MASTER = None 
                self.connect_button.config(text=self.get_current_translation("CONNECT_BUTTON"))
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("MODBUS_DISCONNECTED"))
            except Exception as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("MODBUS_DISCONNECT_FAIL").format(e=e))
            finally:
                self._clear_monitor_area() # Clear monitor display on disconnect
                self._clear_writable_params()
                self.last_status_code_a = None # Clear stored status code on disconnect
                self.last_status_code_b = None # Clear stored status code on disconnect
        else:
            # 建立連接邏輯
            port = self.port_combobox.get()
            baudrate = int(self.baudrate_combobox.get())
            
            if not port:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("COM_PORT_SELECT_ERROR"))
                return

            try:
                self.modbus_master = modbus_tk.modbus_rtu.RtuMaster(serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, xonxoff=0))
                self.modbus_master.set_timeout(1.0) 
                self.modbus_master.open() 
                MODBUS_MASTER = self.modbus_master 
                self.connect_button.config(text=self.get_current_translation("DISCONNECT_BUTTON"))
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("MODBUS_CONNECTED").format(port=port, baudrate=baudrate))
                
                # Initial read of all registers
                self._read_all_registers_and_update_gui() 

                # Start polling for monitor area only
                self.polling_active = True
                self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
                self.polling_thread.start()

            except serial.SerialException as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("COM_PORT_OPEN_FAIL").format(port=port, e=e))
            except Exception as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("MODBUS_CONNECT_FAIL").format(e=e))

    def _read_all_registers_and_update_gui(self):
        """
        讀取所有相關寄存器，並更新GUI。
        """
        slave_id_str = self.slave_id_spinbox.get()
        if not slave_id_str.isdigit() or not (1 <= int(slave_id_str) <= 247):
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("SLAVE_ID_ERROR"))
            return

        slave_id = int(slave_id_str)

        if self.modbus_master:
            try:
                start_addr = 0x0000
                if self.controller_mode == 'dual':
                    quantity = 40 # 0x0000 to 0x0027
                else: # single
                    quantity = 14 # 0x0000 to 0x000D

                print(f"讀取所有寄存器: Mode={self.controller_mode}, Slave ID={slave_id}, From 0x{start_addr:04X}, Quantity={quantity}")
                registers = self.modbus_master.execute(slave_id, defines.READ_HOLDING_REGISTERS, start_addr, quantity)
                print(f"讀取到的寄存器值: {registers}")
                
                # Schedule GUI updates on the main thread
                self.master.after(0, lambda: self._update_monitor_area(registers))
                self.master.after(0, lambda: self._update_writable_params_area(registers))
                
                # Schedule chart update
                if self.controller_mode == 'dual':
                    self.master.after(10, self._draw_chart) # Small delay to ensure UI is ready
                elif self.controller_mode == 'single':
                    self.master.after(10, self._draw_single_controller_chart)

            except Exception as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("READ_REGISTERS_FAIL").format(e=e))

    def _read_monitor_registers_only(self):
        """
        只讀取監控區寄存器。
        """
        if not self.polling_active: return

        slave_id = int(self.slave_id_spinbox.get())

        if self.modbus_master:
            try:
                start_addr = 0x0000
                if self.controller_mode == 'dual':
                    quantity = 6 # A and B group
                else: # single
                    quantity = 3 # Only one group

                registers = self.modbus_master.execute(slave_id, defines.READ_HOLDING_REGISTERS, start_addr, quantity)
                self.master.after(0, lambda: self._update_monitor_area(registers))

            except Exception as e:
                print(self.get_current_translation("READ_REGISTERS_POLLING_FAIL").format(e=e))
                # In case of polling error, stop polling and clear the area to avoid stale data
                self.polling_active = False
                self.master.after(0, self._clear_monitor_area)

    def _update_monitor_area(self, registers):
        """
        根據傳入的寄存器值更新即時監控區的GUI。
        """
        try:
            # --- Update Chart History (under lock) ---
            with self.chart_data_lock:
                current_time = time.time()
                if self.controller_mode == 'dual':
                    if len(registers) >= 6:
                        self.time_history.append(current_time)
                        self.current_history_0000.append(registers[0] / 100.0)
                        self.signal_history_0001.append(registers[1] / 10.0)
                        self.current_history_0003.append(registers[3] / 100.0)
                        self.signal_history_0004.append(registers[4] / 10.0)
                elif self.controller_mode == 'single':
                    if len(registers) >= 3:
                        self.time_history.append(current_time)
                        self.current_history_0000.append(registers[0] / 100.0)
                        self.signal_history_0001.append(registers[1] / 10.0)
                        self.current_history_0003.clear()
                        self.signal_history_0004.clear()

            # --- Update GUI (outside lock) ---
            if self.controller_mode == 'dual':
                if len(registers) < 6: return
                raw_current_a, raw_signal_a, status_a, raw_current_b, raw_signal_b, status_b = registers[:6]
                self.last_status_code_a = status_a
                self.last_status_code_b = status_b

                self.monitor_display_controls_a['0000H'].configure(amountused=raw_current_a * 10)
                self.monitor_display_controls_a['0001H'].configure(amountused=raw_signal_a / 10.0)
                self.monitor_display_controls_a['0002H'].config(text=self.translations["STATUS_MAP_VALUES"].get(status_a, self.translations["UNKNOWN_STATUS"]))

                self.monitor_display_controls_b['0003H'].configure(amountused=raw_current_b * 10)
                self.monitor_display_controls_b['0004H'].configure(amountused=raw_signal_b / 10.0)
                self.monitor_display_controls_b['0005H'].config(text=self.translations["STATUS_MAP_VALUES"].get(status_b, self.translations["UNKNOWN_STATUS"]))

            elif self.controller_mode == 'single':
                if len(registers) < 3: return
                raw_current_a, raw_signal_a, status_a = registers[:3]
                self.last_status_code_a = status_a

                self.monitor_display_controls_a['0000H'].configure(amountused=raw_current_a * 10)
                self.monitor_display_controls_a['0001H'].configure(amountused=raw_signal_a / 10.0)
                self.monitor_display_controls_a['0002H'].config(text=self.translations["S_STATUS_MAP_VALUES"].get(status_a, self.translations["UNKNOWN_STATUS"]))

        except Exception as e:
            print(f"An unexpected error occurred in _update_monitor_area: {e}")

    def _clear_monitor_area(self):
        """清除即時監控區的所有顯示。"""
        for reg, control in self.monitor_display_controls_a.items():
            if isinstance(control, ttk.Meter): control.configure(amountused=0)
            else: control.config(text="----")
        
        if self.controller_mode == 'dual':
            for reg, control in self.monitor_display_controls_b.items():
                if isinstance(control, ttk.Meter): control.configure(amountused=0)
                else: control.config(text="----")

        self.last_status_code_a = None
        self.last_status_code_b = None

    def _update_writable_params_area(self, registers):
        """根據讀取的寄存器值更新可寫入參數區。"""
        config = self.writable_params_config if self.controller_mode == 'dual' else self.single_writable_params_config
        
        for param_config in config:
            reg_hex = param_config['reg']
            register_address_int = int(reg_hex.replace('H', ''), 16)
            
            if register_address_int < len(registers):
                value_from_register = registers[register_address_int]
                # ... (rest of the update logic is generic and should work)
                if reg_hex not in self.writable_entries: continue

                if param_config['type'] == 'combobox':
                    display_value = self.translations[param_config['map_key']].get(value_from_register, "")
                    self.writable_entries[reg_hex].set(display_value)
                elif param_config['type'] == 'entry_scaled':
                    scale = param_config.get('scale', 1)
                    display_value = value_from_register * scale
                    self.writable_entries[reg_hex].set(str(display_value) if display_value is not None else "")
                else: # entry, spinbox
                    scale = param_config.get('scale', 1)
                    if scale != 1:
                        display_value = convert_to_float(value_from_register, scale)
                        if display_value is not None:
                            if reg_hex in ['0012H', '0013H', '001CH', '001DH', '000AH', '000BH']:
                                self.writable_entries[reg_hex].set(f"{display_value:.1f}")
                            else:
                                self.writable_entries[reg_hex].set(f"{display_value:.2f}")
                        else:
                            self.writable_entries[reg_hex].set("")
                    else:
                        self.writable_entries[reg_hex].set(str(value_from_register) if value_from_register is not None else "")
            else:
                self.writable_entries[reg_hex].set("") # Clear if data is missing

    def _clear_writable_params(self):
        """清除可寫入參數區的所有顯示，設為空字串或預設值。"""
        for var in self.writable_entries.values():
            var.set("")
        for reg_hex, control in self.writable_controls.items():
            if isinstance(control, ttk.Combobox):
                control.set("")
            elif isinstance(control, ttk.Spinbox):
                control.set(control.cget("from"))

    def _polling_loop(self):
        """每秒讀取一次即時監控區寄存器的後台迴圈。"""
        while self.polling_active:
            self._read_monitor_registers_only()
            time.sleep(0.1) # Poll faster for chart

    def _write_single_register(self, reg_hex, tk_var, control_type, map_dict=None, min_val=None, max_val=None, scale=1, unit_step=1, is_int=False):
        """
        處理單個寄存器的寫入邏輯，包含輸入驗證和數據轉換。
        修改: 特殊處理000DH寫入邏輯。
        """
        slave_id = int(self.slave_id_spinbox.get())
        register_address = int(reg_hex.replace('H', ''), 16) 
        value_str = tk_var.get().strip() 

        if not self.modbus_master:
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("MODBUS_NOT_CONNECTED_WARNING"))
            return
        
        if not value_str: 
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                   self.get_current_translation("INPUT_EMPTY_ERROR").format(reg_hex=reg_hex))
            return

        write_value = None 

        try:
            if control_type == 'combobox':
                if value_str not in map_dict: # map_dict here is already the rev_map
                    messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                           self.get_current_translation("COMBOBOX_SELECT_ERROR").format(reg_hex=reg_hex))
                    return
                write_value = map_dict[value_str]
            elif control_type == 'spinbox':
                if not validate_input_range(value_str, min_val, max_val, type_name=f"寄存器 {reg_hex}", is_int=True):
                    return
                write_value = int(value_str)
            elif control_type == 'entry': 
                if not validate_input_range(value_str, min_val, max_val, type_name=f"寄存器 {reg_hex}", is_int=is_int):
                    return
                write_value = convert_to_register_value(value_str, scale)
                if write_value is None: 
                    messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                           self.get_current_translation("VALUE_CONVERSION_ERROR").format(reg_hex=reg_hex))
                    return
            elif control_type == 'entry_scaled': 
                if not validate_input_range(value_str, min_val, max_val, type_name=f"寄存器 {reg_hex}", is_int=True):
                    return
                
                display_value = int(value_str)
                if unit_step and (display_value % unit_step != 0):
                    messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                           self.get_current_translation("UNIT_MULTIPLE_ERROR").format(reg_hex=reg_hex, display_value=display_value, unit_step=unit_step))
                    return
                
                write_value = int(display_value / scale) 
                
        except ValueError:
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                   self.get_current_translation("INPUT_VALUE_TYPE_ERROR").format(type_name=f"寄存器 {reg_hex}"))
            return
        except Exception as e:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"),
                                 f"處理寄存器 {reg_hex} 輸入時發生未知錯誤: {e}") 
            return

        # Special validation for Max/Min Current for both A and B groups
        if reg_hex == '000FH' or reg_hex == '0010H': # A Max/Min Current
            max_curr_str = self.writable_entries['000FH'].get()
            min_curr_str = self.writable_entries['0010H'].get()
            if max_curr_str and min_curr_str:
                try:
                    float(max_curr_str)
                    float(min_curr_str)
                    if not validate_current_range(max_curr_str, min_curr_str):
                        return 
                except ValueError:
                    pass 
        elif reg_hex == '0018H' or reg_hex == '0019H': # B Max/Min Current
            max_curr_str = self.writable_entries['0018H'].get()
            min_curr_str = self.writable_entries['0019H'].get()
            if max_curr_str and min_curr_str:
                try:
                    float(max_curr_str)
                    float(min_curr_str)
                    if not validate_current_range(max_curr_str, min_curr_str):
                        return 
                except ValueError:
                    pass 

        # *** 修改點: 單個寫入000DH的特殊處理 (Factory Reset) ***
        if reg_hex == '000DH' or reg_hex == '0007H':
            if write_value == 5:
                if messagebox.askyesno(self.get_current_translation("CONFIRM_TITLE"), self.get_current_translation("FACTORY_RESET_CONFIRM_BATCH_MSG")):
                    self._execute_factory_reset()
                return # Stop further processing for this action
            else:
                # For "No Action" or other values, just write it silently or show a message
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("FACTORY_RESET_NO_ACTION_MSG"))
                return # Stop further processing

        # 對於其他寄存器，或000DH但不是0或5的值，執行正常寫入
        if write_value is not None:
            if write_modbus_register(slave_id, register_address, write_value):
                self._read_all_registers_and_update_gui()
                if self.controller_mode == 'dual': self._draw_chart()
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"),
                                    self.get_current_translation("MODBUS_WRITE_SUCCESS").format(value_str=value_str, register_address=register_address))
        else:
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                   self.get_current_translation("WRITE_VALUE_DETERMINE_FAIL").format(reg_hex=reg_hex))
    
    def _get_current_writable_params(self):
        """獲取當前可寫入參數區的數值，準備儲存或批量寫入。"""
        params = {}
        for reg_hex, var in self.writable_entries.items():
            params[reg_hex] = var.get()
        return params

    def _show_countdown_window(self, duration, callback=None):
        """
        顯示一個模態倒數計時視窗。
        :param duration: 倒數的秒數。
        :param callback: 倒數結束後要執行的函數。
        """
        countdown_dialog = tk.Toplevel(self.master)
        countdown_dialog.title(self.get_current_translation("INFO_TITLE"))
        countdown_dialog.resizable(False, False)
        countdown_dialog.grab_set()  # Make it modal

        # Center the dialog
        self.master.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_w = self.master.winfo_width()
        master_h = self.master.winfo_height()
        dialog_w = 400
        dialog_h = 100
        x = master_x + (master_w // 2) - (dialog_w // 2)
        y = master_y + (master_h // 2) - (dialog_h // 2)
        countdown_dialog.geometry(f'{dialog_w}x{dialog_h}+{x}+{y}')

        countdown_label = ttk.Label(countdown_dialog, text="", font=("", 12))
        countdown_label.pack(pady=20, padx=20)

        remaining = tk.IntVar(value=duration)

        def _update_countdown():
            current_remaining = remaining.get()
            if current_remaining > 0:
                countdown_label.config(text=self.get_current_translation("FACTORY_RESET_COUNTDOWN_MSG").format(seconds=current_remaining))
                remaining.set(current_remaining - 1)
                countdown_dialog.after(1000, _update_countdown)
            else:
                countdown_dialog.destroy()
                if callback:
                    callback()
        
        _update_countdown()
        self.master.wait_window(countdown_dialog)

    def _execute_factory_reset(self):
        """執行恢復出廠設置的完整流程。"""
        self.polling_active = False
        time.sleep(0.2) # Give the polling loop a moment to stop

        slave_id = int(self.slave_id_spinbox.get())
        reg_addr = 0x000D if self.controller_mode == 'dual' else 0x0007
        
        print(f"Sending Factory Reset command to reg {reg_addr:04X}")
        if write_modbus_register(slave_id, reg_addr, 5):
            # Show countdown window
            self._show_countdown_window(10, callback=self._post_reset_actions)
        else:
            # If write fails, just restart polling
            self.polling_active = True
            self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
            self.polling_thread.start()

    def _post_reset_actions(self):
        """恢復出廠設置倒數結束後執行的操作。"""
        print("Reset countdown finished. Re-reading all registers.")
        self._read_all_registers_and_update_gui()
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("FACTORY_RESET_SUCCESS_MSG"))

    def _get_parameters_dir(self):
        """根據當前模式和語言獲取參數檔案的儲存目錄。"""
        lang_code = self.current_language_code.get()
        mode_code = self.controller_mode
        return os.path.join(PARAMETERS_DIR, f"{lang_code}_{mode_code}")

    def _save_parameters_to_file(self):
        """將當前可寫入參數區的數值儲存到檔案。"""
        params_dir = self._get_parameters_dir()
        if not os.path.exists(params_dir):
            os.makedirs(params_dir)

        filename = simpledialog.askstring(self.get_current_translation("PARAM_SAVE_PROMPT_TITLE"), 
                                          self.get_current_translation("PARAM_SAVE_PROMPT"),
                                          parent=self.master)
        if not filename:
            return

        if not filename.endswith(".json"):
            filename += ".json"

        filepath = os.path.join(params_dir, filename)

        if os.path.exists(filepath):
            if not messagebox.askyesno(self.get_current_translation("CONFIRM_TITLE"), 
                                       self.get_current_translation("FILE_EXISTS_CONFIRM").format(filename=filename)):
                return

        current_params = self._get_current_writable_params()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(current_params, f, indent=4, ensure_ascii=False)
            messagebox.showinfo(self.get_current_translation("INFO_TITLE"), 
                                self.get_current_translation("SAVE_SUCCESS").format(filename=filename))
        except Exception as e:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"), 
                               self.get_current_translation("SAVE_FAIL").format(e=e))

    def _load_parameters_from_file(self):
        """從檔案讀取參數並更新GUI。"""
        params_dir = self._get_parameters_dir()
        if not os.path.exists(params_dir) or not os.listdir(params_dir):
            messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("LOAD_FAIL_NO_FILES"))
            return

        # Use a custom dialog to show files
        dialog = tk.Toplevel(self.master)
        dialog.title(self.get_current_translation("LOAD_PROMPT"))
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE)
        listbox.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        files = [f for f in os.listdir(params_dir) if f.endswith('.json')]
        for f in files:
            listbox.insert(tk.END, f)

        selected_file = tk.StringVar()

        def on_select():
            if listbox.curselection():
                selected_file.set(listbox.get(listbox.curselection()))
                dialog.destroy()
            else:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("NO_ITEM_SELECTED_MSG"), parent=dialog)

        def on_delete():
            if not listbox.curselection():
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("NO_ITEM_SELECTED_MSG"), parent=dialog)
                return
            
            filename_to_delete = listbox.get(listbox.curselection())
            if messagebox.askyesno(self.get_current_translation("CONFIRM_DELETE_TITLE"), f"{self.get_current_translation('CONFIRM_DELETE_MSG')} '{filename_to_delete}'?", parent=dialog):
                filepath_to_delete = os.path.join(params_dir, filename_to_delete)
                try:
                    if os.path.exists(filepath_to_delete):
                        os.remove(filepath_to_delete)
                        messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("DELETE_SUCCESS").format(filename=filename_to_delete), parent=dialog)
                        listbox.delete(listbox.curselection())
                    else:
                        messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("FILE_NOT_FOUND_FOR_DELETE").format(filename=filename_to_delete), parent=dialog)
                except Exception as e:
                    messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("DELETE_FAIL").format(filename=filename_to_delete, e=e), parent=dialog)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=5, fill=tk.X, padx=10)
        
        load_btn = ttk.Button(button_frame, text=self.get_current_translation("LOAD_BUTTON"), command=on_select)
        load_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        delete_btn = ttk.Button(button_frame, text=self.get_current_translation("DELETE_BUTTON"), bootstyle="danger", command=on_delete)
        delete_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        cancel_btn = ttk.Button(button_frame, text=self.get_current_translation("CANCEL_BUTTON"), command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        dialog.wait_window()

        if not selected_file.get():
            return

        filepath = os.path.join(params_dir, selected_file.get())

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_params = json.load(f)
            
            for reg_hex, value in loaded_params.items():
                if reg_hex in self.writable_entries:
                    self.writable_entries[reg_hex].set(value)
            
            # Redraw chart after loading parameters
            if self.controller_mode == 'dual':
                self._draw_chart()
            elif self.controller_mode == 'single':
                self._draw_single_controller_chart()

            messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("LOAD_SUCCESS").format(selected_name=selected_file.get()))
        except json.JSONDecodeError:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("FILE_FORMAT_ERROR").format(fname=selected_file.get()))
        except Exception as e:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("FILE_READ_ERROR").format(fname=selected_file.get(), e=e))

    def _validate_single_param_for_batch(self, param_config):
        """在批次寫入前驗證單個參數。返回要寫入的值，或在失敗時返回None。"""
        reg_hex = param_config['reg']
        value_str = self.writable_entries[reg_hex].get().strip()
        control_type = param_config['type']

        if not value_str: return None # Skip empty values

        try:
            if control_type == 'combobox':
                rev_map = param_config['rev_map']
                if value_str not in rev_map:
                    return None
                return rev_map[value_str]
            
            elif control_type in ['entry', 'entry_scaled']:
                min_val = param_config['min']
                max_val = param_config['max']
                is_int = param_config.get('is_int', False)
                scale = param_config.get('scale', 1)
                unit_step = param_config.get('unit_step', 1)

                num_value = float(value_str)
                if not (min_val <= num_value <= max_val):
                    return None

                if control_type == 'entry_scaled':
                    if num_value % unit_step != 0:
                        return None
                    return int(num_value / scale)
                else:
                    return convert_to_register_value(value_str, scale)
        except (ValueError, KeyError):
            return None
        return None

    def _batch_write_parameters(self):
        """批量寫入所有可寫入參數。"""
        if not self.modbus_master:
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("MODBUS_NOT_CONNECTED_WARNING"))
            return

        slave_id = int(self.slave_id_spinbox.get())
        config = self.writable_params_config if self.controller_mode == 'dual' else self.single_writable_params_config

        # --- Special handling for Factory Reset ---
        reset_reg = '000DH' if self.controller_mode == 'dual' else '0007H'
        reset_val_str = self.writable_entries[reset_reg].get()
        reset_map = self.translations['FACTORY_RESET_MAP_VALUES' if self.controller_mode == 'dual' else 'S_FACTORY_RESET_MAP_VALUES']
        reset_rev_map = {v: k for k, v in reset_map.items()}
        
        if reset_rev_map.get(reset_val_str) == 5:
            if messagebox.askyesno(self.get_current_translation("CONFIRM_TITLE"), self.get_current_translation("FACTORY_RESET_CONFIRM_BATCH_MSG")):
                self._execute_factory_reset()
            return # Stop here whether reset is confirmed or cancelled

        # --- Pre-write validation for current ranges ---
        if self.controller_mode == 'dual':
            max_a = self.writable_entries['0010H'].get()
            min_a = self.writable_entries['0011H'].get()
            if float(max_a) < float(min_a) + 0.1:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("CURRENT_RANGE_ERROR_A"))
                return
            max_b = self.writable_entries['001AH'].get()
            min_b = self.writable_entries['001BH'].get()
            if float(max_b) < float(min_b) + 0.1:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("CURRENT_RANGE_ERROR_B"))
                return
        else: # single
            max_s = self.writable_entries['0008H'].get()
            min_s = self.writable_entries['0009H'].get()
            if float(max_s) < float(min_s) + 0.1:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("CURRENT_RANGE_ERROR_S"))
                return

        # --- Setup Progress Window ---
        progress_dialog = tk.Toplevel(self.master)
        progress_dialog.title(self.get_current_translation("BATCH_WRITE_PROGRESS_TITLE"))
        progress_dialog.geometry("400x100")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self.master)
        progress_dialog.grab_set()

        progress_label = ttk.Label(progress_dialog, text=self.get_current_translation("BATCH_WRITE_PREPARING"))
        progress_label.pack(pady=10, padx=10)
        progressbar = ttk.Progressbar(progress_dialog, mode='determinate', length=380)
        progressbar.pack(pady=10, padx=10)
        
        self.master.update_idletasks()

        # --- Writing Logic ---
        registers_to_write = [p for p in config if p['reg'] != reset_reg]
        total_registers = len(registers_to_write)
        progressbar["maximum"] = total_registers
        success_count = 0
        failed_registers = []

        for i, param in enumerate(registers_to_write):
            reg_hex = param['reg']
            progress_label.config(text=self.get_current_translation("BATCH_WRITE_IN_PROGRESS").format(register_address=int(reg_hex.replace('H',''), 16), i=i+1, total_registers=total_registers))
            progressbar["value"] = i + 1
            progress_dialog.update()

            value_to_write = self._validate_single_param_for_batch(param)
            
            if value_to_write is not None:
                if write_modbus_register(slave_id, int(reg_hex.replace('H',''), 16), value_to_write):
                    success_count += 1
                else:
                    failed_registers.append(reg_hex)
                    # Stop on first failure
                    break 
            time.sleep(0.05) # Small delay between writes

        progress_dialog.destroy()

        # --- Final Report ---
        if not failed_registers:
            messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("BATCH_WRITE_SUCCESS_ALL"))
        else:
            failed_registers_list = ", ".join(failed_registers)
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("BATCH_WRITE_PARTIAL_FAIL").format(
                success_count=success_count, 
                total_registers=total_registers, 
                failed_registers_list=failed_registers_list
            ))

        # Refresh all data from controller after writing
        self._read_all_registers_and_update_gui()


if __name__ == "__main__":
    try:
        root = ttk.Window(themename="litera")
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        icon_path = os.path.join(base_path, 'icon', '002.ico')
        root.iconbitmap(icon_path)
        app = ModbusMonitorApp(root)
        if app.controller_mode: # Only start mainloop if a mode was selected
            root.mainloop()
    except tk.TclError as e:
        # This can happen if the root window is destroyed before mainloop starts
        if "can't invoke \"winfo\" command" not in str(e):
            raise
