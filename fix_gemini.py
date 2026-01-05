
import os

filepath = r"d:\07python\gemini-daul-controller\GEMINI.md"
last_good_line = "**文字優化：** 根據使用者回饋，更新了精靈各步驟的標題與說明文字，使其更直觀。"

new_content = """

## 2026年1月5日 進度更新 (自動重連功能)

### 1. 新增斷線通知與自動重連

*   **功能描述：** 當 Modbus 輪詢監測失敗時，不再僅於後台報錯，而是跳出視窗通知使用者，並嘗試自動重新連線。
*   **實作細節 (`dual_controller_app.py`)：**
    *   **新增翻譯鍵：** 在 `TEXTS` 字典中新增了 `RECONNECT_TITLE`, `RECONNECT_MSG`, `RECONNECT_ATTEMPT`, `RECONNECT_FAIL_FINAL`, `RECONNECT_CLOSE_BTN` 等中英文翻譯。
    *   **修改 `ModbusMonitorApp` 類別：**
        *   新增 `is_reconnecting` 旗標，防止重複開啟重連視窗。
        *   新增 `_handle_disconnection_error` 方法：
            *   建立模態視窗 (Modal Window)。
            *   執行 10 秒倒數計時。
            *   倒數結束後，執行最多 3 次的重連嘗試。
            *   若重連成功 (讀取 0x0000 成功)，關閉視窗並恢復輪詢。
            *   若 3 次失敗，顯示最終斷線訊息並啟用關閉按鈕，讓使用者手動斷開連線。
    *   **調整輪詢邏輯：**
        *   在 `_read_monitor_registers_only` 方法的例外處理區塊中，暫停輪詢 (`self.polling_active = False`)，並使用 `self.master.after` 呼叫 `_handle_disconnection_error`。

### 2. 遇到的問題與解決方案

*   **`NameError` in Lambda (`name 'e' is not defined`)**
    *   **問題描述：** 在 `except Exception as e:` 區塊中，嘗試使用 `lambda: self._handle_disconnection_error(e)` 排程 UI 更新。但由於 Python 3 在 `except` 區塊結束後會刪除例外變數 `e`，導致 lambda 執行時找不到 `e`。
    *   **解決方案：** 修改為 `lambda err=str(e): self._handle_disconnection_error(err)`，利用預設參數在 lambda 定義時就捕捉 `e` 的值 (字串形式)。
"""

with open(filepath, 'rb') as f:
    content_bytes = f.read()

content_str = content_bytes.decode('utf-8', errors='ignore')

# Find the marker
split_idx = content_str.rfind(last_good_line)

if split_idx != -1:
    # Keep content up to the end of the last good line
    # We find where the line ends (newline)
    newline_idx = content_str.find('\n', split_idx)
    if newline_idx != -1:
        truncated_content = content_str[:newline_idx+1]
    else:
        truncated_content = content_str # End of file
        
    final_content = truncated_content + new_content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Successfully repaired and appended GEMINI.md")
else:
    print("Could not find marker line. File might be too corrupted or I have the wrong marker.")
