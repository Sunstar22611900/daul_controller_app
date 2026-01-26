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



## 2025年12月31日 進度更新 (快速設定精靈優化)



### 1. 精靈啟動與連線修復

*   **問題：** 應用程式啟動時或精靈連線時發生 `ValueError` 與 `Modbus Error`。

*   **解決方案：**

    *   **延遲寫入機制：** 移除精靈完成後立即觸發的批次寫入，改為設定 `auto_batch_write_pending` 旗標，待主程式連線建立後才安全執行。

    *   **動態寄存器讀取：** 修正 `_read_initial_values`，根據單組/雙組模式動態決定讀取的寄存器數量 (14 或 40)，解決 Modbus 讀取錯誤。



### 2. 參數寫入邏輯精煉

*   **問題：** 精靈結束時會覆寫未修改的參數，或將唯讀參數寫入導致錯誤。

*   **解決方案：**

    *   **修改追蹤 (`modified_regs`)：** 在 `QuickSetupWizard` 中新增 `modified_regs` 集合，僅記錄使用者實際操作過的參數。

    *   **過濾寫入：** `_apply_parameters` 函數現在只會寫入同時存在於允許列表 (`allowed_regs`) 且在 `modified_regs` 中的參數。



### 3. 雙組模式精靈修復 (SY-DPCA-*-2)

*   **A組反饋選擇 (1組流程)：** 補回遺漏的 `_render_step_a_feedback_1g` 介面，並實作下拉選單過濾功能。

*   **連動輸入邏輯：** 在「雙組連動」模式下，選擇 A 組輸入時，現在會自動將對應的 B 組輸入寄存器 (`0018H`) 標記為已修改，確保正確寫入。

*   **1組輸出流程：** 選擇「1組輸出」時，強制將 B 組輸入 (`0018H`) 設為「無輸出」並寫入，確保 B 組被正確關閉。

*   **條件式反饋設定：** 針對所有反饋選擇步驟 (A組1G/2G, B組2G)，新增了邏輯判斷：若選擇「信號1」或「信號2」，會自動插入對應的信號設定步驟 (`0006H`/`0007H`)，避免設定遺漏。



### 4. 使用者體驗改善

*   **新增「快速設定精靈」按鈕：** 在主程式上方工具列（語言選單旁）新增按鈕，點擊後可直接重啟應用程式並重新進入精靈流程。

*   **文字優化：** 根據使用者回饋，更新了精靈各步驟的標題與說明文字，使其更直觀。
 


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

## 2026年1月14日 進度更新 (精靈流程與介面優化)

### 1. 快速設定精靈流程簡化 (雙組控制器)

*   **合併步驟：** 將原有的「Step 4: 選擇輸出線圈組數」與「Step 5: 選擇控制模式」合併為單一的「Step 4 Combined: 選擇控制模式」。
*   **新介面設計：** 新的步驟提供三個明確的選項，直接對應三種常用模式，簡化使用者決策：
    1.  **模式一 (Mode 1)：** 單組信號 vs 單組輸出 (對應舊流程：1組輸出 -> 單信號)
    2.  **模式二 (Mode 2)：** 雙組獨立信號 vs 雙組獨立輸出 (對應舊流程：2組輸出 -> 獨立輸入)
    3.  **模式三 (Mode 3)：** 單組信號 vs 雙組連動輸出 (對應舊流程：2組輸出 -> 共用輸入)
*   **邏輯更新 (`QuickSetupWizard`)：**
    *   新增 `_render_step_dual_combined()` 方法負責繪製新介面。
    *   更新 `_on_next()` 邏輯，根據使用者在 Step 4 Combined 的選擇，自動設定對應的寄存器 (如 `0018H` 設為 0 或虛擬變數 `input_mode`)，因為選擇本身已隱含了這些設定。
    *   修正 `_show_step()` 方法，補上了對 `4_dual_combined` 步驟的調度處理。

### 2. 介面佈局與視覺優化

*   **垂直排列按鈕：** 應使用者要求，將模式選擇按鈕從水平排列改為由上到下的垂直排列。
*   **Rich Text 按鈕實現：**
    *   為了讓按鈕內的文字更易讀（標題加粗加大、描述正常），捨棄了標準的 `ttk.Radiobutton`。
    *   使用 `ttk.Frame` 搭配兩個 `ttk.Label` (標題與描述) 自定義實作了「類 RadioButton」元件。
    *   實作了點擊事件綁定與 `variable.trace` 監聽，確保自定義元件能像標準 RadioButton 一樣響應選擇並改變外觀樣式 (Bootstyle)。
*   **翻譯更新：** 在 `TEXTS` 字典的繁體中文 (`zh`) 與英文 (`en`) 區塊中，更新了對應的新標題與模式描述文字。

## 2026年1月15日 進度更新 (精靈邏輯優化)

### 1. 快速設定精靈「上一步」邏輯優化

*   **問題描述：** 原本在精靈的「Step 3: 連接控制器」步驟，若使用者已經建立 Modbus 連線但隨後按下「上一步」返回型號選擇頁面，Modbus 連線並未斷開。這可能導致在型號切換或其他操作時發生狀態衝突或困惑。
*   **功能調整：** 修改了 `QuickSetupWizard._on_back` 方法的行為。
*   **實作細節 (`dual_controller_app.py`)：**
    *   在 `_on_back` 函數開頭加入檢查：若當前步驟為 3 且 `self.modbus_master` 存在 (即已連線)，則強制呼叫 `self._try_connect()` 來斷開連線。
    *   確保使用者在退回 Step 2 (型號選擇) 之前，連線狀態已完全重置。

## 2026年1月16日 進度更新 (深色主題與無邊框視窗)

### 1. PID 參數調整
*   **範圍變更：** 將 PID 參數 (0022H ~ 0027H) 的數值範圍從 0-100 擴展至 0-1000。
*   **介面優化：** 將上述參數的輸入方式從 `Entry` 輸入框改為 `Scale` 拉桿，並顯示當前數值，提供更直觀的操作體驗。

### 2. 深色主題與圖表適配
*   **主題更換：** 應用程式主題切換為 `cyborg` (深色風格)。
*   **圖表修正：** 因應深色背景，將圖表 (Canvas) 的座標軸、格線與文字顏色從黑色/灰色改為白色/淺灰色，確保在深色主題下的可視性。解決了 `_tkinter.TclError` 關於 `outline` 屬性的錯誤。

### 3. 無邊框視窗設計
*   **移除系統邊框：** 啟用 `overrideredirect(True)` 移除 Windows 預設視窗邊框。
*   **自定義標題列：** 實作了整合於介面內的自定義標題列：
    *   **拖曳功能：** 支援拖曳標題列移動視窗。
    *   **視窗控制：** 新增自定義的「最小化」與「關閉」按鈕。
    *   **標題顯示：** 標題文字會隨模式（單/雙控制器）與語言切換自動更新。

## 2026年1月19日 進度更新 (控制器圖表視窗重構)

### 1. 控制器模式圖表視窗化
*   **功能重構：** 將原本嵌在主視窗即時監控區下方的「控制器模式圖表區」，獨立移出成為一個浮動視窗。
*   **目的：** 優化主畫面空間配置，解決在低解析度螢幕上內容可能被截斷的問題。
*   **介面調整：**
    *   移除了主視窗底部的圖表 Frame。
    *   新增了一顆「控制器模式圖表」按鈕 (取代原區域)，點擊後開啟浮動視窗。
    *   浮動視窗採用 **無邊框設計 (Frameless)**，且支援點擊視窗任一處進行拖曳移動 (與 Real-time Chart 行為一致)。

### 2. 遇到的問題與解決方案

*   **`AttributeError: 'ModbusMonitorApp' object has no attribute 'chart_frame'`**
    *   **原因：** 重構移除主視窗的 `chart_frame` 後，`_update_all_text` 函式仍嘗試去設定該 Frame 的標題文字。
    *   **修正：** 修改 `_update_all_text`，移除對 `chart_frame` 的直接引用，改為若按鈕存在則更新按鈕文字，若浮動視窗開啟則更新浮動視窗的標題。

*   **圖表視窗空白 (Empty Window)**
    *   **原因：** 在程式碼合併過程中，新定義的 `ControllerModeChartWindow` 類別被錯誤地縮排到了 `RealtimeChartWindow` 類別內部，導致兩個視窗類別的結構損壞，無法正確建立。
    *   **修正：** 將 `ControllerModeChartWindow` 類別移至正確的模組層級 (Module Level)，修復了類別定義。

*   **單組模式啟動錯誤 (`AttributeError: 'NoneType' object has no attribute 'winfo_exists'`)**
    *   **原因：** 在單組控制器模式 (`single`) 下啟動程式時，`_update_all_text` 會嘗試呼叫 `_draw_single_controller_chart`。此時 `chart_canvas` 尚未被建立 (因為圖表視窗預設未開啟)，導致 `self.chart_canvas` 為 `None`，呼叫 `winfo_exists` 時發生錯誤。
    *   **修正：** 在 `_draw_single_controller_chart` 函式開頭加入防呆檢查：`if not hasattr(self, 'chart_canvas') or self.chart_canvas is None: return`。

*   **單組模式圖表繪製錯誤 (`KeyError: '000EH'`)**
    *   **原因：** 單組模式下點擊開啟圖表時，`_draw_chart` 函式預設會去讀取雙組模式專用的寄存器 (如 `000EH`) 來判斷圖表類型，因單組模式的 `writable_entries` 中沒有這些鍵值而報錯。
    *   **修正：** 修改 `_draw_chart` 函式 (現在作為統一的繪圖入口)，在執行任何邏輯前先檢查 `self.controller_mode`。若是 `'single'` 模式，則直接轉呼叫 `_draw_single_controller_chart()` 並返回；若是 `'dual'` 模式才執行原有的判斷邏輯。

### 3. 即時趨勢圖優化 (Realtime Chart Optimization)

*   **風格統一 (Theming)**：
    *   將即時趨勢圖視窗 (`RealtimeChartWindow`) 的背景色與圖表樣式改為與主程式一致的 "superhero" 深色主題 (`#2b3e50`)，文字與座標軸顏色調整為白色以確保可視性。

*   **版面重構 (Layout)**：
    *   **尺寸調整**：將視窗預設尺寸從 800x600 縮小至 800x400，使畫面更輕量。
    *   **排列方式**：在雙組控制器模式下，原本上下排列的兩個圖表改為 **左右並排**，更符合寬螢幕的使用習慣。

*   **Bug 修復**：
    *   **雙組圖表連動失效**：修復了在改為左右排列後，右側圖表 (B組) 無法隨時間軸滾動更新的問題。
        *   **原因**：左右排列 (`subplot(121), subplot(122)`) 預設未共享 X 軸。
        *   **修正**：在建立第二個子圖表時明確指定 `sharex=ax1_a`，強制兩者時間軸同步。

## 2026年1月20日 進度更新 (批量寫入優化)

### 1. 批量寫入功能優化 (Batch Write Optimization)

*   **功能改進：** 修改了 `_batch_write_parameters` 函數，實作了「差異寫入」機制。
    *   **快取機制：** 新增 `self.last_read_registers_dict` 字典，用於快取每次讀取到的最新寄存器數值。
    *   **寫入判斷：** 在批量寫入時，程式會將介面上的輸入值與快取中的原始值進行比對。
    *   **效能提升：** 只有當數值確實發生變更（或是使用者清空的欄位）才會被加入寫入列表，未修改的參數將被自動跳過，大幅縮短了與控制器通訊的時間。
    *   **空操作提示：** 若使用者點擊寫入按鈕但未修改任何參數，程式會直接彈出提示視窗「未檢測到參數變更 (`NO_CHANGES_DETECTED`)」，而不發送任何 Modbus 指令。

*   **新增翻譯鍵：**

    *   `NO_CHANGES_DETECTED`: "未檢測到參數變更。" (zh) / "No parameter changes detected." (en)

## 2026年1月22日 進度更新 (程式碼審查與重構)

### 1. 程式碼審查 (Code Review)

*   **執行審查：** 對 `dual_controller_app.py` 進行了全面的程式碼審查，識別出潛在的維護性和可靠性問題。
*   **主要發現：**
    *   **硬編碼限制 (Hardcoded Limits)：** 圖表繪製邏輯中使用了硬編碼的電流上限 (3.0A)，若硬體規格變更將難以維護。
    *   **恢復出廠設置時序 (Factory Reset Timing)：** 恢復出廠設置後僅依靠固定的睡眠時間 (sleep) 來等待設備重啟，這在不同設備或負載下可能不可靠。

### 2. 重構與優化

根據審查結果，實施了以下改進：

*   **圖表電流上限常數化：**
    *   在 `ModbusMonitorApp` 類別中新增了 `MAX_CHART_CURRENT_AMPS` 常數（預設為 3.0）。
    *   更新了所有圖表繪製函數 (`_draw_single_controller_chart`, `_draw_independent_charts`, `_draw_linked_chart`, `_draw_single_output_chart`)，將原本的硬編碼數值替換為使用此常數。這提高了程式碼的可維護性，未來若需調整電流範圍，只需修改一處。

*   **恢復出廠設置可靠性提升 (Ping 機制)：**
    *   重寫了 `_post_reset_actions` 函數。
    *   **新增 Ping 機制：** 在恢復出廠設置倒數結束後，不再盲目地立即恢復輪詢，而是進入一個「Ping 迴圈」。
    *   **邏輯：** 程式會嘗試讀取一個安全的 Modbus 寄存器（最多嘗試 5 次）。只有在成功收到設備回應（代表設備已重啟並上線）後，才會重新讀取所有參數並恢復 GUI 的即時監控輪詢。
    *   這大幅提升了功能的穩健性，避免了因設備重啟較慢而導致的讀取錯誤。

### 3. 使用者手冊與體驗調整

*   **倒數時間調整：** 根據使用者反饋，將恢復出廠設置的倒數等待時間從 10 秒縮短為 3 秒，改善操作流暢度。
*   **訊息提示優化：** 註解掉了恢復出廠設置成功後的 `messagebox.showinfo` 提示，避免使用者需要額外點擊確認，使流程更順暢。


## 2026年1月23日 進度更新 (程式重構與除錯)

### 1. 程式碼重構 (Refactoring)

為了提高程式碼的可維護性與擴充性，進行了大幅度的重構，將原本龐大的 \`ModbusMonitorApp\` 類別拆分為多個職責單一的類別：

*   **\`ModbusClient\`**: 封裝所有 Modbus 通訊邏輯，包括連接、斷開、讀取、寫入及執行緒安全的鎖定機制。
*   **\`ConfigManager\`**: 負責參數設定檔的儲存、讀取與與路徑管理。
*   **\`ChartManager\`**: 專門處理圖表數據的儲存、更新與歷史記錄管理。
*   **\`ModbusMonitorApp\`**: 作為主要控制器，協調上述各模組與 GUI 的互動。

### 2. 除錯與修正 (Debugging & Fixes)

在重構後，針對使用者回報的問題進行了以下修正：

*   **快速設定精靈 (QuickSetupWizard) 錯誤修正:**
    *   修正了 Wizard 中錯誤引用 \`self.master\` (在此情境下為 root window) 來存取 \`modbus_client\` 的問題，改為正確引用 \`self.app.modbus_client\`。
    *   **結果:** 解決了 Wizard 無法寫入參數及完成設定的 \`AttributeError\`。

*   **Modbus 連接邏輯修正:**
    *   移除了 \`ModbusMonitorApp\` 中所有對已廢棄屬性 \`self.modbus_master\` 的引用，全面改用 \`self.modbus_client.is_connected\` 來判斷連線狀態。
    *   **結果:** 解決了在 \`_update_all_text\` (更新 UI 文字) 和 \`_on_closing\` (關閉程式) 時因屬性不存在而導致的崩潰。

*   **設定精靈流程優化:**
    *   修正了 \`_on_next\` 和 \`_on_back\` 的邏輯。現在，如果在 Wizard 第 3 步 (連線設定) 按下「上一步」，程式會正確地斷開 Modbus 連線，避免連線被錯誤地保留到前一步驟。

*   **參數存檔與讀檔修正:**
    *   修正了 \`ConfigManager\` 中 \`save_parameters\` 和 \`load_parameters\` 方法被呼叫時參數順序錯誤的問題。
    *   修正了 \`list_files\` 方法參數順序錯誤的問題，這導致程式在讀取檔案時去錯誤的資料夾 (\`dual_zh\`) 尋找檔案，而不是正確的 (\`zh_dual\`)。
    *   **結果:** 「本地儲存」與「本地讀取」功能現在可以正確地在對應語言與模式的資料夾中存取檔案。

*   **模式切換錯誤修正:**
    *   修正了在切換單/雙組模式時，因嘗試清除已移除的 \`self.time_history\` 屬性而導致的錯誤。改為呼叫 \`self.chart_manager.clear_history()\`。
"

### 3. 使用者介面優化 (UI Improvements)

*   **對話視窗一致性優化:**
    *   將「本地儲存」(_save_parameters_to_file) 和「本地讀取」(_load_parameters_from_file) 的視窗統一修改為無邊框 (frameless) 且置中顯示的樣式，以符合應用程式整體的視覺風格。
    *   新增 \`_center_toplevel\` 輔助方法，確保這些浮動視窗能精確地顯示在螢幕正中央。
    *   移除了無邊框視窗的 \`transient\` 屬性，並加入 \`lift\` 和 \`focus_force\`，解決了視窗可能被主視窗遮擋而不見的問題。

*   **批次寫入進度視窗置中:**
    *   將「批次寫入參數」時跳出的進度條視窗也應用了置中邏輯，改善使用者體驗，不再出現於螢幕左上角。

### 4. 嚴重錯誤修正 (Critical Bug Fixes)

*   **斷線重連機制修復:**
    *   **屬性遺失錯誤:** 修正了 \`AttributeError: 'ModbusMonitorApp' object has no attribute 'connection_info'\`。在 \`ModbusMonitorApp\` 初始化時正確建立了 \`self.connection_info\` 字典，並確保在每次連線成功（無論是通過 Wizard 還是主畫面）時都會更新其中的 port 和 baudrate 資訊。
    *   **重連邏輯錯誤:** 修正了 \`_handle_disconnection_error\` 中的重連邏輯。原先錯誤地直接使用已廢棄的 \`modbus_master\` 或未帶參數呼叫連線。現在改為使用 \`self.connection_info\` 中儲存的資訊，透過 \`self.modbus_client.connect()\` 顯式地重新建立連線，確保重連流程的可靠性。

## 2026年1月26日 進度更新 (客製化 Messagebox)

### 1. 客製化訊息視窗實作

*   **目標：** 替換原有的 `tkinter.messagebox`，使其風格與主程式 ("superhero") 一致，並能正確置中於主視窗或快速設定精靈。

*   **實作細節 (`CustomMessagebox` 類別)：**
    *   **無框設計：** 使用 `overrideredirect(True)` 移除視窗標題列。
    *   **風格統一：** 背景色與按鈕樣式採用與 "superhero" 主題相符的深色系。
    *   **動態置中：** 使用 `_get_parent()` 邏輯動態偵測當前焦點視窗（主視窗或 Wizard），將訊息視窗置中於該父視窗。
    *   **按鈕在地化：** `askyesno` (Question) 類型的視窗按鈕會根據應用程式當前語言顯示「是/否」或「Yes/No」。

*   **整合：**
    *   在 `dual_controller_app.py` 中新增 `CustomMessagebox` 類別。
    *   將原本的 `messagebox` 匯入替換為 `CustomMessagebox` 類別的別名，確保現有程式碼無需大幅修改即可套用新視窗。
    *   引入 `GLOBAL_ROOT` 與 `GLOBAL_APP` 全域變數，供 `CustomMessagebox` 存取主視窗參考與應用程式語言設定。