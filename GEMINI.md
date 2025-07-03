# 對話摘要：雙控制器應用程式開發

## 專案目標
將現有的 `gmn_v03.py` 應用程式修改為支援雙控制器的版本，並根據 `daul_controller_user_manual.pdf` 文件更新 GUI 介面和 Modbus 通訊邏輯。

## 規劃與實施
1.  **創建新檔案：** 將 `gmn_v03.py` 的內容複製到 `dual_controller_app.py`。
2.  **更新 `TEXTS` 字典：** 根據新的雙控制器需求，新增和修改了中英文翻譯鍵值，特別是針對新的監控區和可寫入參數區的標籤。
3.  **修改 `writable_params_config`：** 根據 `daul_controller_user_manual.pdf` 中的寄存器地址，重新定義了可寫入參數的配置，並將其分組為「通用參數」、「A 組參數」、「B 組參數」和「信號 PID 參數」。
4.  **重構 `_create_widgets` 函數：**
    *   將「即時監控」區分為「即時監控 (A組)」和「即時監控 (B組)」兩個獨立的 `LabelFrame`，分別顯示 A 組和 B 組的輸出電流、輸入信號和目前狀態。
    *   將「可寫入參數區」改為使用 `ttk.Notebook`，並創建了四個標籤頁：通用參數、A 組參數、B 組參數、信號 PID 參數。每個標籤頁內部使用 `Canvas` 和 `Scrollbar` 來處理內容過多時的滾動。
    *   動態創建可寫入參數的元件時，根據 `param['group']` 將其放置到對應的標籤頁框架中。
5.  **更新 `_update_all_text` 函數：** 確保在語言切換時，所有新的 GUI 元素（包括 `ttk.Notebook` 的標籤文字）都能正確更新。
6.  **調整 Modbus 讀取相關函數：**
    *   `_read_all_registers_and_update_gui`：修改為讀取從 `0x0000H` 到 `0x0024H` 共 37 個寄存器。
    *   `_read_monitor_registers_only`：修改為讀取 `0x0000H` 到 `0x0005H` 共 6 個寄存器，用於 A、B 兩組的即時監控。
    *   `_update_monitor_area`：更新邏輯以正確解析並顯示 A 組和 B 組的監控數據.
    *   `_update_writable_params_area`：重寫此函數，以將讀取到的所有寄存器值正確地填充到新的可寫入參數 GUI 控制項中，並處理不同類型控制項的數據轉換。
7.  **修改 Modbus 寫入相關函數：**
    *   `_write_single_register`：將「恢復出廠設置」的特殊處理從 `0007H` 移至 `000CH`。
    *   `_batch_write_parameters`：更新此函數以遍歷新的 `writable_params_config`，並在批次寫入時跳過 `000CH`（恢復出廠設置）的寫入操作。

## 遇到的問題與解決方案

在開發過程中，我們遇到了一些問題並逐一解決：

1.  **`_tkinter.TclError: bitmap "..." not defined` (圖示檔案缺失)**
    *   **問題描述：** 程式無法找到 `icon/001.ico` 圖示檔案。
    *   **解決方案：** 經檢查，`icon` 目錄不存在。手動創建 `D:\07python\gemini-daul-controller\icon` 目錄並將 `001.ico` 和 `002.ico` 複製到其中。

2.  **`KeyError: 'is_int'` (參數配置錯誤)**
    *   **問題描述：** 在 `_create_widgets` 函數中，為 `entry` 類型控制項創建按鈕命令時，程式預期 `param` 字典中存在 `is_int` 鍵，但某些 `entry` 參數並未定義此鍵。
    *   **解決方案：** 修改相關程式碼，使用 `param.get('is_int', False)` 來安全地獲取 `is_int` 的值，如果不存在則預設為 `False`。

3.  **`_tkinter.TclError: couldn't read file "forest-light.tcl"` (主題檔案缺失)**
    *   **問題描述：** 程式無法找到 `forest-light.tcl` 主題檔案。
    *   **解決方案：** 經檢查，`forest-light.tcl` 和 `forest-light` 目錄不存在。手動將這些檔案/目錄複製到 `D:\07python\gemini-daul-controller\` 目錄。

4.  **`AttributeError: 'ModbusMonitorApp' object has no attribute 'writable_params_frame'` (GUI 元素引用錯誤)**
    *   **問題描述：** 在 `_update_all_text` 函數中，程式嘗試配置已替換為 `writable_params_notebook` 的 `writable_params_frame`。
    *   **解決方案：** 從 `_update_all_text` 函數中移除對 `self.writable_params_frame.config` 的呼叫。

## 目前狀態
所有規劃的程式碼修改已完成，並且應用程式已成功執行。您現在應該可以看到一個帶有 Modbus 參數設置、A/B 組即時監控區、可寫入參數（分為通用、A 組、B 組、PID 參數標籤頁）以及批量操作區的應用程式視窗。

## 生成可執行檔

在程式碼修改完成並確認應用程式能夠正常運行後，我們嘗試使用 `PyInstaller` 工具將 `dual_controller_app.py` 打包成可執行檔。

### 遇到的問題與解決方案 (PyInstaller)

1.  **`Unable to find 'D:\07python\gemini-daul-controller\"icon\001.ico' when adding binary and data files.` (路徑引號問題)**
    *   **問題描述：** 首次嘗試使用 `pyinstaller` 命令時，`--add-data` 參數中的路徑因引號和轉義問題導致 `PyInstaller` 無法找到檔案.\
    *   **解決方案：** 嘗試了多種引號和轉義方式，但直接在 `run_shell_command` 的 `command` 字串中處理複雜的 `PyInstaller` 參數轉義較為困難。

2.  **`.spec` 檔案語法錯誤 (`SyntaxError: unexpected character after line continuation character`)**
    *   **問題描述：** 在嘗試修正 `PyInstaller` 命令後，生成的可執行檔仍然失敗，並報告 `.spec` 檔案中存在語法錯誤，這表明 `PyInstaller` 在解析命令時對路徑字串的處理仍然存在問題.\
    *   **解決方案：** 採取更穩健的方法：
        1.  **生成基本 `.spec` 檔案：** 首先執行 `pyinstaller dual_controller_app.py` 命令，讓 `PyInstaller` 生成一個不包含 `icon` 和 `add-data` 參數的預設 `.spec` 檔案 (`dual_controller_app.spec`)。
        2.  **修改 `.spec` 檔案：** 手動讀取 `dual_controller_app.spec` 檔案，並以程式碼方式精確地修改 `EXE` 物件的 `console` 屬性為 `False`，並添加 `icon='icon/002.ico'`。同時，在 `Analysis` 物件的 `datas` 列表中添加所有必要的資料檔案路徑：
            ```python
            datas=[
                ('icon/001.ico', 'icon'),
                ('icon/002.ico', 'icon'),
                ('forest-light.tcl', '.'),
                ('forest-light', 'forest-light'),
            ],
            ```
        3.  **使用修改後的 `.spec` 檔案生成可執行檔：** 最後，執行 `pyinstaller dual_controller_app.spec` 命令，讓 `PyInstaller` 使用修改後的 `.spec` 檔案來建置可執行檔。

3.  **輸出目錄不為空 (`The output directory "..." is not empty.`)**
    *   **問題描述：** 在使用修改後的 `.spec` 檔案再次生成可執行檔時，`PyInstaller` 報告輸出目錄不為空。
    *   **解決方案：** 在 `pyinstaller` 命令中加入 `-y` 選項 (`pyinstaller dual_controller_app.spec -y`)，強制 `PyInstaller` 覆寫現有的輸出目錄。

### 最終結果
經過上述步驟，`PyInstaller` 成功生成了 `dual_controller_app.exe` 可執行檔。您可以在 `D:\07python\gemini-daul-controller\dist` 目錄中找到它。

## 2025年7月1日 進度更新

### 1. Modbus 參數更新

*   **`writable_params_config` 調整：**
    *   新增了「第二組485控制信號」（寄存器 `000AH`）。
    *   新增了「A組震顫幅度」（寄存器 `0017H`）和「B組震顫幅度」（寄存器 `0021H`）。
    *   調整了「恢復出廠設置」的寄存器地址，從 `000CH` 變更為 `000DH`。
    *   更新了「A組輸入信號選擇」和「B組輸入信號選擇」的選項，使其與控制器規格一致.\
    *   修正了「震顫幅度」的範圍為 0~25%。

*   **`TEXTS` 字典更新：**
    *   為新增的參數添加了中英文翻譯鍵。
    *   修改了現有參數的翻譯鍵，以匹配新的命名和範圍。
    *   更新了「A組輸入信號選擇」和「B組輸入信號選擇」的映射值。

*   **Modbus 讀取邏輯調整：**
    *   將 `_read_all_registers_and_update_gui` 函數中讀取的寄存器總數從 37 個增加到 40 個（從 `0x0000` 到 `0x0027`）。
    *   更新了 `_update_writable_params_area` 函數中的數據長度檢查。

*   **Modbus 寫入邏輯調整：**
    *   更新了 `_write_single_register` 和 `_batch_write_parameters` 函數中對「恢復出廠設置」寄存器地址的引用，從 `000CH` 變更為 `000DH`。

### 2. 圖表功能初步實現

*   **GUI 佈局調整：** 在「可寫入參數區」和「批量操作區」之間新增了「控制器模式圖表」區域，包含一個 `tk.Canvas`。
*   **圖表繪製函數：**
    *   新增了 `_draw_chart` 函數作為圖表繪製的核心入口。
    *   新增了 `_draw_independent_charts` 函數用於繪製獨立模式下的兩個圖表。
    *   新增了 `_draw_linked_chart` 函數用於繪製連動模式下的單個圖表。
    *   圖表會根據 `000EH` (A組輸入信號選擇) 和 `0018H` (B組輸入信號選擇) 的值判斷控制器模式並切換顯示。
    *   圖表會根據「最大/最小電流」、「上升/下降時間」和「震顫幅度」等參數繪製示意曲線。
*   **圖表動態更新：**
    *   在 `_read_all_registers_and_update_gui` 函數末尾調用 `_draw_chart`。
    *   在 `_write_single_register` 函數成功寫入後調用 `_draw_chart`。
    *   在 `_batch_write_parameters` 函數成功寫入後調用 `_draw_chart`。

### 3. 遇到的問題與解決方案 (2025年7月2日)

*   **問題描述：** 執行程式後，「可寫入參數區」的內容（文字、輸入框、按鈕）沒有顯示，圖表區雖然存在但內容空白。
*   **解決方案：**
    1.  **`_create_widgets` 函數重構：** 重新編寫 `_create_widgets` 函數，確保所有 GUI 元件（特別是可寫入參數區的標籤、輸入框和按鈕）都被正確創建並賦值給 `self` 的屬性。同時，為 `ttk.Notebook` 內的每個 `scrollable_frame` 添加 `grid_columnconfigure(1, weight=1)`，確保內容能夠正確顯示。
    2.  **`writable_params_config` 語法修正：** 修正 `writable_params_config` 類別屬性定義中的語法錯誤（`SyntaxError: unterminated triple-quoted string literal`），確保其為有效的 Python 列表。
    3.  **`_create_monitor_widgets` 函數位置修正：** 將 `_create_monitor_widgets` 函數從 `_create_widgets` 內部移出，使其成為 `ModbusMonitorApp` 類別的獨立方法，並在 `_create_widgets` 中正確呼叫。
    4.  **語言切換問題修正：**
        *   修正 `TEXTS` 字典中英文 `LANGUAGE_LABEL` 的翻譯。
        *   確保 `_create_widgets` 函數中 `language_frame` 的初始文本使用翻譯鍵。
        *   將 `self.current_language_code.trace_add` 的位置移動到 `_create_widgets()` 函數之後，確保在觸發語言更新時所有 GUI 元件都已存在。

*   **目前狀態：** 「可寫入參數區」已恢復正常顯示，語言切換功能也已完全正常。

## 2025年7月2日 進度更新 (圖表功能改進)

### 1. 圖表繪製邏輯改進

*   **`_draw_chart` 函數模式判斷：**
    *   修改了模式判斷邏輯，現在會根據 A 組和 B 組輸入信號選擇的 *數值* 是否相同來判斷是獨立模式還是連動模式。
*   **`_draw_independent_charts` 函數（模式一）改進：**
    *   調整了 X 軸為輸入信號 0~100%，Y 軸為電流 0~3A。
    *   實現了根據「指令死區值」、「最小電流值」和「最大電流值」繪製梯形電流曲線。
    *   在電流曲線周圍繪製了帶狀區域以視覺化「震顫幅度」。
    *   在圖表軸上添加了「電流」和「時間」的標籤.\
*   **`_draw_linked_chart` 函數（模式二）改進：**
    *   調整了 X 軸為輸入信號 0~100%，Y 軸為電流 0~3A。
    *   實現了根據「B組最大電流值」、「B組指令死區值」、「B組最小電流值」、「A組指令死區值」、「A組最小電流值」和「A組最大電流值」繪製連動模式下的曲線。
    *   在電流曲線周圍繪製了帶狀區域以視覺化「震顫幅度」。
    *   在圖表軸上添加了「電流」和「時間」的標籤.\
*   **圖表更新時機：**
    *   確保 `_read_all_registers_and_update_gui` 函數在更新所有參數後調用 `_draw_chart`。
    *   確保 `_write_single_register` 函數在成功寫入後調用 `_draw_chart`。
    *   確保 `_batch_write_parameters` 函數在批量寫入完成後調用 `_draw_chart`。

### 2. 翻譯鍵更新

*   **`TEXTS` 字典更新：**
    *   為圖表軸標籤（「輸入信號」、「電流」、「時間」）和圖例（「A組曲線」、「B組曲線」）添加了新的中英文翻譯鍵。

## 2025年7月2日 進度更新 (圖表功能改進 - 續)

### 1. 圖表模式與名稱調整

*   **模式名稱更新：**
    *   原「獨立模式」更名為「雙組信號-雙組輸出」(Dual Output Dual Slope)。
    *   原「連動模式」更名為「單組信號-雙組輸出」(Dual Output Single Slope)。
*   **新增第三種模式「單組輸出」(Single Output)：**
    *   當 B 組輸入信號選擇為「無輸出」或「No Output」時觸發。
    *   此模式下，圖表區只顯示 A 組參數的圖表。
*   **模式名稱顯示：** 在圖表區最上方以較顯眼的方式顯示當前模式名稱。

### 2. 圖表顯示優化

*   **圖表尺寸：** 個別圖表的寬度統一調整為 250 像素。
*   **圖表外觀：**
    *   移除了 X 軸和 Y 軸的箭頭。
    *   圖表區域現在具有完整的上下左右外框線。
    *   X 軸每 10% 繪製一條垂直格線。
    *   Y 軸每 0.5A 繪製一條水平格線。
*   **參數文字顯示：**
    *   「雙組信號-雙組輸出」模式下，A、B 兩組參數的顯示已修正，確保正確對應各自的組別。
    *   「單組信號-雙組輸出」模式下，新增了 A、B 兩組的最大電流、最小電流和指令死區數值的顯示。
    *   所有圖表中的參數文字已從圖表下方移至圖表右側，方便閱讀。
*   **「單組信號-雙組輸出」線條顏色：**
    *   圖表線條在 X 軸 50% 以下的部分顯示為紅色。
    *   圖表線條在 X 軸 50% 以上的部分顯示為藍色。
*   **圖例移除：** 「單組信號-雙組輸出」模式下，移除了「A組曲線」和「B組曲線」的圖例文字。

## 2025年7月3日 進度更新

### 1. 參數輸入區優化

*   **移除個別寫入按鈕：** 將參數輸入區每個參數旁邊的獨立寫入按鈕全部移除，簡化介面.\
*   **兩欄顯示：** 將參數輸入欄位從單欄改為左右兩欄顯示，提高空間利用率.\
*   **統一元件寬度：** 調整 `ttk.Combobox` 和 `ttk.Spinbox` 的 `width` 屬性為 `15`，`ttk.Entry` 保持 `18`，以實現視覺上總寬度的一致性.\
*   **批量操作按鈕位置調整：** 將「儲存」、「讀取」和「批次寫入」按鈕從原有的「批量操作區」移至「可寫入參數區」的底部，並統一按鈕寬度為 `15`.\
*   **語言切換問題修正：** 修正了 `KeyError` 導致語言切換時參數調整區語言無法更新的問題，確保所有控制項在語言切換時都能正確更新。

### 2. 參數顯示邏輯調整

*   **小數點位數控制：** 修改 `_update_writable_params_area` 函數中的顯示邏輯，針對寄存器 `0012H` (A組電流上升時間)、`0013H` (A組電流下降時間)、`001CH` (B組電流上升時間) 和 `001DH` (B組電流下降時間)，在顯示時只顯示到小數點後第一位。

### 3. 批次寫入邏輯調整

*   **`_batch_write_parameters` 函數行為模式修改：**
    1.  **若選擇"無作用(No Action)"時按下批次寫入鍵(目前顯示名稱是"套用至控制器")，則正常批次寫入。**
    2.  **若選擇"恢復出廠設置(Factory Reset)"時按下批次寫入鍵，則跳出警示視窗，內容為"即將將控制器恢復出廠設置，是否確定?"**
        *   **按下確認：** 其餘參數皆不寫入，單獨將對應值寫入 `000DH`，並強制暫停讀取寫入控制器 5 秒，再恢復。
        *   **按下取消：** 則不進行任何動作。
*   **`_write_single_register` 函數中恢復出廠設置的暫停時間調整：** 將暫停時間從 2 秒調整為 5 秒，以與批次寫入邏輯保持一致。
*   **`TEXTS` 字典更新：**
    *   新增 `FACTORY_RESET_CONFIRM_BATCH_MSG` 翻譯鍵。
    *   更新 `FACTORY_RESET_SUCCESS_MSG` 的中英文翻譯，以反映新的暫停時間。

## 2025年7月3日 進度更新 (GUI 佈局優化)

### 1. 中間欄寬度固定

*   **`_create_widgets` 函數調整：**
    *   將主視窗的 `geometry` 設置為 `1000x850`。
    *   新增 `self.main_content_frame` 作為所有主要內容的父框架，並將其 `width` 固定為 `1000`。
    *   對 `self.main_content_frame` 呼叫 `grid_propagate(False)` 以防止其根據子元件內容自動調整大小。
    *   將 `self.main_content_frame` 內部的主欄位 `grid_columnconfigure` 的 `weight` 設置為 `0`，並設定 `minsize` 為 `1000`，確保內容區域的寬度嚴格固定。
    *   調整所有原先直接放置在 `self.master` 中的主要 GUI 元素（如 `top_frame`, `monitor_area_frame`, `writable_params_area_frame`, `chart_area_frame`）的父級為 `self.main_content_frame`，並相應調整其 `grid` 參數。

## 2025年7月3日 進度更新 (圖表座標軸優化)

### 1. 圖表 X 軸動態更新

*   **新增輔助函數 `_get_chart_xaxis_properties`：**
    *   此函數根據傳入的組別（'A' 或 'B'）以及相關的輸入信號選擇參數（`000EH`, `0006H`, `0018H`, `0007H`）來動態決定 X 軸的標題和刻度標籤。
    *   **標題邏輯：**
        *   若選擇 "RS485"，標題直接顯示為 "第一組RS485" 或 "第二組RS485"。
        *   若選擇 "信號 1" 或 "信號 2"，標題直接顯示為 "信號 1" 或 "信號 2"。
    *   **刻度邏輯：**
        *   若為 RS485 信號，刻度保持為 "0%" 和 "100%"。
        *   若為類比信號，則根據對應的類比信號模式（"0~5V", "0~10V", "4~20mA"）將刻度更新為實際的物理單位（如 "0V", "5V"）。
*   **修改圖表繪製函數：**
    *   `_draw_single_output_chart`、`_draw_independent_charts` 和 `_draw_linked_chart` 現在都會呼叫 `_get_chart_xaxis_properties` 來獲取 X 軸的屬性，並用其回傳值來繪製座標軸，取代了原先寫死的標籤。

### 2. 「單組信號-雙組輸出」模式中間刻度修正

*   **`_get_chart_xaxis_properties` 函數增強：**
    *   除了標題和最大/最小刻度，此函數現在還會計算並回傳一個 `mid_label`（中間刻度標籤）。
    *   如果 X 軸的單位是 V 或 mA，`mid_label` 會被計算為範圍的中點（例如，"0V" 和 "5V" 的中點是 "2.5V"）。
    *   如果單位是百分比，`mid_label` 保持為 "50%"。
*   **`_draw_linked_chart` 函數更新：**
    *   繪製 X 軸中間刻度時，不再使用固定的 "50%"，而是使用從 `_get_chart_xaxis_properties` 獲取的 `mid_label` 值，確保了在不同物理單位下中間點刻度的準確性。
