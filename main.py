"""桌面小轉盤（網頁介面版）：用系統內建的 WebView 顯示 index.html。

    pip install pywebview
    python main.py
"""
import sys
from pathlib import Path

import webview


def resource(name: str) -> str:
    # 一般執行時在 main.py 旁；PyInstaller 打包後在 sys._MEIPASS
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return str(base / name)


if __name__ == "__main__":
    webview.create_window(
        "小轉盤",
        resource("index.html"),
        width=1100,
        height=700,
        min_size=(600, 620),  # 低於 760 寬會改成上下排列；此尺寸以上下排列時為準，面板內容超出會自動捲動
        resizable=True,
    )
    # Windows：指定 WebView2（Chromium）。若缺少 Runtime 會直接報錯，避免退回老舊引擎造成嚴重卡頓
    webview.start(gui="edgechromium" if sys.platform == "win32" else None)  # 除錯可加 debug=True
