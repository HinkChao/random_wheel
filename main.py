"""桌面小轉盤（網頁介面版）：用系統內建的 WebView 顯示 index.html。

    pip install pywebview
    python main.py
"""
import json
import os
import sys
from pathlib import Path

import webview

TITLE = "randomwheel"


def resource(name: str) -> str:
    # 一般執行時在 main.py 旁；PyInstaller 打包後在 sys._MEIPASS
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return str(base / name)


def _state_file() -> Path:
    """存檔位置：macOS ~/Library/Application Support/randomwheel/、Windows %APPDATA%\\小轉盤\\（打包後也不會寫進程式資料夾）。"""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / TITLE / "state.json"


def _apply_mac(mode: str) -> None:
    """macOS：auto 跟隨系統；light / dark 強制整個 app 的外觀（標題列、捲軸、系統選色視窗都會跟著變）。"""
    from AppKit import NSApplication, NSAppearance
    from PyObjCTools import AppHelper

    def run():  # 介面操作必須在主執行緒
        if mode == "auto":
            appearance = None
        else:
            appearance = NSAppearance.appearanceNamed_(
                "NSAppearanceNameDarkAqua" if mode == "dark" else "NSAppearanceNameAqua")
        NSApplication.sharedApplication().setAppearance_(appearance)

    AppHelper.callAfter(run)


def _apply_win(dark: bool) -> None:
    """Windows：用 DWM 切換標題列深色模式（Windows 10 1809 以上；Windows 11 皆支援）。"""
    import ctypes
    from ctypes import wintypes

    user32, dwm = ctypes.windll.user32, ctypes.windll.dwmapi
    user32.FindWindowW.restype = wintypes.HWND
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, wintypes.UINT]
    dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]

    hwnd = user32.FindWindowW(None, TITLE)
    if not hwnd:
        return
    value = ctypes.c_int(1 if dark else 0)
    for attr in (20, 19):  # 20：Windows 10 2004+ / 11；19：較早的 Windows 10
        if dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
            break
    # 強制標題列重畫（NOMOVE | NOSIZE | NOZORDER | FRAMECHANGED）
    user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004 | 0x0020)


class Api:
    """提供給網頁呼叫：window.pywebview.api.set_theme / load_state / save_state"""

    def set_theme(self, mode, dark):
        # mode：auto / light / dark（使用者選的）；dark：目前實際是否為深色
        try:
            if sys.platform == "darwin":
                _apply_mac(str(mode))
            elif sys.platform == "win32":
                _apply_win(bool(dark))
        except Exception as e:  # 標題列變色失敗不該影響轉盤本身
            print("set_theme failed:", e)

    def load_state(self):
        """讀取存檔；沒有存檔或檔案壞掉時回傳 None（網頁端會改用預設值）。"""
        try:
            return json.loads(_state_file().read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except Exception as e:
            print("load_state failed:", e)
            return None

    def save_state(self, state):
        """寫入存檔：先寫暫存檔再替換，避免程式中途關閉造成檔案損毀。"""
        try:
            text = json.dumps(state, ensure_ascii=False, indent=2)
            if len(text) > 2_000_000:  # 防呆：異常龐大的資料不寫入
                return False
            path = _state_file()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(path)
            return True
        except Exception as e:
            print("save_state failed:", e)
            return False


if __name__ == "__main__":
    webview.create_window(
        TITLE,
        resource("index.html"),
        js_api=Api(),
        width=1100,
        height=700,
        min_size=(600, 620),  # 低於 760 寬會改成上下排列；此尺寸以上下排列時為準，面板內容超出會自動捲動
        resizable=True,
    )
    # Windows：指定 WebView2（Chromium）。若缺少 Runtime 會直接報錯，避免退回老舊引擎造成嚴重卡頓
    webview.start(gui="edgechromium" if sys.platform == "win32" else None)  # 除錯可加 debug=True