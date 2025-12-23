# SUNSTAR Modbus RTU 控制器監控軟體 (V2.0)

這是一款使用 Python 開發的桌面應用程式，專為監控和調整 SUNSTAR 的 **SY-DPCA-*-1 (單組)** 和 **SY-DPCA-*-2 (雙組)** 控制器而設計。

<img width="960" alt="image" src="https://github.com/user-attachments/assets/51e04fba-3dfd-44c7-8e27-916826353510" />

## ✨ 主要功能

-   **雙型號支援**：
    -   程式啟動時會彈出對話框，讓使用者選擇要操作的控制器型號（單組或雙組）。
    -   主介面提供下拉選單，可在程式執行期間隨時切換型號，介面會自動重置以適應新模式。

-   **多國語言**：
    -   內建中文與英文介面，可透過下拉選單即時切換。

-   **即時監控**：
    -   **視覺化儀表**：使用 `ttkbootstrap` 的半圓形儀表 (Meter) 動態顯示輸出電流 (mA) 和輸入信號 (%)，比純文字更直觀。
    -   **狀態顯示**：清楚標示控制器目前的運作狀態（如：正常、線圈開路、線圈短路等）。

-   **參數設定與寫入**：
    -   **優化佈局**：參數設定區採兩欄式佈局，提高空間利用率。
    -   **分頁管理 (雙組模式)**：將雙組控制器的複雜參數分為「通用參數」、「A組輸出」、「B組輸出」、「PID參數」四個標籤頁，介面更清晰。
    -   **智慧批次寫入**：
        -   移除單獨的寫入按鈕，統一使用「套用至控制器」按鈕進行批次寫入，並提供進度條。
        -   **參數驗證**：在寫入前會檢查參數是否在規定範圍內，並針對部分參數邏輯如最大電流是否大於最小電流做出判斷，避免錯誤設定。
        -   **安全恢復出廠設置**：執行恢復出廠設置時，會彈出確認對話框，並在執行後顯示 10 秒倒數計時，防止誤操作並給予控制器反應時間。

-   **圖表化分析**：
    -   **靜態特性曲線 (主畫面)**：
        -   根據當前參數，在主介面下方即時繪製控制器的輸出特性曲線。
        -   圖表會根據雙組控制器的三種不同工作模式自動切換樣式：
            1.  **單組輸出 (Single Output)**
            2.  **雙組信號-雙組輸出 (Dual Output Dual Slope)**
            3.  **單組信號-雙組輸出 (Dual Output Single Slope)**
        -   圖表的 X 軸會根據信號類型（電壓/電流/百分比）動態更新其單位與刻度。
    -   **即時數據圖表 (彈出視窗)**：
        -   提供「即時圖表」按鈕，可開啟一個獨立視窗。
        -   使用 `Matplotlib` 繪製即時的「輸出電流 vs. 時間」和「輸入信號 vs. 時間」關係圖。
        -   支援將圖表記錄的數據匯出為 `.csv` 檔案，方便後續分析。

-   **參數方案管理**：
    -   可將當前所有參數儲存為本地 `.json` 檔案。
    -   讀取設定檔時，程式會根據當前的「控制器模式」和「語言」自動篩選對應的資料夾，避免誤用不相容的設定檔。

## ⚙️ 如何使用

### 1. 安裝依賴套件

請確保您已安裝 Python，並透過 pip 安裝以下必要的函式庫：

```bash
pip install ttkbootstrap modbus-tk pyserial matplotlib
```

### 2. 執行程式

直接執行主程式檔案：

```bash
python dual_controller_app.py
```

### 3. 操作流程

1.  **選擇型號**：在程式啟動時的對話框中選擇 `SY-DPCA-*-1` (單組) 或 `SY-DPCA-*-2` (雙組)。
2.  **連接控制器**：
    -   在「Modbus通訊參數設置」區域選擇正確的通訊端口 (COM Port)、鮑率 (Baud Rate) 和設備位址 (Address)。
    -   點擊「連接」按鈕。
3.  **參數調整與寫入**：
    -   連接成功後，程式會自動開始輪詢讀取控制器狀態。
    -   在「可寫入參數」區域修改您需要的數值。
    -   點擊「套用至控制器」按鈕，將所有修改後的參數一次性寫入控制器。
4.  **圖表分析**：
    -   觀察主視窗下方的靜態特性曲線，確認參數設定是否符合預期。
    -   點擊「即時圖表」按鈕，開啟新視窗觀察電流與信號的即時變化。
5.  **儲存與讀取**：
    -   使用「本地儲存」將調校好的參數保存起來。
    -   使用「本地讀取」載入之前保存的參數方案。

## 📦 如何打包成執行檔

如果您想將此程式打包成一個獨立的 `.exe` 執行檔，可以依賴 `PyInstaller`。

### 1. 安裝 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包步驟

由於程式依賴了外部的圖示 (`.ico`) 和 `ttkbootstrap` 的主題檔案 (`.tcl`)，直接打包會導致這些資源遺失。建議使用 `.spec` 檔案來進行更精確的打包。

**步驟一：生成 `.spec` 檔案**

首先，執行一次基本的打包命令，這會生成一個 `dual_controller_app.spec` 檔案：

```bash
pyinstaller --noconsole --name "SunstarController" dual_controller_app.py
```
* `--noconsole`: 執行時不顯示黑色命令提示字元視窗。
* `--name`: 指定輸出的執行檔名稱。

**步驟二：修改 `.spec` 檔案**

用文字編輯器打開生成的 `dual_controller_app.spec` 檔案，找到 `Analysis` 和 `EXE` 這兩個區塊，並進行以下修改：

- **`datas`**: 告訴 PyInstaller 將哪些外部檔案或資料夾包含進來。
- **`icon`**: 指定執行檔的圖示。

```python
# dual_controller_app.spec

# ... (前面的內容保持不變)

a = Analysis(
    ['dual_controller_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon/002.ico', 'icon'),
        ('forest-light.tcl', '.'),
        ('forest-light', 'forest-light')
    ],  # <--- 在這裡加入 datas
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SunstarController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # <--- 確保為 False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/002.ico', # <--- 在這裡指定圖示
)

# ... (後面的內容保持不變)
```

**步驟三：使用 `.spec` 檔案進行打包**

最後，讓 PyInstaller 使用你修改過的 `.spec` 檔案來執行打包：

```bash
pyinstaller dual_controller_app.spec --clean -y
```
* `--clean`: 打包前清理舊的暫存檔。
* `-y`: 如果輸出目錄已存在，直接覆蓋。

打包完成後，您可以在 `dist` 資料夾中找到 `SunstarController.exe` 以及所有相關的資源檔案。