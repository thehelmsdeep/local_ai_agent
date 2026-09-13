import ctypes
import re
import subprocess
import time

import pyautogui
import pyperclip


def _focus_calculator() -> bool:
    """Bring the native Windows Calculator window to the foreground."""
    user32 = ctypes.windll.user32
    target = "calculator"
    found = False

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def callback(hwnd, _):
        nonlocal found
        if not user32.IsWindowVisible(hwnd):
            return True

        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip().lower()

        if target in title:
            user32.ShowWindow(hwnd, 5)
            user32.SetForegroundWindow(hwnd)
            found = True
            return False

        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return found


def open_calculator() -> str:
    """Open the native Windows Calculator application and focus it."""
    subprocess.Popen(["calc.exe"])

    # Give Windows Calculator time to start, then explicitly focus its window.
    for _ in range(20):
        time.sleep(0.2)
        if _focus_calculator():
            return "Windows Calculator opened and focused."

    return "Windows Calculator opened, but its window could not be focused."


def calculator(expression: str) -> str:
    """Open Calculator, focus it, paste an arithmetic expression, and press Enter."""
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        raise ValueError("Calculator expression contains unsupported characters")

    open_calculator()
    time.sleep(0.3)

    if not _focus_calculator():
        raise RuntimeError("Could not focus Windows Calculator")

    # Clipboard paste is more reliable than pyautogui.write for symbols such as *.
    pyperclip.copy(expression)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)
    pyautogui.press("enter")
    return f"Sent to Windows Calculator: {expression}"


TOOLS = {
    "open_calculator": open_calculator,
    "calculator": calculator,
}
