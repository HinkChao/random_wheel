# 小轉盤 Random Wheel

一個跨平台（macOS / Windows）的桌面小轉盤：輸入選項、按下開始，讓轉盤幫你決定。
介面是一個純 HTML / CSS / JavaScript 檔案，用 [pywebview](https://pywebview.flowrl.com/) 包成原生視窗，所以它是真正的桌面程式，不需要瀏覽器，也不會連網。

> **English summary** — A small desktop spin-the-wheel app for macOS and Windows. The UI is a single `index.html` shown in a native window via pywebview. It supports fair and weighted (custom-odds) modes, light/dark themes with matching title bar, color palettes (including a custom one), sound effects with volume/mute, Chinese/English UI, and auto-saved settings. Quick start: `pip install pywebview` then `python main.py`.

---

## 功能

**轉盤**
- 新增、編輯、刪除選項；輸入框按 Enter 新增，也可以一次貼上多行。
- 每個選項前有勾選框，取消勾選就不會出現在轉盤上（選項本身還在）。
- 點轉盤或按「開始」轉動，約 4 秒，先快後慢。結果是先決定好再轉到對應位置，指針停的位置一定和結果一致。
- 轉盤與視窗大小連動，視窗很窄時改成上下排列。

**兩種模式（可隨時切換，互不影響）**
- **公平**：每個選項機率相同。
- **自訂機率**：每個選項有 1～100 的權重，旁邊即時顯示機率，扇形寬度也依機率變寬或變窄。「重設權重」可一鍵恢復成相同。切回公平模式時權重會保留。

**轉盤選項**
- **轉到後從轉盤移除**：轉到的選項只會被取消勾選，不會被刪除；「全部恢復」可一鍵放回去。
- **跳過動畫**：直接得到結果。

**設定（左上角齒輪）**
- **畫面**：跟隨系統／日間／夜間。視窗標題列也會跟著變色（見下方「運作方式」）。
- **轉盤配色**：5 組預設（繽紛、粉彩、海洋、日落、森林）＋「自訂」。自訂可用 2～10 個顏色，用方格色票或 6 位色碼挑選，皆為不透明色。
- **轉動音效**：指針每跨過一條分隔線會有「滴答」聲，停下時有提示音；可靜音、調整音量。聲音由程式合成，不需要音檔。
- **語言**：齒輪下方的小膠囊可切換 中文／EN。

**自動存檔**
選項（含勾選與權重）、模式、配色與自訂顏色、日夜設定、語言、音量與靜音、兩個勾選框都會自動記住，改完約 0.3 秒後寫入。

---

## 快速開始

需要 Python 3 與 [pywebview](https://pywebview.flowrl.com/)：

```bash
pip install pywebview
python main.py
```

| 平台 | 額外需求 |
| --- | --- |
| macOS | 使用系統內建的 WKWebView，不需另外安裝瀏覽器元件。 |
| Windows（x86-64） | 需要 **WebView2 Runtime**。Windows 11 通常已內建；舊版 Windows 10 請先安裝 Microsoft 的 Evergreen 版。程式會強制使用 WebView2，缺少時會直接報錯，而不是默默退回舊的 IE 引擎。 |

除錯時，把 `main.py` 最後一行改成 `webview.start(..., debug=True)` 可開啟開發者工具。

---

## 專案結構

```
.
├── main.py            # 啟動 pywebview 視窗，並提供網頁呼叫的 Python 功能
├── index.html         # 整個介面（HTML + CSS + JS，無外部相依）
├── icon.ico           # Windows 打包用的圖示
├── requirements.txt   # pywebview、pyinstaller
├── build_windows.bat  # 一鍵打包成 Windows 程式
└── README.md
```

## 運作方式

- **介面**：`index.html` 自成一體，不載入任何外部資源。轉盤用 Canvas 繪製；轉動時只讓轉盤那一層用 CSS／Web Animations 旋轉，由 GPU 合成，所以不會因為 JavaScript 忙碌而掉幀。音效使用瀏覽器內建的 Web Audio 合成。
- **Python 端**（`main.py`）透過 pywebview 的 `js_api` 提供三個功能給網頁呼叫：
  - `set_theme(mode, dark)`：讓視窗標題列跟著日夜變色。macOS 設定整個 app 的外觀（`auto` 時恢復跟隨系統）；Windows 用 DWM 切換標題列深色模式（Windows 10 1809 以上）。
  - `load_state()` / `save_state(state)`：讀寫存檔。寫入時先寫暫存檔再替換，避免中途關閉造成檔案損毀。
- **視窗**：預設 1100×700，最小 600×620。

## 存檔位置

存檔是一個 JSON 檔，放在使用者資料夾，所以打包後或更新程式都不會消失：

| 平台 | 路徑 |
| --- | --- |
| macOS | `~/Library/Application Support/<TITLE>/state.json` |
| Windows | `%APPDATA%\<TITLE>\state.json` |

`<TITLE>` 是 `main.py` 開頭的 `TITLE` 常數，同時也是視窗標題（目前為 `randomwheel`）。要回到預設值，刪掉這個檔案即可。壞掉或欄位不對的存檔會被忽略，改用預設值。

> 修改 `TITLE` 會同時改變視窗標題與存檔資料夾，原本的存檔不會自動搬過去。Windows 的標題列變色功能是靠 `TITLE` 找到視窗的，所以兩者要保持一致。

---

## 打包成 Windows 程式

需要在 **Windows** 上打包（PyInstaller 不能跨平台編譯），並使用 **64 位元** Python。

1. 確認 `main.py`、`index.html`、`icon.ico`、`requirements.txt`、`build_windows.bat` 在同一個資料夾。
2. 雙擊 `build_windows.bat`。它會建立虛擬環境 `.venv-build`、安裝相依套件並執行 PyInstaller。
3. 完成後：
   - 程式：`dist\SpinWheel\SpinWheel.exe`
   - 方便分享的壓縮檔：`dist\SpinWheel-win64.zip`

注意事項：
- 採用資料夾模式（非單一檔案），啟動較快，也比較不容易被防毒軟體誤判。分享時請給**整個資料夾或 zip**，不能只給 exe。
- 沒有簽名，第一次執行時 Windows SmartScreen 會警告，點「其他資訊」→「仍要執行」。
- 對方電腦需要 WebView2 Runtime（見上方）。
- 打包後沒有主控台，錯誤看不到。打不開時，先把腳本裡的 `--windowed` 拿掉再用命令列執行，就能看到錯誤訊息；若錯誤與 `clr` 有關，可在指令加上 `--hidden-import clr`。

## 打包 macOS 版

目前沒有提供 macOS 的打包腳本，也尚未在 macOS 上實測打包。可以從這個起點開始（用 PyInstaller）：

```bash
pip install pywebview pyinstaller
pyinstaller --noconfirm --windowed --name RandomWheel --add-data "index.html:." main.py
```

- Intel 與 Apple Silicon 是不同架構；要同時支援，需使用 universal2 版的 Python 打包。
- 沒有簽名與公證的 app，在別人的 Mac 上無法直接開啟。macOS Sequoia（15）以後，先雙擊讓它被擋下，再到「系統設定 → 隱私權與安全性」按「仍要打開」。想省掉這個步驟，需要付費加入 Apple Developer Program 並做簽名與公證。

---

## 疑難排解

| 狀況 | 可能原因與做法 |
| --- | --- |
| Windows 啟動就報錯，提到 WebView2 | 沒有安裝 WebView2 Runtime，請安裝 Evergreen 版。 |
| 用瀏覽器直接開 `index.html`，設定沒有被記住 | 存檔由 Python 端負責，只有用 `main.py` 開啟的視窗才會存檔。 |
| 視窗標題列沒有跟著日夜變色 | 同上，且 Windows 需要 10 1809 以上。也請確認 `TITLE` 與實際視窗標題一致。 |
| 沒有聲音 | 檢查設定裡是否靜音或音量為 0。瀏覽器規定要在使用者操作之後才能發聲，按下開始後就會啟用。 |
| 想重設所有設定 | 刪除上方「存檔位置」的 `state.json`。 |

## 已知限制

- 轉盤上的文字固定為白色，選到很淺的顏色（例如白色）時字會看不清楚。
- 選項很多或權重很小時，扇形上的文字會縮小甚至被截短；完整名稱請看右側清單。
- 只提供網頁介面的繁體中文與英文兩種語言；選項內容不會被翻譯。

## 可能的下一步

- 網頁版（部署到 GitHub Pages）：加入 localStorage 存檔備援，並做成可安裝的 PWA。
- macOS 打包腳本；用 GitHub Actions 在雲端同時打包 Windows 與 macOS 版。
- Windows 安裝檔（例如用 Inno Setup）。

## 授權

尚未指定。公開發佈前請先選擇授權（例如 MIT），並在此補上。
