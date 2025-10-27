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

## 遇到的問題與解決方案 (歷史紀錄)

1.  **`_tkinter.TclError: bitmap "..." not defined`**
    *   **問題描述：** 應用程式無法找到 `icon/001.ico` 檔案。
    *   **解決方案：** 確保 `icon` 資料夾及其內容位於正確的路徑，例如 `D:\07python\gemini-daul-controller\icon`，並且 `001.ico` 和 `002.ico` 檔案存在。

2.  **`KeyError: 'is_int'`**
    *   **問題描述：** 在 `_create_widgets` 函數中，當處理 `entry` 類型的參數時，嘗試存取 `param` 字典中不存在的 `is_int` 鍵。
    *   **解決方案：** 修改程式碼，使用 `param.get('is_int', False)` 來安全地存取 `is_int` 鍵，如果不存在則預設為 `False`。

3.  **`_tkinter.TclError: couldn't read file "forest-light.tcl"`**
    *   **問題描述：** 應用程式無法找到 `forest-light.tcl` 主題檔案。
    *   **解決方案：** 確保 `forest-light.tcl` 和 `forest-light` 資料夾位於應用程式的根目錄或可存取的路徑，例如 `D:\07python\gemini-daul-controller\`。

4.  **`AttributeError: 'ModbusMonitorApp' object has no attribute 'writable_params_frame'` (GUI 更新問題)**
    *   **問題描述：** 在 `_update_all_text` 函數中，嘗試存取 `self.writable_params_frame` 屬性時發生錯誤，因為該屬性可能尚未被創建或已被銷毀。這通常發生在 `writable_params_notebook` 及其子框架被重新建立時。
    *   **解決方案：** 在 `_update_all_text` 函數中，添加 `hasattr(self, 'writable_params_notebook')` 等檢查，確保在更新 GUI 元件之前，這些元件已經存在。

5.  **`_tkinter.TclError: invalid command name ".!frame.!frame.!labelframe.!combobox.popdown.f.l"` (ttkbootstrap 主題問題)**
    *   **問題描述：** 使用 `ttkbootstrap` 主題時，特別是 `Combobox` 元件，在某些操作後會出現無效命令名稱的錯誤。這可能與 `ttkbootstrap` 主題的內部狀態管理有關。
    *   **解決方案：** 確保在 `ModbusMonitorApp` 類別初始化時，正確地設定 `ttk.Style().theme_use('litera')`，並且所有 `ttkbootstrap` 元件都使用 `ttk` 模組而不是 `tk` 模組。同時，確保 `forest-light.tcl` 和 `forest-light` 資料夾被正確地包含在應用程式的資源中。

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
    *   確保 `_batch_write_parameters` 函數在批量寫入完成後調用 `_draw_chart`。

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
    *   如果單位是百分比，`mid_label` 保持為 "50%風。
*   **`_draw_linked_chart` 函數更新：**
    *   繪製 X 軸中間刻度時，不再使用固定的 "50%"，而是使用從 `_get_chart_xaxis_properties` 獲取的 `mid_label` 值，確保了在不同物理單位下中間點刻度的準確性。

## 2025年7月5日 進度更新 (GUI 介面優化)

### 1. 即時監控區優化

*   **使用 `ttk.Meter` 取代文字顯示：**
    *   將「輸出電流」和「輸入信號」的純文字顯示改為 `ttkbootstrap` 的 `Meter` 元件，使其更具視覺化效果。
    *   `Meter` 設定為半圓形 (`metertype="semi"`)，並調整了大小和顏色。
    *   使用 `amountformat` 參數確保 `Meter` 元件可以正確顯示小數。
*   **版面佈局調整：**
    *   移除了 `Meter` 上方的獨立標題，將項目名稱直接顯示在 `Meter` 的 `subtext` 中，使介面更簡潔。
    *   將「目前狀態」顯示區移至兩個 `Meter` 元件的下方，並使其橫跨整個監控組的寬度，佈局更合理。

### 2. 可寫入參數區優化

*   **標籤格式調整：**
    *   將可寫入參數的標籤格式從 "寄存器位址: 參數名稱" 修改為 "參數名稱 (寄存器位址)"，使參數名稱更突出，同時保留了必要的地址信息。

## 2025年7月18日 進度更新 (模式切換與視窗顯示問題)

### 1. 問題描述
程式在啟動時，模式選擇對話框沒有正確顯示，導致主程式卡住，無法正常進入主介面。
*   **原因分析：**
    *   在 `__init__` 函數中，主視窗 (`root`) 被 `root.withdraw()` 隱藏。
    *   模式選擇對話框 (`dialog`) 被設定為依附於主視窗 (`dialog.transient(self.master)`)。
    *   由於主視窗是隱藏的，依附於它的對話框也變成了隱藏狀態，導致使用者無法看到並操作對話框。
    *   程式隨後在 `dialog.wait_window()` 處無限期等待，造成邏輯死鎖。

### 2. 修正計畫
1.  **修改 `__init__` 函數：**
    *   移除 `self.master.withdraw()`。
    *   在呼叫 `_show_mode_selection_dialog()` 之前，確保所有潛在的 UI 變數都被初始化為 `None` 或空字典，以避免在 UI 重新建立時出現 `AttributeError`。
    *   在模式選擇完成後（即 `self.controller_mode` 不為 `None` 時），呼叫 `_setup_main_window()` 來設定主視窗的標題和大小，並呼叫 `_create_widgets()` 來建立 UI。
2.  **修改 `_show_mode_selection_dialog` 函數：**
    *   確保對話框的 `transient` 設定不會導致其隱藏。
3.  **修改 `if __name__ == "__main__":` 區塊：**
    *   在創建 `ModbusMonitorApp` 實例之前，將 `root.withdraw()` 移到這裡，確保主視窗在模式選擇對話框顯示之前是隱藏的。
    *   在模式選擇完成後，如果 `app.controller_mode` 不為 `None`，則呼叫 `root.deiconify()` 顯示主視窗。
    *   如果 `app.controller_mode` 為 `None` (使用者關閉了模式選擇對話框)，則呼叫 `root.destroy()` 確保程式正常退出。

## 2025年7月21日 進度更新 (啟動流程修復)

### 1. 問題描述
在 7 月 18 日的修正後，程式出現了新的啟動問題：
1.  **初次修正後：** 視窗閃退，但程式仍在終端機背景執行，無法操作。
2.  **二次修正後：** 視窗完全不出現，程式卡在等待一個不可見的對話框。

*   **根本原因分析：**
    *   一個被 `withdraw()` 隱藏的 `tk.Tk` 或 `ttk.Window` 主視窗，其子視窗 (`Toplevel`) 也會被隱藏。因此，在隱藏主視窗後才建立的模式選擇對話框，使用者根本看不到，導致程式卡在 `dialog.wait_window()`，等待一個永遠不會發生的互動。

### 2. 最終修正方案
採用了更穩健的啟動流程，將視窗的顯示與隱藏邏輯完全封裝在 `ModbusMonitorApp` 類別的 `__init__` 函數中：

1.  **`__init__` 函數：**
    *   在函數一開始，立刻呼叫 `self.master.withdraw()` 隱藏主視窗。
    *   初始化所有必要的變數。
    *   呼叫 `_show_mode_selection_dialog()` 顯示模式選擇對話框。
    *   **關鍵：** 如果使用者在對話框中選擇了一個模式 (`self.controller_mode` 有值)，則繼續執行後續的 UI 建立 (`_setup_main_window`, `_create_widgets`)。
    *   在所有 UI 元件都建立完成後，最後才呼叫 `self.master.deiconify()` 將配置好的主視窗顯示給使用者。
    *   如果使用者直接關閉了模式選擇對話框，`__init__` 函數會提前返回，主程式的 `mainloop` 也不會啟動，從而實現乾淨的退出。

2.  **`_show_mode_selection_dialog` 函數：**
    *   移除了 `dialog.transient(self.master)`，解除對話框與主視窗的依附關係，確保即使主視窗被隱藏，對話框也能獨立顯示。
    *   將對話框的關閉按鈕 (`WM_DELETE_WINDOW`) 的行為設定為直接銷毀主視窗 (`self.master.destroy`)，這能確保在使用者不想選擇模式時，整個應用程式能完全關閉，避免留下「殭屍」進程。

3.  **`if __name__ == "__main__":` 區塊：**
    *   大幅簡化，只負責建立 `ttk.Window` 和 `ModbusMonitorApp` 的實例，然後無條件啟動 `root.mainloop()`。整個啟動流程的複雜邏輯都已移交給 `ModbusMonitorApp` 類別內部處理，使得主程式碼區塊更清晰，並且能正確處理 `mainloop` 在視窗被提前銷毀時可能拋出的 `TclError`。

### 3. 目前狀態
程式已能穩定、正確地啟動。模式選擇對話框會優先顯示，使用者做出選擇後，主視窗才會出現。若使用者關閉選擇對話框，程式會乾淨地退出。接下來將由使用者進行全面的功能測試。

## 2025年7月21日 進度更新 (功能修正)

根據使用者的測試回饋，完成了以下四項功能修正：

### 1. 參數顯示/寫入邏輯修正

*   **問題 1 (雙組模式 `entry_scaled` 顯示錯誤)：** 雙組輸出模式下，`0015H`, `0016H`, `001FH`, `0020H` 等 `entry_scaled` 類型的參數在讀取後未正確乘以比例因子，導致顯示值錯誤（例如，讀取到 7 卻顯示為 0.7）。
    *   **解決方案：** 修改 `_update_writable_params_area` 函數，為 `entry_scaled` 類型的參數新增一個獨立的處理分支，確保從寄存器讀取到的值會乘以其在 `writable_params_config` 中定義的 `scale` 後再顯示於介面。

*   **問題 3 (單組模式 `000CH` 邏輯錯誤)：** 單組輸出模式下，`000CH`（震顫頻率）的讀取和寫入邏輯不正確。
    *   **解決方案：**
        1.  修改 `single_writable_params_config` 中 `000CH` 的定義，將其 `scale` 從 `1` 修正為 `10`。
        2.  由於 `entry_scaled` 類型的處理邏輯已在問題 1 中修正，現在 `000CH` 在讀取時會自動乘以 10 顯示，在寫入時（透過 `_validate_single_param_for_batch` 函數）會自動除以 10 存入，使其行為與預期一致。

### 2. 即時監控邏輯修正

*   **問題 2 (單組模式電流顯示為 0)：** 單組輸出模式下，`0000H` 的輸出電流值在即時監控區始終顯示為 0。
    *   **解決方案：** 修改 `_update_monitor_area` 函數，移除了原本錯誤的判斷 `100 if self.controller_mode == 'single' else 0.1`，並將單組模式和雙組模式 A 組的電流換算比例 (`scale`) 都修正為 `100`，確保電流值能被正確轉換並顯示。

### 3. 檔案儲存路徑重構

*   **問題 4 (本地存檔混用)：** 本地儲存功能未區分模式和語言，導致所有設定檔都存在同一個資料夾下，容易造成不相容的設定檔被誤用。
    *   **解決方案：**
        1.  **新增 `_get_parameters_dir` 輔助函數：** 此函數會根據當前的控制器模式 (`self.controller_mode`) 和語言 (`self.current_language_code`) 回傳一個唯一的資料夾路徑（例如 `modbus_parameters/zh_dual` 或 `modbus_parameters/en_single`）。
        2.  **修改 `_save_parameters_to_file` 函數：** 在儲存檔案前，呼叫 `_get_parameters_dir` 來確定目標資料夾，並自動建立不存在的資料夾，確保設定檔被存放在正確的分類路徑下。
        3.  **修改 `_load_parameters_from_file` 函數：** 在讀取檔案時，同樣呼叫 `_get_parameters_dir`，只列出並讀取當前模式與語言對應的資料夾中的設定檔，從根本上避免了混淆。

## 2025年7月21日 進度更新 (使用者體驗優化)

根據使用者的回饋，完成了以下幾項介面和邏輯的優化：

### 1. 模式切換介面優化

*   **問題：** 原本的「切換模式」按鈕不夠直觀，且相關提示訊息只有中文。
*   **解決方案：**
    1.  將 `Button` 元件改為 `ttk.Combobox`，並用一個 `LabelFrame` 包裝，使其功能更清晰，外觀更統一。
    2.  新增 `SWITCH_MODE_FRAME_TEXT`, `DUAL_MODE_OPTION`, `SINGLE_MODE_OPTION`, `CONFIRM_SWITCH_MODE_TITLE`, `CONFIRM_SWITCH_MODE_MSG` 等中英文翻譯鍵。
    3.  重構模式切換的事件處理函數 `_on_mode_select`，確保在切換時能正確處理中英文提示，並在使用者取消操作時，`Combobox` 的選項會自動恢復原狀。
    4.  修正了因元件替換而遺漏的 `_update_all_text` 函數中的更新邏輯，確保在切換語言時，新的模式切換介面也能正確顯示對應的語言。

### 2. 批次寫入流程優化

*   **問題：** 批次寫入時，使用者無法得知目前的進度，且缺少對關鍵參數的邏輯驗證。
*   **解決方案：**
    1.  **新增進度條視窗：** 重構 `_batch_write_parameters` 函數，在開始寫入前，建立一個包含 `ttk.Progressbar` 和狀態標籤的 `Toplevel` 視窗。在遍歷寫入每個寄存器時，即時更新進度條和狀態文字，寫入完成或失敗後自動關閉視窗。
    2.  **新增最大/最小電流邏輯驗證：** 在 `_batch_write_parameters` 函數的開頭，加入對最大/最小電流的檢查。根據當前是單組還是雙組模式，檢查對應的參數（`0010H` vs `0011H`, `001AH` vs `001BH`, `0008H` vs `0009H`），確保最大電流值不小於最小電流值 + 0.1。若驗證失敗，則彈出對應的中英文錯誤訊息並中止寫入。
    3.  為新的進度條和錯誤訊息新增了 `BATCH_WRITE_PROGRESS_TITLE`, `BATCH_WRITE_IN_PROGRESS`, `CURRENT_RANGE_ERROR_A`, `CURRENT_RANGE_ERROR_B`, `CURRENT_RANGE_ERROR_S` 等中英文翻譯鍵。

### 3. 即時監控顯示修正

*   **問題：** 切換語言時，即時監控區 `Meter` 元件的子標題（輸出電流、輸入信號）不會跟著改變。
*   **解決方案：** 在 `_update_all_text` 函數中，為單組和雙組模式的處理分支明確加入了更新 `Meter` 元件 `subtext` 的程式碼，確保語言切換時所有介面元素都能同步更新。

## 2025年7月22日 進度更新

### 1. 恢復出廠設置功能改進

*   **問題：** 單組/雙組控制器的「恢復出廠設置」功能未按預期動作，且缺少倒數計時提示。
*   **解決方案：**
    1.  在 `TEXTS` 語言包中新增 `FACTORY_RESET_COUNTDOWN_MSG` 翻譯鍵，用於倒數計時提示。
    2.  新增 `_show_countdown_window` 函數，用於顯示一個模態的 10 秒倒數計時視窗。
    3.  新增 `_execute_factory_reset` 函數，統一處理恢復出廠設置的完整邏輯：
        *   停止 Modbus 輪詢。
        *   發送重置命令（值 5）到控制器。
        *   顯示 10 秒倒數計時視窗。
        *   倒數結束後，重新讀取所有控制器參數並更新 GUI。
        *   重新啟動 Modbus 輪詢。
    4.  修改 `_write_single_register` 函數，移除舊的恢復出廠設置特殊處理，統一呼叫 `_execute_factory_reset`。
    5.  修改 `_batch_write_parameters` 函數，當選擇「恢復出廠設置」並確認後，呼叫 `_execute_factory_reset`。

### 2. GUI 狀態管理修正

*   **問題：** 在 `_set_gui_state` 函數中，嘗試存取不存在的 `self.mode_switch_button` 屬性，導致 `AttributeError`。
*   **解決方案：** 將 `_set_gui_state` 函數中的 `self.mode_switch_button` 替換為正確的 `self.mode_combobox`，確保 GUI 元件狀態能被正確管理。

### 3. 即時監控區「目前狀態」標題語言切換修正

*   **問題：** 切換語言時，即時監控區的「目前狀態」標題不會隨之切換。
*   **解決方案：** 修改 `_update_all_text` 函數，確保在語言切換時，`monitor_display_controls_a['0002H']` 和 `monitor_display_controls_b['0005H']` 所對應的 `LabelFrame` 的 `text` 屬性也能被更新。

## 2025年10月22日 進度更新 (即時圖表功能新增與修正)

### 1. 即時圖表功能新增

*   **新增 `RealtimeChartWindow` 類別：**
    *   實現了一個獨立的彈出視窗，用於顯示即時的「輸出電流 vs 時間」和「輸入信號 vs 時間」圖表。
    *   圖表支援雙 Y 軸，左側顯示電流 (0-3A)，右側顯示輸入信號 (0-100%)。
    *   X 軸為時間軸，預設顯示最近 20 秒的數據。
    *   根據控制器模式（單組或雙組）動態調整圖表數量和顯示內容。
    *   提供「儲存圖表數據」按鈕，可將過去最多 200 秒的數據儲存為 CSV 檔案。
*   **`ModbusMonitorApp` 類別修改：**
    *   在 `__init__` 中新增了 `deque` 數據結構，用於儲存 Modbus 讀取的歷史數據（電流、信號、時間）。
    *   在 `_update_monitor_area` 函數中，將最新的 Modbus 數據添加到歷史數據 `deque` 中，並觸發 `RealtimeChartWindow` 的圖表更新。
    *   新增了「即時圖表」按鈕，用於開啟/關閉 `RealtimeChartWindow`。
    *   更新了 `_update_all_text` 函數，確保在語言切換時，`RealtimeChartWindow` 中的文字也能正確更新。
*   **`TEXTS` 字典更新：**
    *   新增了 `CHART_SAVE_SUCCESS_MSG` 和 `CHART_SAVE_ERROR_MSG` 翻譯鍵。
    *   確認並使用了現有的圖表相關翻譯鍵，如 `SHOW_CHART_BUTTON`, `CHART_WINDOW_TITLE`, `Y_AXIS_CURRENT`, `Y_AXIS_SIGNAL`, `X_AXIS_TIME` 等。

### 2. 圖表按鈕顯示問題修正

*   **問題描述：** 首次實作後，使用者回報即時圖表按鈕未顯示。
*   **原因分析：** 按鈕原先使用 `place` 佈局管理器，可能與父容器的 `grid` 佈局產生衝突或被覆蓋。
*   **解決方案：** 將 `_create_dual_controller_ui` 和 `_create_single_controller_ui` 函數中「即時圖表」按鈕的佈局方式從 `place` 修改為 `grid`，確保其能可靠地顯示在即時監控區的右上角。

## 2025年10月23日 進度更新 (即時圖表功能優化與修正)

根據使用者回饋，針對昨日新增的「即時圖表」功能進行了多項修正與優化。

### 1. 圖表中文顯示問題

*   **問題描述：** 在中文介面下，圖表中的所有中文（標題、座標軸標籤、圖例）都顯示為亂碼（方框）。
*   **原因分析：** 繪圖函式庫 `Matplotlib` 使用的預設字體不包含中文字元。
*   **解決方案：** 在程式啟動時，透過 `matplotlib.rcParams` 將 `Matplotlib` 的預設字體設定為支援中文的 `Microsoft YaHei`，並設定 `axes.unicode_minus` 為 `False` 以確保負號能正常顯示。

### 2. 圖表Y軸標籤位置錯誤

*   **問題描述：** 圖表的右側Y軸標籤（輸入信號）被錯誤地顯示在左側。
*   **解決方案：** 修改 `RealtimeChartWindow` 中的 `_setup_axes` 函數，為右側座標軸 `ax2` 明確地設定其標籤和刻度的顯示位置 (`ax2.yaxis.set_label_position("right")` 和 `ax2.yaxis.tick_right()`)。

### 3. 圖表顯示卡頓問題

*   **問題描述：** 開啟即時圖表後，整個應用程式的操作變得非常卡頓。
*   **原因分析：** 圖表更新邏輯效率低下，每次更新都會將整個圖表（背景、座標軸、線條等）完全清除並重繪。
*   **解決方案：**
    1.  重構 `RealtimeChartWindow` 類別，將圖表的靜態元素（座標軸、標題、網格等）改為只在創建時繪製一次。
    2.  將 `update_chart_data` 函數的邏輯從「清除並重繪」改為僅使用 `set_data()` 方法更新線條的數據。
    3.  為進一步確保流暢度，將圖表的更新頻率從 100毫秒 (10Hz) 降低至 250毫秒 (4Hz)。

### 4. 主畫面監控數值換算錯誤

*   **問題 1 (輸出電流)：** 主畫面的「輸出電流」`Meter` 元件顯示數值錯誤，例如 `0.2A` 被顯示為 `2` 而不是 `200` (mA)。
    *   **解決方案：** 修正 `_update_monitor_area` 函數中的換算邏輯，將從控制器讀取的原始值乘以 10 (`raw_current * 10`) 以得到正確的 mA 單位數值。
*   **問題 2 (輸入信號 - Regression)：** 在修正電流問題時，錯誤地移除了「輸入信號」的換算，導致其顯示值變為預期的 10 倍 (例如 50% 顯示為 500%)。
    *   **解決方案：** 在 `_update_monitor_area` 函數中，恢復對信號原始值的 `/ 10.0` 操作，確保其在主畫面和即時圖表中都顯示為正確的百分比。

### 5. 雙組模式「即時圖表」按鈕顯示問題

*   **問題描述：** 在雙組輸出模式下，「即時圖表」按鈕被 B 組的監控視窗完全遮擋，無法看見或點擊。
*   **原因分析：** `_create_dual_controller_ui` 函數中的 Grid 佈局發生衝突，按鈕和 B 組監控視窗被放置在同一個儲存格。
*   **解決方案：** 重新規劃 `monitor_area_frame` 的佈局，將「即時圖表」按鈕放置在 `row=0`，而兩個監控視窗 (`monitor_frame_a`, `monitor_frame_b`) 則放置在 `row=1`，從結構上分離兩者，確保按鈕始終可見。

## 2025年10月24日 進度更新 (靜態與即時圖表修正)

### 1. 單組模式靜態圖表語言切換問題

*   **問題描述:** 在單組控制器模式下，切換程式語言時，主畫面下方的靜態特性曲線圖 (`chart_area_frame`) 的標題與內容不會更新。
*   **原因分析:** 語言更新函式 `_update_all_text` 在處理單組模式的邏輯分支中，遺漏了更新圖表標題 (`self.chart_frame`) 以及呼叫重繪函式 (`_draw_single_controller_chart`) 的程式碼。
*   **解決方案:** 在 `_update_all_text` 函式的 `elif self.controller_mode == 'single':` 區塊中，補上更新圖表標題和呼叫重繪函式的程式碼，確保語言變更時圖表能被即時刷新。

### 2. 雙組模式即時圖表與監控區顯示問題

*   **問題描述:** 在修復上述問題後，衍生出兩個新問題：
    1.  在雙組模式下，彈出式「即時圖表」視窗雖然不再報錯，但曲線變成一片空白，且 X 軸（時間軸）被凍結。
    2.  無論是單組或雙組模式，主畫面「即時監控區」的儀表 (`Meter`) 元件數值都卡在 0，無法刷新（功能退化 Regression）。
*   **原因分析與解決過程:**
    1.  **儀表數值為 0:** 經查，前次修改 `_update_monitor_area` 函式時，將更新 `Meter` 元件的方式從 `.configure(amountused=...)` 簡化為直接屬性賦值 (`.amountused = ...`)，導致 `ttkbootstrap` 元件更新失效。
    2.  **圖表曲線空白:** 使用者提供了關鍵線索：「雙組模式的 X 軸是凍結的」。這表示 Matplotlib 子圖表 (subplot) 之間的 X 軸共享機制在當前複雜的 GUI 嵌入環境下沒有如預期般自動生效。即使程式碼更新了第一個圖表的 X 軸範圍，第二個圖表也未跟隨變動，反之亦然，最終導致整個 X 軸更新失敗。
*   **最終解決方案:**
    1.  **修復儀表:** 將 `_update_monitor_area` 函式中更新 `Meter` 的程式碼改回使用 `.configure(amountused=...)` 方法，恢復了即時監控區的正常顯示。
    2.  **修復圖表:** 修改 `RealtimeChartWindow` 中的 `_create_charts` 函式。在建立第二個子圖表時，透過 `sharex` 參數，**明確地**將其 X 軸與第一個子圖表共享 (`ax1_b = self.figure.add_subplot(212, sharex=ax1_a)`)。此舉強制了兩個圖表的 X 軸聯動，徹底解決了 X 軸凍結和曲線無法顯示的問題。
