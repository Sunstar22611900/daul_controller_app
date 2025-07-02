#根據gemini02版本手動修改排版

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import serial.tools.list_ports
import modbus_tk
import modbus_tk.defines as defines
import modbus_tk.modbus_rtu
import json
import threading
import time
import sys
import os

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
        "APP_TITLE": "SUNSTAR Modbus RTU 控制器監控調整程式 V1.0",
        "MODBUS_PARAMS_FRAME_TEXT": "Modbus通訊參數設置",
        "COM_PORT_LABEL": "通訊端口",
        "BAUDRATE_LABEL": "鮑率",
        "SLAVE_ID_LABEL": "設備位址",
        "REFRESH_PORTS_BUTTON": "刷新端口",
        "CONNECT_BUTTON": "連接",
        "DISCONNECT_BUTTON": "斷開",
        "MONITOR_AREA_FRAME_TEXT": "即時監控 (0000H~0002H)",
        "OUTPUT_CURRENT_LABEL": "輸出電流",
        "INPUT_SIGNAL_LABEL": "輸入信號",
        "CURRENT_STATUS_LABEL": "目前狀態",
        "WRITABLE_PARAMS_FRAME_TEXT": "可寫入參數 (0003H~000DH)",
        "WRITE_BUTTON": "寫入",
        "BATCH_PARAMS_FRAME_TEXT": "儲存/讀取/寫入",
        "SAVE_PARAMS_BUTTON": "儲存",
        "LOAD_PARAMS_BUTTON": "讀取",
        "BATCH_WRITE_BUTTON": "批次寫入",
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
        "FILE_EXISTS_CONFIRM": "名稱 '{filename}' 已存在，是否覆蓋原存檔？",
        "SAVE_SUCCESS": "參數已成功儲存為 '{filename}'。",
        "SAVE_FAIL": "儲存參數失敗: {e}",
        "LOAD_FAIL_NO_FILES": "未找到任何已儲存的參數檔案。",
        "LOAD_PROMPT": "請選擇要讀取的參數方案:",
        "FILE_FORMAT_ERROR": "檔案 '{fname}' 格式不正確，已跳過。",
        "FILE_READ_ERROR": "讀取檔案 '{fname}' 失敗: {e}",
        "LOAD_SUCCESS": "參數方案 '{selected_name}' 已成功讀取。",
        "SELECT_ITEM_ERROR": "請選擇一個參數方案。",
        "LOAD_BUTTON": "讀取",
        "CANCEL_BUTTON": "取消",
        "BATCH_WRITE_PROGRESS_TITLE": "批次寫入進度",
        "BATCH_WRITE_PREPARING": "準備寫入...",
        "BATCH_WRITE_IN_PROGRESS": "正在寫入寄存器 0x{register_address:04X} ({i}/{total_registers})...",
        "BATCH_WRITE_SUCCESS_ALL": "所有參數已成功寫入控制器！",
        "BATCH_WRITE_PARTIAL_FAIL": "批次寫入部分失敗。成功寫入 {success_count}/{total_registers} 個參數。\n失敗寄存器: {failed_registers_list}",
        "INFO_TITLE": "資訊",
        "WARNING_TITLE": "警告",
        "ERROR_TITLE": "錯誤",
        "CONFIRM_DELETE_TITLE": "刪除確認",
        "CONFIRM_DELETE_MSG": "您確定要刪除參數方案",
        "DELETE_BUTTON": "刪除",
        "NO_ITEM_SELECTED_MSG": "請選擇一個項目。",
        "FACTORY_RESET_NO_ACTION_MSG": "恢復出廠設置 (0) 不執行任何操作。",
        "FACTORY_RESET_SUCCESS_MSG": "恢復出廠設置 (5) 指令已發送，2秒後將重新讀取寄存器。",
        "SKIP_REGISTER_BATCH_WRITE": "跳過寄存器 0x{register_address:04X} ({i}/{total_registers})...",
        # 可寫入參數區的翻譯鍵
        "INPUT_SIGNAL_SELECT": "輸入訊號選擇",
        "ENABLE_MODE": "制能模式",
        "PANEL_DISPLAY_MODE": "面板顯示模式",
        "RS485_CONTROL_SIGNAL": "485控制信號 (0~100)",
        "FACTORY_RESET": "恢復出廠設置",
        "MAX_CURRENT": "最大電流 (0.02~3.00A)",
        "MIN_CURRENT": "最小電流 (0.00~1.00A)",
        "CURRENT_RISE_TIME": "電流上升時間 (0.1~5.0s)",
        "CURRENT_FALL_TIME": "電流下降時間 (0.1~5.0s)",
        "TREMOR_FREQUENCY": "震顫頻率 (70~350Hz, 單位10)",
        "COMMAND_DEAD_ZONE": "指令死區 (0~5)",
        "LANGUAGE_LABEL": "Language",
        "UNKNOWN_STATUS": "未知狀態",
        "WARNING_READ_DATA_INSUFFICIENT": "警告: 讀取到的寄存器數據不足以更新所有可寫入參數。",
        "PARAM_SAVE_PROMPT_TITLE": "參數儲存",
        "CONFIRM_TITLE": "確認",
        "FILE_NOT_FOUND_FOR_DELETE": "檔案 '{filename}' 不存在，無法刪除。",
        "DELETE_FAIL": "刪除檔案 '{filename}' 失敗: {e}",
        "DELETE_SUCCESS": "參數已成功刪除為 '{filename}'。", # 新增刪除成功訊息
        
        # 寄存器值映射表 (用於本地化顯示)
        "STATUS_MAP_VALUES": {
            0: "正常",
            1: "4~20mA控制信號斷路",
            2: "4~20mA控制信號過載",
            3: "線圈開路",
            4: "線圈短路"
        },
        "INPUT_SIGNAL_MAP_VALUES": {
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA",
            3: "RS485",
            4: "面板按鈕"
        },
        "ENABLE_MODE_MAP_VALUES": {
            0: "關閉",
            1: "開啟"
        },
        "DISPLAY_MODE_MAP_VALUES": {
            0: "顯示電流",
            1: "顯示電壓",
            2: "不顯示"
        },
        "FACTORY_RESET_MAP_VALUES": {
            0: "無作用",
            5: "恢復出廠設置"
        }
    },
    "en": {
        "APP_TITLE": "SUNSTAR Modbus RTU Controller Setup V1.0",
        "MODBUS_PARAMS_FRAME_TEXT": "Modbus Setting",
        "COM_PORT_LABEL": "Port",
        "BAUDRATE_LABEL": "Baud Rate",
        "SLAVE_ID_LABEL": "Device Address",
        "REFRESH_PORTS_BUTTON": "Refresh Ports",
        "CONNECT_BUTTON": "Connect",
        "DISCONNECT_BUTTON": "Disconnect",
        "MONITOR_AREA_FRAME_TEXT": "Real-time Monitoring (0000H~0002H)",
        "OUTPUT_CURRENT_LABEL": "Output Current",
        "INPUT_SIGNAL_LABEL": "Input Signal",
        "CURRENT_STATUS_LABEL": "Status",
        "WRITABLE_PARAMS_FRAME_TEXT": "Writable Parameters (0003H~000DH)",
        "WRITE_BUTTON": "Write",
        "BATCH_PARAMS_FRAME_TEXT": "Batch SAVE/LOAD/WRITE",
        "SAVE_PARAMS_BUTTON": "SAVE",
        "LOAD_PARAMS_BUTTON": "LOAD",
        "BATCH_WRITE_BUTTON": "Batch Write",
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
        "FILE_EXISTS_CONFIRM": "Name '{filename}' already exists. Overwrite?",
        "SAVE_SUCCESS": "Parameters successfully saved as '{filename}'.",
        "SAVE_FAIL": "Failed to save parameters: {e}",
        "LOAD_FAIL_NO_FILES": "No saved parameter files found.",
        "LOAD_PROMPT": "Please select a parameter set to load:",
        "FILE_FORMAT_ERROR": "File '{fname}' has incorrect format, skipped.",
        "FILE_READ_ERROR": "Failed to read file '{fname}': {e}",
        "LOAD_SUCCESS": "Parameter set '{selected_name}' successfully loaded.",
        "SELECT_ITEM_ERROR": "Please select an item.",
        "LOAD_BUTTON": "Load",
        "CANCEL_BUTTON": "Cancel",
        "BATCH_WRITE_PROGRESS_TITLE": "Batch Write Progress",
        "BATCH_WRITE_PREPARING": "Preparing to write...",
        "BATCH_WRITE_IN_PROGRESS": "Writing register 0x{register_address:04X} ({i}/{total_registers})...",
        "BATCH_WRITE_SUCCESS_ALL": "All parameters successfully written to controller!",
        "BATCH_WRITE_PARTIAL_FAIL": "Batch write partially failed. Successfully wrote {success_count}/{total_registers} parameters.\nFailed Registers: {failed_registers_list}",
        "INFO_TITLE": "Information",
        "WARNING_TITLE": "Warning",
        "ERROR_TITLE": "Error",
        "CONFIRM_DELETE_TITLE": "Delete Confirmation",
        "CONFIRM_DELETE_MSG": "Are you sure you want to delete parameter set",
        "DELETE_BUTTON": "Delete",
        "NO_ITEM_SELECTED_MSG": "Please select an item.",
        "FACTORY_RESET_NO_ACTION_MSG": "Factory Reset (0) performs no action.",
        "FACTORY_RESET_SUCCESS_MSG": "Factory Reset (5) command sent. Re-reading registers in 2 seconds.",
        "SKIP_REGISTER_BATCH_WRITE": "Skipping register 0x{register_address:04X} ({i}/{total_registers})...",
        # Writable parameter area translations
        "INPUT_SIGNAL_SELECT": "Input Signal Selection",
        "ENABLE_MODE": "Enable Mode",
        "PANEL_DISPLAY_MODE": "Panel Display Mode",
        "RS485_CONTROL_SIGNAL": "RS485 Control Signal (0~100)",
        "FACTORY_RESET": "Factory Reset",
        "MAX_CURRENT": "Max Output Current (0.02~3.00A)",
        "MIN_CURRENT": "Min Output Current (0.00~1.00A)",
        "CURRENT_RISE_TIME": "Ramp up Time (0.1~5.0s)",
        "CURRENT_FALL_TIME": "Ramp down Time (0.1~5.0s)",
        "TREMOR_FREQUENCY": "Dither Frequency (70~350Hz, unit 10)",
        "COMMAND_DEAD_ZONE": "Command Deadband (0~5)",
        "LANGUAGE_LABEL": "語言",
        "UNKNOWN_STATUS": "Unknown Status",
        "WARNING_READ_DATA_INSUFFICIENT": "Warning: Insufficient register data read to update all writable parameters.",
        "PARAM_SAVE_PROMPT_TITLE": "Save Parameters",
        "CONFIRM_TITLE": "Confirm",
        "FILE_NOT_FOUND_FOR_DELETE": "File '{filename}' not found for deletion.",
        "DELETE_FAIL": "Failed to delete file '{filename}': {e}",
        "DELETE_SUCCESS": "Parameters successfully deleted as '{filename}'.", # New translation key
        
        # Register value maps (for localized display)
        "STATUS_MAP_VALUES": {
            0: "Normal",
            1: "4~20mA Signal Open Circuit",
            2: "4~20mA Signal Overload",
            3: "Coil Open Circuit",
            4: "Coil Short Circuit"
        },
        "INPUT_SIGNAL_MAP_VALUES": {
            0: "0~10V",
            1: "0~5V",
            2: "4~20mA",
            3: "RS485",
            4: "Panel Button"
        },
        "ENABLE_MODE_MAP_VALUES": {
            0: "Off",
            1: "On"
        },
        "DISPLAY_MODE_MAP_VALUES": {
            0: "Display Current",
            1: "Display Voltage",
            2: "Do Not Display"
        },
        "FACTORY_RESET_MAP_VALUES": {
            0: "No Action",
            5: "Factory Reset"
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
class ModbusMonitorApp:
    # 類級變量，用於獲取當前翻譯，以便於輔助函數使用
    _current_translations = TEXTS["zh"] 

    @staticmethod
    def get_current_translation(key):
        return ModbusMonitorApp._current_translations.get(key, key) # Fallback to key if not found

    def __init__(self, master):
        self.master = master
        
        self.current_language_code = tk.StringVar(value="zh") # Internal language code
        self._current_translations = TEXTS[self.current_language_code.get()] # Initialize class-level translations
        self.translations = self._current_translations # Initialize instance-level translations here
        
        master.title(self.get_current_translation("APP_TITLE"))
        master.geometry("1000x850") 
        master.resizable(True, True) 

        self.modbus_master = None
        self.polling_active = False
        self.polling_thread = None
        self.last_status_code = None # Added to store the numeric status code for language updates

        self.saved_parameters = {}

        if not os.path.exists(PARAMETERS_DIR):
            os.makedirs(PARAMETERS_DIR)

        self._create_widgets()
        self._refresh_ports() 
        
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 綁定語言選擇變量，當其值改變時更新界面
        self.current_language_code.trace_add("write", self._update_all_text)

    def _on_closing(self):
        """處理視窗關閉事件，停止輪詢線程並關閉Modbus連接。"""
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

    def _create_widgets(self):
        """創建所有GUI元件並佈局。"""
        #total_frame = ttk.Frame(self.master)
        #total_frame.pack()
        # 0~2高度由內容決定
        self.master.grid_rowconfigure(0, weight=0)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=0)
        # 3高度隨視窗變化
        self.master.grid_rowconfigure(3, weight=1)
        # 4-5高度由內容決定
        self.master.grid_rowconfigure(4, weight=0)
        self.master.grid_rowconfigure(5, weight=0)

        # --- 列配置實現左右置中 ---
        # 第0列: 左側的「填充」列，負責吸收多餘的水平空間，weight=1
        self.master.grid_columnconfigure(0, weight=1)
        # 第1列: 放置實際內容的列，不設置weight，其寬度由內容或 explicitly 設定
        # 這裡我們不設置 weight，表示它不會隨視窗拉伸。其寬度將由內部內容決定。
        # 或者你可以考慮在你的主內容框架上直接設定一個固定寬度。
        self.master.grid_columnconfigure(1, weight=0)
        # 第2列: 右側的「填充」列，負責吸收多餘的水平空間，weight=1
        self.master.grid_columnconfigure(2, weight=1)



        # --- 頂部區域框架 ---
        top_frame = ttk.Frame(self.master)
        top_frame.grid(row=0, column=1, sticky='ew')


        # Language Selection (Top Right)
        self.language_frame = ttk.LabelFrame(top_frame, text=self.get_current_translation("LANGUAGE_LABEL"), padding="10")
        self.language_frame.pack(side=tk.RIGHT, pady=5)
#        self.language_label = ttk.Label(language_frame, text=self.get_current_translation("LANGUAGE_LABEL"))
#        self.language_label.pack(side=tk.LEFT, padx=5)
        
        self.language_combobox_var = tk.StringVar(value="中文") # Display value for combobox
        self.language_combobox = ttk.Combobox(self.language_frame, values=["中文", "English"], state="readonly", width=5, textvariable=self.language_combobox_var)
        self.language_combobox.pack(side=tk.LEFT, padx=5, pady=5, )
        self.language_combobox.bind("<<ComboboxSelected>>", self._on_language_select) # Bind to combobox selection event

        # A. Modbus通訊參數設置區域 (左側)
        self.modbus_params_frame = ttk.LabelFrame(top_frame, text=self.get_current_translation("MODBUS_PARAMS_FRAME_TEXT"), padding="10")
        self.modbus_params_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # 端口選擇
        self.com_port_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("COM_PORT_LABEL"))
        self.com_port_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_combobox = ttk.Combobox(self.modbus_params_frame, state="readonly", width=10)
        self.port_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # 鮑率選擇
        self.baudrate_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("BAUDRATE_LABEL"))
        self.baudrate_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.baudrate_combobox = ttk.Combobox(self.modbus_params_frame, values=[4800, 9600, 19200, 38400, 57600], state="readonly", width=10)
        self.baudrate_combobox.set(19200) # 預設鮑率
        self.baudrate_combobox.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # 設備位址選擇
        self.slave_id_label = ttk.Label(self.modbus_params_frame, text=self.get_current_translation("SLAVE_ID_LABEL"))
        self.slave_id_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.slave_id_var = tk.StringVar(value="1") # 使用StringVar以便於取值和Spinbox更新
        self.slave_id_spinbox = ttk.Spinbox(self.modbus_params_frame, from_=1, to=247, increment=1, width=5, textvariable=self.slave_id_var)
        self.slave_id_spinbox.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

        # 刷新端口按鈕
        self.refresh_ports_button = ttk.Button(self.modbus_params_frame, text=self.get_current_translation("REFRESH_PORTS_BUTTON"), command=self._refresh_ports)
        self.refresh_ports_button.grid(row=0, column=6, padx=10, pady=5)
        # 連接/斷開按鈕 (修改功能: 連接同時讀取0003h~000dh)
        self.connect_button = ttk.Button(self.modbus_params_frame, text=self.get_current_translation("CONNECT_BUTTON"), command=self._toggle_connection)
        self.connect_button.grid(row=0, column=7, padx=10, pady=5)


        # --- 分隔線 ---
        ttk.Separator(self.master, orient='horizontal').grid(row=1, column=1, pady=10, sticky='nsew')

        # --- 中間區域框架 ---
        middle_frame = ttk.Frame(self.master)
        middle_frame.grid(row=2, column=1, sticky='nsew')

        # A. 即時監控區 (0000H~0002H)
        self.monitor_frame = ttk.LabelFrame(middle_frame, text=self.get_current_translation("MONITOR_AREA_FRAME_TEXT"), padding="10")
        self.monitor_frame.pack(fill=tk.X, pady=10)
        
        # 使用一個內部框架來佈局監控標籤，使其保持水平排版
        monitor_inner_frame = ttk.Frame(self.monitor_frame)
        monitor_inner_frame.pack(fill=tk.X, pady=5)

        self.monitor_labels_info = {} # 儲存 {reg_hex: {'label_obj': obj, 'title_key': 'key', 'unit': 'unit_str'}}
        self.monitor_display_labels = {} # 儲存實際顯示數值的label物件
        
        # 修改：0000H單位為A，0001H單位為%
        monitor_data_config = [
            ("0000H", "OUTPUT_CURRENT_LABEL", "A"), 
            ("0001H", "INPUT_SIGNAL_LABEL", "%"),   
            ("0002H", "CURRENT_STATUS_LABEL", "")
        ]
        
        # 創建監控標籤
        for i, (reg_hex, title_key, unit) in enumerate(monitor_data_config):
            item_frame = ttk.Frame(monitor_inner_frame)
            item_frame.pack(side=tk.LEFT, padx=10, pady=2, expand=True)

            title_label = ttk.Label(item_frame, text=f"{reg_hex}: {self.get_current_translation(title_key)}")
            title_label.pack(side=tk.TOP, anchor=tk.W)
            
            value_frame = ttk.Frame(item_frame)
            value_frame.pack(side=tk.TOP, anchor=tk.W)
            
            display_label = ttk.Label(value_frame, text="----", anchor="w", font=('Arial', 16, 'bold'))
            display_label.pack(side=tk.LEFT)
            if unit:
                ttk.Label(value_frame, text=unit).pack(side=tk.LEFT, padx=2)
            
            self.monitor_labels_info[reg_hex] = {'title_label': title_label, 'unit': unit, 'title_key': title_key}
            self.monitor_display_labels[reg_hex] = display_label
        
        self._clear_monitor_area() 

        middle_frame2 = ttk.Frame(self.master)
        middle_frame2.grid(row=3, column=1, sticky='nsew')


        # B. 可寫入參數區 (0003H~000DH)
        self.writable_params_frame = ttk.LabelFrame(middle_frame2, text=self.get_current_translation("WRITABLE_PARAMS_FRAME_TEXT"), padding="10")
        self.writable_params_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 使用Canvas和Scrollbar處理內容過多
        self.canvas = tk.Canvas(self.writable_params_frame)
        scrollbar = ttk.Scrollbar(self.writable_params_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.writable_entries = {} 
        self.writable_controls = {} 
        self.writable_labels = {} # Store label widgets for language update
        self.writable_write_buttons = {} # Store write button widgets for language update

        # 定義可寫入參數的結構，包含寄存器地址、標題、類型、映射表、範圍等
        self.writable_params_config = [ 
            {'reg': '0003H', 'title_key': 'INPUT_SIGNAL_SELECT', 'type': 'combobox', 'map_key': 'INPUT_SIGNAL_MAP_VALUES'},
            {'reg': '0004H', 'title_key': 'ENABLE_MODE', 'type': 'combobox', 'map_key': 'ENABLE_MODE_MAP_VALUES'},
            {'reg': '0005H', 'title_key': 'PANEL_DISPLAY_MODE', 'type': 'combobox', 'map_key': 'DISPLAY_MODE_MAP_VALUES'},
            {'reg': '0006H', 'title_key': 'RS485_CONTROL_SIGNAL', 'type': 'spinbox', 'min': 0, 'max': 100, 'is_int': True},
            {'reg': '0007H', 'title_key': 'FACTORY_RESET', 'type': 'combobox', 'map_key': 'FACTORY_RESET_MAP_VALUES'},
            {'reg': '0008H', 'title_key': 'MAX_CURRENT', 'type': 'entry', 'min': 0.02, 'max': 3.00, 'scale': 100},
            {'reg': '0009H', 'title_key': 'MIN_CURRENT', 'type': 'entry', 'min': 0.00, 'max': 1.00, 'scale': 100},
            {'reg': '000AH', 'title_key': 'CURRENT_RISE_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10},
            {'reg': '000BH', 'title_key': 'CURRENT_FALL_TIME', 'type': 'entry', 'min': 0.1, 'max': 5.0, 'scale': 10},
            {'reg': '000CH', 'title_key': 'TREMOR_FREQUENCY', 'type': 'entry_scaled', 'min': 70, 'max': 350, 'scale': 10, 'unit_step': 10, 'is_int': True},
            {'reg': '000DH', 'title_key': 'COMMAND_DEAD_ZONE', 'type': 'spinbox', 'min': 0, 'max': 5, 'is_int': True},
        ]

        # 動態創建可寫入參數區的元件
        for i, param in enumerate(self.writable_params_config):
            reg_hex = param['reg']
            # Store label reference
            label = ttk.Label(self.scrollable_frame, text=f"{reg_hex}: {self.get_current_translation(param['title_key'])}")
            label.grid(row=i, column=0, padx=5, pady=2, sticky=tk.W)
            self.writable_labels[reg_hex] = label # Store label reference
            
            var = tk.StringVar()
            self.writable_entries[reg_hex] = var

            control = None
            if param['type'] == 'combobox':
                # Get initial map values from current language
                initial_map_values = self.translations[param['map_key']]
                control = ttk.Combobox(self.scrollable_frame, textvariable=var, values=list(initial_map_values.values()), state="readonly", width=25)
                control.grid(row=i, column=1, padx=5, pady=2, sticky=tk.NSEW)
                self.writable_controls[reg_hex] = control
                # Store map and rev_map directly in param for easy access later
                param['map'] = initial_map_values
                param['rev_map'] = {v: k for k, v in initial_map_values.items()}
                
                btn = ttk.Button(self.scrollable_frame, text=self.get_current_translation("WRITE_BUTTON"), command=lambda r=reg_hex, v=var, t='combobox', p=param: self._write_single_register(r, v, t, map_dict=p['rev_map']))
                btn.grid(row=i, column=2, padx=5, pady=2)
                self.writable_write_buttons[reg_hex] = btn # Store button reference
            elif param['type'] == 'spinbox':
                control = ttk.Spinbox(self.scrollable_frame, from_=param['min'], to=param['max'], increment=1, textvariable=var, width=25)
                control.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)
                self.writable_controls[reg_hex] = control
                btn = ttk.Button(self.scrollable_frame, text=self.get_current_translation("WRITE_BUTTON"), command=lambda r=reg_hex, v=var, t='spinbox', mn=param['min'], mx=param['max'], is_int=param['is_int']: self._write_single_register(r, v, t, min_val=mn, max_val=mx, is_int=is_int))
                btn.grid(row=i, column=2, padx=5, pady=2)
                self.writable_write_buttons[reg_hex] = btn # Store button reference
            elif param['type'] == 'entry':
                control = ttk.Entry(self.scrollable_frame, textvariable=var, width=25)
                control.grid(row=i, column=1, padx=5, pady=2, sticky=tk.NSEW)
                self.writable_controls[reg_hex] = control
                btn = ttk.Button(self.scrollable_frame, text=self.get_current_translation("WRITE_BUTTON"), command=lambda r=reg_hex, v=var, t='entry', mn=param['min'], mx=param['max'], sc=param['scale'], is_int=False: self._write_single_register(r, v, t, min_val=mn, max_val=mx, scale=sc, is_int=is_int))
                btn.grid(row=i, column=2, padx=5, pady=2)
                self.writable_write_buttons[reg_hex] = btn # Store button reference
            elif param['type'] == 'entry_scaled':
                control = ttk.Entry(self.scrollable_frame, textvariable=var, width=25)
                control.grid(row=i, column=1, padx=5, pady=2, sticky=tk.NSEW)
                self.writable_controls[reg_hex] = control
                btn = ttk.Button(self.scrollable_frame, text=self.get_current_translation("WRITE_BUTTON"), command=lambda r=reg_hex, v=var, t='entry_scaled', mn=param['min'], mx=param['max'], sc=param['scale'], ust=param['unit_step'], is_int=param['is_int']: self._write_single_register(r, v, t, min_val=mn, max_val=mx, scale=sc, unit_step=ust, is_int=is_int))
                btn.grid(row=i, column=2, padx=5, pady=2)
                self.writable_write_buttons[reg_hex] = btn # Store button reference

        self._clear_writable_params() 

        # --- 分隔線 ---
        #ttk.Separator(total_frame, orient='horizontal').grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        # --- 底部區域框架 ---
        btm_frame = ttk.Frame(self.master)
        btm_frame.grid(row=5, column=1, sticky='nsew')

        # C. 批量參數儲存/讀取/寫入區
        self.batch_params_frame = ttk.LabelFrame(btm_frame, text=self.get_current_translation("BATCH_PARAMS_FRAME_TEXT"), padding="10")
        self.batch_params_frame.pack(fill=tk.X, pady=5)

        self.save_params_button = ttk.Button(self.batch_params_frame, text=self.get_current_translation("SAVE_PARAMS_BUTTON"), command=self._save_parameters_to_file)
        self.save_params_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.load_params_button = ttk.Button(self.batch_params_frame, text=self.get_current_translation("LOAD_PARAMS_BUTTON"), command=self._load_parameters_from_file)
        self.load_params_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.batch_write_button = ttk.Button(self.batch_params_frame, text=self.get_current_translation("BATCH_WRITE_BUTTON"), command=self._batch_write_parameters)
        self.batch_write_button.pack(side=tk.LEFT, padx=10, pady=5)


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
        ModbusMonitorApp._current_translations = TEXTS[self.current_language_code.get()]
        self.translations = ModbusMonitorApp._current_translations

        self.master.title(self.translations["APP_TITLE"])
        
        # Update LabelFrames
        self.modbus_params_frame.config(text=self.translations["MODBUS_PARAMS_FRAME_TEXT"])
        self.monitor_frame.config(text=self.translations["MONITOR_AREA_FRAME_TEXT"])
        self.writable_params_frame.config(text=self.translations["WRITABLE_PARAMS_FRAME_TEXT"])
        self.batch_params_frame.config(text=self.translations["BATCH_PARAMS_FRAME_TEXT"])

        # Update specific labels
        self.com_port_label.config(text=self.translations["COM_PORT_LABEL"])
        self.baudrate_label.config(text=self.translations["BAUDRATE_LABEL"])
        self.slave_id_label.config(text=self.translations["SLAVE_ID_LABEL"])
        
        # Update buttons
        self.refresh_ports_button.config(text=self.translations["REFRESH_PORTS_BUTTON"])
        # Update connect/disconnect button text based on connection status
        self.connect_button.config(text=self.translations["DISCONNECT_BUTTON"] if self.modbus_master else self.translations["CONNECT_BUTTON"])
        
        # Update monitor area labels (titles only)
        for reg_hex, info in self.monitor_labels_info.items():
            info['title_label'].config(text=f"{reg_hex}: {self.translations[info['title_key']]}")

        # Update monitor area 0002H (Current Status) display value
        if hasattr(self, 'last_status_code') and self.last_status_code is not None:
            status_text = self.translations["STATUS_MAP_VALUES"].get(self.last_status_code, self.translations["UNKNOWN_STATUS"])
            self.monitor_display_labels['0002H'].config(text=status_text)
        else:
            self.monitor_display_labels['0002H'].config(text="----")


        # Update writable parameters labels and single write buttons
        for param_config in self.writable_params_config:
            reg_hex = param_config['reg']
            self.writable_labels[reg_hex].config(text=f"{reg_hex}: {self.translations.get(param_config['title_key'], param_config['title_key'])}")
            
            # Special handling for comboboxes to update values and re-translate selected item
            if param_config['type'] == 'combobox':
                new_map_values = self.translations[param_config['map_key']]
                current_numeric_value = None
                
                # Try to get the current numeric value based on the OLD language's rev_map
                # Check if 'rev_map' key exists and is not None
                if 'rev_map' in param_config and param_config['rev_map'] is not None:
                    current_display_text = self.writable_entries[reg_hex].get()
                    # Attempt to find the numeric key from the previous display text
                    for k, v in param_config['map'].items(): # Use param_config['map'] here which is the old language's map
                        if v == current_display_text:
                            current_numeric_value = k
                            break

                # Update the combobox values list with the new language's display strings
                self.writable_controls[reg_hex].config(values=list(new_map_values.values()))

                # Update the internal 'map' and 'rev_map' for this param_config to the new language's maps
                param_config['map'] = new_map_values
                param_config['rev_map'] = {v: k for k, v in new_map_values.items()}

                # Re-set the textvariable with the new language's corresponding string
                if current_numeric_value is not None:
                    self.writable_entries[reg_hex].set(new_map_values.get(current_numeric_value, ""))
                else: # If no value was previously set or couldn't be translated, clear it
                    self.writable_entries[reg_hex].set("")

            # Update single write button text
            self.writable_write_buttons[reg_hex].config(text=self.translations["WRITE_BUTTON"])
            
        # Update batch operation buttons
        self.save_params_button.config(text=self.translations["SAVE_PARAMS_BUTTON"])
        self.load_params_button.config(text=self.translations["LOAD_PARAMS_BUTTON"])
        self.batch_write_button.config(text=self.translations["BATCH_WRITE_BUTTON"])

        # Update language label
        self.language_frame.config(text=self.translations["LANGUAGE_LABEL"])


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
        """連接或斷開Modbus通訊。
        修改: 連接成功後，讀取0003h~000dh並顯示於可寫入參數區，同時開始每秒更新0000h~0002h。
        斷開時停止更新並清空。
        """
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
                self.last_status_code = None # Clear stored status code on disconnect
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
        讀取0000H~000DH所有寄存器，並更新即時監控區和可寫入參數區。
        此函數用於連接成功或寫入成功後的完整界面刷新。
        """
        slave_id_str = self.slave_id_spinbox.get()
        if not slave_id_str.isdigit() or not (1 <= int(slave_id_str) <= 247):
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("SLAVE_ID_ERROR"))
            self._clear_monitor_area()
            self._clear_writable_params()
            return

        slave_id = int(slave_id_str)

        if self.modbus_master:
            try:
                print(f"讀取所有寄存器: Slave ID={slave_id}, From 0x0000, Quantity=14")
                registers = self.modbus_master.execute(slave_id, defines.READ_HOLDING_REGISTERS, 0x0000, 14)
                print(f"讀取到的寄存器值: {registers}")
                
                self._update_monitor_area(registers) 
                self._update_writable_params_area(registers) 

            except Exception as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"), self.get_current_translation("READ_REGISTERS_FAIL").format(e=e))
                print(f"讀取所有寄存器失敗: {e}")
                self._clear_monitor_area()
                self._clear_writable_params()
        else:
            self._clear_monitor_area()
            self._clear_writable_params()

    def _read_monitor_registers_only(self):
        """
        只讀取0000H~0002H寄存器，並更新即時監控區。
        此函數專用於每秒更新的輪詢。
        """
        # Ensure polling is still active before attempting to read
        if not self.polling_active:
            return

        slave_id_str = self.slave_id_spinbox.get()
        if not slave_id_str.isdigit() or not (1 <= int(slave_id_str) <= 247):
            print("設備位址錯誤，停止輪詢。")
            self.polling_active = False # Stop polling if slave ID is invalid
            self.master.after(0, lambda: self._clear_monitor_area())
            return

        slave_id = int(slave_id_str)

        if self.modbus_master:
            try:
                registers = self.modbus_master.execute(slave_id, defines.READ_HOLDING_REGISTERS, 0x0000, 3)
                self._update_monitor_area(registers) 

            except Exception as e:
                print(self.get_current_translation("READ_REGISTERS_POLLING_FAIL").format(e=e)) 
                self.polling_active = False # Stop polling on error
                self.master.after(0, lambda: self._clear_monitor_area())
        else:
            self.polling_active = False # Stop polling if master is not connected
            self.master.after(0, lambda: self._clear_monitor_area())


    def _update_monitor_area(self, registers):
        """根據讀取的寄存器值更新即時監控區的顯示。"""
        # 0000H: 輸出電流 (A)
        current_val = convert_to_float(registers[0], 100)
        self.monitor_display_labels['0000H'].config(text=f"{current_val:.2f}" if current_val is not None else "----")

        # 0001H: 輸入信號 (%)
        signal_val = convert_to_float(registers[1], 10)
        self.monitor_display_labels['0001H'].config(text=f"{signal_val:.1f}" if signal_val is not None else "----")

        # 0002H: 目前狀態
        status_code = registers[2]
        self.last_status_code = status_code # Store the numeric value for language updates
        status_text = self.translations["STATUS_MAP_VALUES"].get(status_code, self.get_current_translation("UNKNOWN_STATUS")) 
        self.monitor_display_labels['0002H'].config(text=status_text)

    def _clear_monitor_area(self):
        """清除即時監控區的所有顯示，設為"----"。"""
        for label in self.monitor_display_labels.values():
            label.config(text="----")
        self.last_status_code = None # Clear stored status code when area is cleared

    def _update_writable_params_area(self, registers):
        """根據讀取的寄存器值更新可寫入參數區的元件顯示。
        注意: registers參數需要包含0003H到000DH的數據。
        """
        if len(registers) < 14:
            print(self.get_current_translation("WARNING_READ_DATA_INSUFFICIENT")) 
            self._clear_writable_params()
            return

        # 0003H: 輸入訊號選擇
        input_signal_val = registers[3]
        self.writable_entries['0003H'].set(self.translations["INPUT_SIGNAL_MAP_VALUES"].get(input_signal_val, ""))

        # 0004H: 制能模式
        enable_mode_val = registers[4]
        self.writable_entries['0004H'].set(self.translations["ENABLE_MODE_MAP_VALUES"].get(enable_mode_val, ""))

        # 0005H: 面板顯示模式
        display_mode_val = registers[5]
        self.writable_entries['0005H'].set(self.translations["DISPLAY_MODE_MAP_VALUES"].get(display_mode_val, ""))

        # 0006H: 485控制信號
        rs485_signal_val = registers[6]
        self.writable_entries['0006H'].set(str(rs485_signal_val) if rs485_signal_val is not None else "")

        # 0007H: 恢復出廠設置
        factory_reset_val = registers[7]
        self.writable_entries['0007H'].set(self.translations["FACTORY_RESET_MAP_VALUES"].get(factory_reset_val, ""))

        # 0008H: 最大電流
        max_current_val = convert_to_float(registers[8], 100)
        self.writable_entries['0008H'].set(f"{max_current_val:.2f}" if max_current_val is not None else "")

        # 0009H: 最小電流
        min_current_val = convert_to_float(registers[9], 100)
        self.writable_entries['0009H'].set(f"{min_current_val:.2f}" if min_current_val is not None else "")

        # 000AH: 電流上升時間
        rise_time_val = convert_to_float(registers[10], 10)
        self.writable_entries['000AH'].set(f"{rise_time_val:.1f}" if rise_time_val is not None else "")

        # 000BH: 電流下降時間
        fall_time_val = convert_to_float(registers[11], 10)
        self.writable_entries['000BH'].set(f"{fall_time_val:.1f}" if fall_time_val is not None else "")

        # 000CH: 震顫頻率 (寄存器數值為實際值/10)
        tremor_freq_val = registers[12] * 10 if registers[12] is not None else None
        self.writable_entries['000CH'].set(f"{tremor_freq_val:.0f}" if tremor_freq_val is not None else "")

        # 000D H: 指令死區
        dead_zone_val = registers[13]
        self.writable_entries['000DH'].set(str(dead_zone_val) if dead_zone_val is not None else "")

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
            self.master.after(0, self._read_monitor_registers_only) 
            time.sleep(1) 

    def _write_single_register(self, reg_hex, tk_var, control_type, map_dict=None, min_val=None, max_val=None, scale=1, unit_step=1, is_int=False):
        """
        處理單個寄存器的寫入邏輯，包含輸入驗證和數據轉換。
        修改: 特殊處理0007H寫入邏輯。
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
                if not validate_input_range(value_str, min_val, max_val, type_name=f"寄存器 {reg_hex}", is_int=False):
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
                if display_value % unit_step != 0:
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

        # 特殊驗證：0008H (最大電流) 和 0009H (最小電流)
        if reg_hex in ['0008H', '0009H']:
            max_curr_str = self.writable_entries['0008H'].get()
            min_curr_str = self.writable_entries['0009H'].get()
            if max_curr_str and min_curr_str:
                try:
                    float(max_curr_str)
                    float(min_curr_str)
                    if not validate_current_range(max_curr_str, min_curr_str):
                        return 
                except ValueError:
                    pass 

        # *** 修改點: 單個寫入0007H的特殊處理 ***
        if reg_hex == '0007H':
            if write_value == 0:
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("FACTORY_RESET_NO_ACTION_MSG"))
                return # 寫入0不執行任何動作
            elif write_value == 5:
                if write_modbus_register(slave_id, register_address, write_value):
                    messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("FACTORY_RESET_SUCCESS_MSG"))
                    # 間隔2秒後再重新讀取所有寄存器並更新介面
                    self.master.after(2000, self._read_all_registers_and_update_gui)
                return # 已處理，退出函數
        
        # 對於其他寄存器，或0007H但不是0或5的值，執行正常寫入
        if write_value is not None:
            if write_modbus_register(slave_id, register_address, write_value):
                self._read_all_registers_and_update_gui()
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

    def _save_parameters_to_file(self):
        """將"可寫入參數區"的參數儲存在本地檔案中。"""
        params_to_save = self._get_current_writable_params()

        filename = simpledialog.askstring(self.get_current_translation("PARAM_SAVE_PROMPT_TITLE"),
                                          self.get_current_translation("PARAM_SAVE_PROMPT"))
        if not filename: 
            return

        file_path = os.path.join(PARAMETERS_DIR, f"{filename}.json")

        if os.path.exists(file_path):
            if not messagebox.askyesno(self.get_current_translation("CONFIRM_TITLE"),
                                       self.get_current_translation("FILE_EXISTS_CONFIRM").format(filename=filename)):
                return 

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(params_to_save, f, indent=4, ensure_ascii=False)
            messagebox.showinfo(self.get_current_translation("INFO_TITLE"),
                                self.get_current_translation("SAVE_SUCCESS").format(filename=filename))
        except Exception as e:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"),
                                 self.get_current_translation("SAVE_FAIL").format(e=e))

    def _load_parameters_from_file(self):
        """從本地讀取參數檔案，並在選單中顯示供使用者選擇。
        修改: 新增"刪除"按鈕。
        """
        self.saved_parameters = {}
        for fname in os.listdir(PARAMETERS_DIR):
            if fname.endswith(".json"):
                name = os.path.splitext(fname)[0] 
                file_path = os.path.join(PARAMETERS_DIR, fname)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.saved_parameters[name] = data
                except json.JSONDecodeError:
                    messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                           self.get_current_translation("FILE_FORMAT_ERROR").format(fname=fname))
                except Exception as e:
                    messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                           self.get_current_translation("FILE_READ_ERROR").format(fname=fname, e=e))

        if not self.saved_parameters:
            messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("LOAD_FAIL_NO_FILES"))
            return

        select_window = tk.Toplevel(self.master)
        select_window.title(self.get_current_translation("LOAD_PROMPT"))
        select_window.geometry("400x300") 
        select_window.transient(self.master) 
        select_window.grab_set() 

        ttk.Label(select_window, text=self.get_current_translation("LOAD_PROMPT")).pack(padx=10, pady=5)
        
        listbox_frame = ttk.Frame(select_window)
        listbox_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, height=10, width=40, exportselection=False)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        for name in self.saved_parameters.keys():
            listbox.insert(tk.END, name)

        def on_select():
            selected_index = listbox.curselection()
            if selected_index:
                selected_name = listbox.get(selected_index[0])
                params = self.saved_parameters.get(selected_name)
                if params:
                    self._apply_parameters_to_gui(params)
                    messagebox.showinfo(self.get_current_translation("INFO_TITLE"),
                                        self.get_current_translation("LOAD_SUCCESS").format(selected_name=selected_name))
                select_window.destroy() 
            else:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("SELECT_ITEM_ERROR"))
        
        def on_delete_selected():
            selected_index = listbox.curselection()
            if selected_index:
                selected_name = listbox.get(selected_index[0])
                if messagebox.askyesno(self.get_current_translation("CONFIRM_DELETE_TITLE"),
                                       self.get_current_translation("CONFIRM_DELETE_MSG") + f" '{selected_name}'?"):
                    self._delete_parameter_file(selected_name)
                    listbox.delete(selected_index[0]) # 從列表框中移除
                    if not listbox.size(): # 如果列表為空，關閉窗口
                        select_window.destroy()
            else:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("NO_ITEM_SELECTED_MSG"))

        def on_cancel():
            select_window.destroy()

        button_frame = ttk.Frame(select_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text=self.get_current_translation("LOAD_BUTTON"), command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=self.get_current_translation("DELETE_BUTTON"), command=on_delete_selected).pack(side=tk.LEFT, padx=5) # 新增刪除按鈕
        ttk.Button(button_frame, text=self.get_current_translation("CANCEL_BUTTON"), command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        select_window.wait_window() 

    def _delete_parameter_file(self, filename_to_delete):
        """刪除指定的參數檔案。"""
        file_path = os.path.join(PARAMETERS_DIR, f"{filename_to_delete}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                # 從 saved_parameters 字典中移除
                if filename_to_delete in self.saved_parameters:
                    del self.saved_parameters[filename_to_delete]
                # *** 修正點：使用 DELETE_SUCCESS 而非 SAVE_SUCCESS ***
                messagebox.showinfo(self.get_current_translation("INFO_TITLE"),
                                    self.get_current_translation("DELETE_SUCCESS").format(filename=filename_to_delete)) 
            else:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                       self.get_current_translation("FILE_NOT_FOUND_FOR_DELETE").format(filename=filename_to_delete))
        except Exception as e:
            messagebox.showerror(self.get_current_translation("ERROR_TITLE"),
                                 self.get_current_translation("DELETE_FAIL").format(filename=filename_to_delete, e=e))

    def _apply_parameters_to_gui(self, params):
        """將從檔案讀取到的參數填入GUI的"可寫入參數區"的相應欄位。"""
        for reg_hex, value_str in params.items():
            if reg_hex in self.writable_entries:
                self.writable_entries[reg_hex].set(value_str)

    def _batch_write_parameters(self):
        """
        批量將"可寫入檔案區"的所有參數依次寫入控制器。
        修改: 跳過0007h不進行寫入動作。
        """
        if not self.modbus_master:
            messagebox.showwarning(self.get_current_translation("WARNING_TITLE"), self.get_current_translation("MODBUS_NOT_CONNECTED_WARNING"))
            return

        # Use self.writable_params_config which is a list of dicts
        params_to_write_list = self.writable_params_config 

        # 預先執行所有驗證。若有任何一個參數不合法，則停止整個批量寫入
        for param_entry_dict in params_to_write_list: # Iterate through the list of dictionaries
            reg_hex = param_entry_dict['reg']
            
            # Skip validation for 0007H
            if reg_hex == '0007H':
                continue 
            
            value_str = self.writable_entries[reg_hex].get().strip() # Get value from GUI entry for this reg_hex
            if not value_str:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                       self.get_current_translation("INPUT_EMPTY_ERROR").format(reg_hex=reg_hex))
                return

            try:
                # Use param_entry_dict for specific parameter info
                if param_entry_dict['type'] == 'combobox':
                    # *** 修正點: 批次寫入預驗證，對 combobox 使用 rev_map 進行驗證 ***
                    # Access the rev_map stored in param_entry_dict itself (updated on language change)
                    if value_str not in param_entry_dict['rev_map']:
                        messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                               self.get_current_translation("COMBOBOX_SELECT_ERROR").format(reg_hex=reg_hex))
                        return
                elif param_entry_dict['type'] == 'spinbox':
                    if not validate_input_range(value_str, param_entry_dict['min'], param_entry_dict['max'], type_name=f"寄存器 {reg_hex}", is_int=True):
                        return
                elif param_entry_dict['type'] == 'entry':
                    if not validate_input_range(value_str, param_entry_dict['min'], param_entry_dict['max'], type_name=f"寄存器 {reg_hex}", is_int=False):
                        return
                    if convert_to_register_value(value_str, param_entry_dict['scale']) is None:
                        messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                               self.get_current_translation("VALUE_CONVERSION_ERROR").format(reg_hex=reg_hex))
                        return
                elif param_entry_dict['type'] == 'entry_scaled':
                    if not validate_input_range(value_str, param_entry_dict['min'], param_entry_dict['max'], type_name=f"寄存器 {reg_hex}", is_int=True):
                        return
                    if int(value_str) % param_entry_dict['unit_step'] != 0:
                        messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                               self.get_current_translation("UNIT_MULTIPLE_ERROR").format(reg_hex=reg_hex, display_value=value_str, unit_step=param_entry_dict['unit_step']))
                        return
            except ValueError:
                messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                       self.get_current_translation("INPUT_VALUE_TYPE_ERROR").format(type_name=f"寄存器 {reg_hex}"))
                return
            except Exception as e:
                messagebox.showerror(self.get_current_translation("ERROR_TITLE"),
                                     f"驗證寄存器 {reg_hex} 時發生未知錯誤: {e}")
                return

        max_curr_str = self.writable_entries['0008H'].get()
        min_curr_str = self.writable_entries['0009H'].get()
        if not validate_current_range(max_curr_str, min_curr_str):
            return 

        progress_window = tk.Toplevel(self.master)
        progress_window.title(self.get_current_translation("BATCH_WRITE_PROGRESS_TITLE"))
        progress_window.geometry("350x120")
        progress_window.transient(self.master) 
        progress_window.grab_set() 
        progress_window.resizable(False, False) 
        
        self._set_gui_state(tk.DISABLED)

        progress_label = ttk.Label(progress_window, text=self.get_current_translation("BATCH_WRITE_PREPARING"))
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=250, mode="determinate")
        progress_bar.pack(pady=5)

        # total_elements_in_batch is the total number of items in the config list (including skipped ones for progress bar visuals)
        total_elements_in_batch = len(params_to_write_list)
        
        def do_batch_write():
            slave_id = int(self.slave_id_spinbox.get())
            success_count = 0
            failed_registers = []
            
            for i_idx, param_entry_dict in enumerate(params_to_write_list): # Iterate directly over the list
                reg_hex = param_entry_dict['reg'] 
                
                # Calculate progress for display, based on overall index
                display_progress_count = i_idx + 1 

                if reg_hex == '0007H':
                    self.master.after(0, progress_label.config, {'text': self.get_current_translation("SKIP_REGISTER_BATCH_WRITE").format(register_address=int(reg_hex.replace('H', ''), 16), i=display_progress_count, total_registers=total_elements_in_batch)})
                    self.master.after(0, progress_bar.config, {'value': display_progress_count / total_elements_in_batch * 100 if total_elements_in_batch > 0 else 100})
                    self.master.update_idletasks()
                    time.sleep(0.1)
                    continue 
                
                register_address = int(reg_hex.replace('H', ''), 16)
                value_str = self.writable_entries[reg_hex].get().strip() # Get value from GUI entry
                write_value = None

                if param_entry_dict['type'] == 'combobox':
                    write_value = param_entry_dict['rev_map'][value_str] # Use rev_map for conversion to actual value
                elif param_entry_dict['type'] == 'spinbox':
                    write_value = int(value_str)
                elif param_entry_dict['type'] == 'entry':
                    write_value = convert_to_register_value(value_str, param_entry_dict['scale'])
                elif param_entry_dict['type'] == 'entry_scaled':
                    write_value = int(int(value_str) / param_entry_dict['scale'])

                self.master.after(0, progress_label.config, {'text': self.get_current_translation("BATCH_WRITE_IN_PROGRESS").format(register_address=register_address, i=display_progress_count, total_registers=total_elements_in_batch)})
                self.master.after(0, progress_bar.config, {'value': display_progress_count / total_elements_in_batch * 100 if total_elements_in_batch > 0 else 100})
                self.master.update_idletasks() 

                if write_modbus_register(slave_id, register_address, write_value): 
                    success_count += 1
                else:
                    failed_registers.append(reg_hex)
                    
                time.sleep(0.1) 

            self.master.after(0, progress_window.destroy)
            self.master.after(0, lambda: self._set_gui_state(tk.NORMAL)) 

            # Calculate total registers that were *intended* to be written (excluding 0007H)
            actual_total_to_write = len([p for p in params_to_write_list if p['reg'] != '0007H'])

            if success_count == actual_total_to_write:
                self.master.after(0, lambda: messagebox.showinfo(self.get_current_translation("INFO_TITLE"), self.get_current_translation("BATCH_WRITE_SUCCESS_ALL")))
            else:
                self.master.after(0, lambda: messagebox.showwarning(self.get_current_translation("WARNING_TITLE"),
                                                                     self.get_current_translation("BATCH_WRITE_PARTIAL_FAIL").format(success_count=success_count, total_registers=actual_total_to_write, failed_registers_list=', '.join(failed_registers))))
            
            self.master.after(0, self._read_all_registers_and_update_gui)

        threading.Thread(target=do_batch_write, daemon=True).start()

    def _set_gui_state(self, state):
        """
        設置主窗口中特定元件的狀態（正常或禁用）。
        用於在批量寫入時禁用GUI操作。
        """
        self.connect_button.config(state=state)
        self.port_combobox.config(state=state)
        self.baudrate_combobox.config(state=state)
        self.slave_id_spinbox.config(state=state)
        self.refresh_ports_button.config(state=state)
        
        for reg_hex, var in self.writable_entries.items():
            control_widget = self.writable_controls.get(reg_hex)
            if isinstance(control_widget, (ttk.Entry, ttk.Spinbox)):
                control_widget.config(state=state)
            elif isinstance(control_widget, ttk.Combobox):
                if state == tk.DISABLED:
                    control_widget.config(state=tk.DISABLED)
                else: 
                    control_widget.config(state="readonly")
        
        for btn in self.writable_write_buttons.values():
            btn.config(state=state)
                                        
        self.save_params_button.config(state=state)
        self.load_params_button.config(state=state)
        self.batch_write_button.config(state=state)


def resource_path(relative_path):
    #Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.normpath(os.path.join(base_path, relative_path))

# --- 主程式入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(resource_path('icon/001.ico'))
    app = ModbusMonitorApp(root)

    root.tk.call('source', resource_path('forest-light.tcl'))
    ttk.Style().theme_use('forest-light')

    root.mainloop()

#打包指令 pyinstaller -w -F -i icon/002.ico --add-data="icon/001.ico;icon" ds_v17.py
#exe簽章指令 signtool sign /a /t http://timestamp.sectigo.com /v D:\07python\dist\ds_v13.exe
#加入主題後的打包指令 pyinstaller -w -F -i icon/002.ico --add-data="icon/001.ico;icon" --add-data="forest-light.tcl;." --add-data="forest-light/*;forest-light" gmn_v03.pypyinstaller -w -F -i icon/002.ico --add-data="icon/001.ico;icon" --add-data="forest-light.tcl;." --add-data="forest-light/*;forest-light" gmn_v03.py